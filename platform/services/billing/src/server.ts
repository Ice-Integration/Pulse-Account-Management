import Fastify from 'fastify';
import pg from 'pg';
import { randomUUID } from 'node:crypto';
import { z } from 'zod';

const app = Fastify({ logger: true });
const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL ?? 'postgres://pulse:pulse@localhost:5432/pulse' });
const serviceKey = process.env.SERVICE_KEY ?? 'dev-service-key-change-me';

app.addHook('onRequest', async (request, reply) => {
  if (request.url === '/health') return;
  if (request.headers['x-service-key'] !== serviceKey) {
    return reply.code(401).send({ error: 'invalid_service_key' });
  }
});

app.get('/health', async () => ({ status: 'ok', service: 'billing' }));

app.get('/accounts/:accountId/invoices', async (req) => {
  const { accountId } = req.params as { accountId: string };
  const { rows } = await pool.query('SELECT * FROM invoices WHERE account_id=$1 ORDER BY created_at DESC', [accountId]);
  return rows;
});

app.get('/invoices/:invoiceId/account', async (req, reply) => {
  const { invoiceId } = req.params as { invoiceId: string };
  const { rows } = await pool.query('SELECT account_id FROM invoices WHERE id=$1', [invoiceId]);
  if (!rows.length) return reply.code(404).send({ error: 'invoice_not_found' });
  return rows[0];
});

app.post('/invoices/:invoiceId/pay', async (req, reply) => {
  const body = z.object({ amount: z.number().positive(), provider: z.string().default('sandbox') }).parse(req.body);
  const { invoiceId } = req.params as { invoiceId: string };
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const invoice = await client.query('SELECT * FROM invoices WHERE id=$1 FOR UPDATE', [invoiceId]);
    if (!invoice.rowCount) return reply.code(404).send({ error: 'invoice_not_found' });
    if (invoice.rows[0].status === 'paid') return reply.code(409).send({ error: 'invoice_already_paid' });
    if (Number(invoice.rows[0].total) !== body.amount) return reply.code(400).send({ error: 'amount_mismatch' });
    const paymentId = randomUUID();
    await client.query('INSERT INTO payments(id,invoice_id,provider,provider_reference,amount,status) VALUES($1,$2,$3,$4,$5,$6)', [paymentId, invoiceId, body.provider, `sandbox_${paymentId}`, body.amount, 'succeeded']);
    await client.query("UPDATE invoices SET status='paid', paid_at=now() WHERE id=$1", [invoiceId]);
    await client.query('COMMIT');
    return { paymentId, invoiceId, status: 'succeeded' };
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally { client.release(); }
});

app.post('/accounts/:accountId/plan-changes', async (req, reply) => {
  const body = z.object({ toPlanId: z.string().uuid(), requestedBy: z.string().uuid().optional() }).parse(req.body);
  const { accountId } = req.params as { accountId: string };
  const current = await pool.query('SELECT plan_id FROM account_plans WHERE account_id=$1 AND active=true ORDER BY effective_at DESC LIMIT 1', [accountId]);
  const target = await pool.query('SELECT id, monthly_price FROM plans WHERE id=$1 AND active=true', [body.toPlanId]);
  if (!target.rowCount) return reply.code(404).send({ error: 'target_plan_not_found' });
  const id = randomUUID();
  const effectiveAt = new Date(Date.now() + 24 * 60 * 60 * 1000);
  await pool.query('INSERT INTO plan_change_requests(id,account_id,from_plan_id,to_plan_id,requested_by,status,effective_at) VALUES($1,$2,$3,$4,$5,$6,$7)', [id, accountId, current.rows[0]?.plan_id ?? null, body.toPlanId, body.requestedBy ?? null, 'scheduled', effectiveAt]);
  return reply.code(202).send({ id, status: 'scheduled', effectiveAt });
});

const port = Number(process.env.PORT ?? 4003);
app.listen({ port, host: '0.0.0.0' });
