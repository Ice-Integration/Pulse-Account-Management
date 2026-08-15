import Fastify from 'fastify';
import cors from '@fastify/cors';
import bcrypt from 'bcryptjs';
import { SignJWT } from 'jose';
import pg from 'pg';
import { createHash, randomBytes, randomInt, randomUUID } from 'node:crypto';
import { z } from 'zod';

const app = Fastify({ logger: true });
await app.register(cors, { origin: true });

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const secret = new TextEncoder().encode(process.env.JWT_SECRET ?? 'dev-secret-change-me');

const credentials = z.object({ email: z.string().email(), password: z.string().min(8) });
const refreshInput = z.object({ refreshToken: z.string().min(32) });
const resetRequest = z.object({ email: z.string().email() });
const resetConfirm = z.object({ token: z.string().min(32), password: z.string().min(8) });
const mfaVerify = z.object({ challengeId: z.string().uuid(), code: z.string().length(6) });

const hash = (value: string) => createHash('sha256').update(value).digest('hex');

async function tokenFor(user: { id: string; email: string; role: string }) {
  return new SignJWT({ email: user.email, role: user.role })
    .setProtectedHeader({ alg: 'HS256' })
    .setSubject(user.id)
    .setIssuedAt()
    .setExpirationTime('15m')
    .sign(secret);
}

async function issueSession(user: { id: string; email: string; role: string }) {
  const raw = randomBytes(48).toString('base64url');
  await pool.query(
    `INSERT INTO refresh_tokens (id,user_id,token_hash,expires_at)
     VALUES ($1,$2,$3,now() + interval '30 days')`,
    [randomUUID(), user.id, hash(raw)],
  );
  return { accessToken: await tokenFor(user), refreshToken: raw };
}

app.get('/health', async () => ({ status: 'ok' }));

app.post('/auth/register', async (request, reply) => {
  const input = credentials.parse(request.body);
  const passwordHash = await bcrypt.hash(input.password, 12);
  const id = randomUUID();
  try {
    const result = await pool.query(
      'INSERT INTO users (id,email,password_hash,role) VALUES ($1,$2,$3,$4) RETURNING id,email,role',
      [id, input.email.toLowerCase(), passwordHash, 'customer'],
    );
    const user = result.rows[0];
    return reply.code(201).send({ user, ...(await issueSession(user)) });
  } catch (error: any) {
    if (error?.code === '23505') return reply.code(409).send({ error: 'email_already_registered' });
    throw error;
  }
});

app.post('/auth/login', async (request, reply) => {
  const input = credentials.parse(request.body);
  const result = await pool.query(
    'SELECT id,email,password_hash,role,mfa_enabled FROM users WHERE email=$1',
    [input.email.toLowerCase()],
  );
  const user = result.rows[0];
  if (!user || !(await bcrypt.compare(input.password, user.password_hash))) {
    return reply.code(401).send({ error: 'invalid_credentials' });
  }

  if (user.mfa_enabled) {
    const code = randomInt(100000, 1000000).toString();
    const challengeId = randomUUID();
    await pool.query(
      `INSERT INTO mfa_challenges (id,user_id,code_hash,expires_at)
       VALUES ($1,$2,$3,now() + interval '10 minutes')`,
      [challengeId, user.id, hash(code)],
    );
    await pool.query(
      `INSERT INTO notifications (id,user_id,channel,template,payload)
       VALUES ($1,$2,'email','mfa_code',$3::jsonb)`,
      [randomUUID(), user.id, JSON.stringify({ code })],
    );
    return reply.code(202).send({ mfaRequired: true, challengeId });
  }

  const safeUser = { id: user.id, email: user.email, role: user.role };
  return { user: safeUser, ...(await issueSession(safeUser)) };
});

app.post('/auth/mfa/verify', async (request, reply) => {
  const input = mfaVerify.parse(request.body);
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const result = await client.query(
      `SELECT c.id,c.user_id,c.code_hash,u.email,u.role
       FROM mfa_challenges c JOIN users u ON u.id=c.user_id
       WHERE c.id=$1 AND c.verified_at IS NULL AND c.expires_at > now()
       FOR UPDATE`,
      [input.challengeId],
    );
    const row = result.rows[0];
    if (!row || row.code_hash !== hash(input.code)) {
      await client.query('ROLLBACK');
      return reply.code(401).send({ error: 'invalid_or_expired_mfa_code' });
    }
    await client.query('UPDATE mfa_challenges SET verified_at=now() WHERE id=$1', [input.challengeId]);
    await client.query('COMMIT');
    const user = { id: row.user_id, email: row.email, role: row.role };
    return { user, ...(await issueSession(user)) };
  } finally {
    client.release();
  }
});

app.post('/auth/refresh', async (request, reply) => {
  const input = refreshInput.parse(request.body);
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const result = await client.query(
      `SELECT r.id,r.user_id,u.email,u.role
       FROM refresh_tokens r JOIN users u ON u.id=r.user_id
       WHERE r.token_hash=$1 AND r.revoked_at IS NULL AND r.expires_at > now()
       FOR UPDATE`,
      [hash(input.refreshToken)],
    );
    const row = result.rows[0];
    if (!row) {
      await client.query('ROLLBACK');
      return reply.code(401).send({ error: 'invalid_refresh_token' });
    }
    await client.query('UPDATE refresh_tokens SET revoked_at=now() WHERE id=$1', [row.id]);
    await client.query('COMMIT');
    const user = { id: row.user_id, email: row.email, role: row.role };
    return { user, ...(await issueSession(user)) };
  } finally {
    client.release();
  }
});

app.post('/auth/logout', async (request, reply) => {
  const input = refreshInput.parse(request.body);
  await pool.query('UPDATE refresh_tokens SET revoked_at=now() WHERE token_hash=$1 AND revoked_at IS NULL', [
    hash(input.refreshToken),
  ]);
  return reply.code(204).send();
});

app.post('/auth/password-reset/request', async (request, reply) => {
  const input = resetRequest.parse(request.body);
  const result = await pool.query('SELECT id FROM users WHERE email=$1', [input.email.toLowerCase()]);
  const user = result.rows[0];
  if (user) {
    const raw = randomBytes(48).toString('base64url');
    await pool.query(
      `INSERT INTO password_reset_tokens (id,user_id,token_hash,expires_at)
       VALUES ($1,$2,$3,now() + interval '30 minutes')`,
      [randomUUID(), user.id, hash(raw)],
    );
    await pool.query(
      `INSERT INTO notifications (id,user_id,channel,template,payload)
       VALUES ($1,$2,'email','password_reset',$3::jsonb)`,
      [randomUUID(), user.id, JSON.stringify({ token: raw })],
    );
  }
  return reply.code(202).send({ accepted: true });
});

app.post('/auth/password-reset/confirm', async (request, reply) => {
  const input = resetConfirm.parse(request.body);
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const result = await client.query(
      `SELECT id,user_id FROM password_reset_tokens
       WHERE token_hash=$1 AND used_at IS NULL AND expires_at > now() FOR UPDATE`,
      [hash(input.token)],
    );
    const row = result.rows[0];
    if (!row) {
      await client.query('ROLLBACK');
      return reply.code(400).send({ error: 'invalid_or_expired_reset_token' });
    }
    const passwordHash = await bcrypt.hash(input.password, 12);
    await client.query('UPDATE users SET password_hash=$1 WHERE id=$2', [passwordHash, row.user_id]);
    await client.query('UPDATE password_reset_tokens SET used_at=now() WHERE id=$1', [row.id]);
    await client.query('UPDATE refresh_tokens SET revoked_at=now() WHERE user_id=$1 AND revoked_at IS NULL', [row.user_id]);
    await client.query('COMMIT');
    return { changed: true };
  } finally {
    client.release();
  }
});

app.listen({ port: Number(process.env.PORT ?? 4001), host: '0.0.0.0' });
