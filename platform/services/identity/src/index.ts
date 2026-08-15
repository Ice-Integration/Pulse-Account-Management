import Fastify from 'fastify';
import cors from '@fastify/cors';
import bcrypt from 'bcryptjs';
import { SignJWT } from 'jose';
import pg from 'pg';
import { randomUUID } from 'node:crypto';
import { z } from 'zod';

const app = Fastify({ logger: true });
await app.register(cors, { origin: true });

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const secret = new TextEncoder().encode(process.env.JWT_SECRET ?? 'dev-secret-change-me');

const credentials = z.object({ email: z.string().email(), password: z.string().min(8) });

async function tokenFor(user: { id: string; email: string; role: string }) {
  return new SignJWT({ email: user.email, role: user.role })
    .setProtectedHeader({ alg: 'HS256' })
    .setSubject(user.id)
    .setIssuedAt()
    .setExpirationTime('1h')
    .sign(secret);
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
    return reply.code(201).send({ user, accessToken: await tokenFor(user) });
  } catch (error: any) {
    if (error?.code === '23505') return reply.code(409).send({ error: 'email_already_registered' });
    throw error;
  }
});

app.post('/auth/login', async (request, reply) => {
  const input = credentials.parse(request.body);
  const result = await pool.query('SELECT id,email,password_hash,role FROM users WHERE email=$1', [
    input.email.toLowerCase(),
  ]);
  const user = result.rows[0];
  if (!user || !(await bcrypt.compare(input.password, user.password_hash))) {
    return reply.code(401).send({ error: 'invalid_credentials' });
  }
  return { user: { id: user.id, email: user.email, role: user.role }, accessToken: await tokenFor(user) };
});

app.listen({ port: Number(process.env.PORT ?? 4001), host: '0.0.0.0' });
