import { createSchema, createYoga } from 'graphql-yoga';
import { createServer } from 'node:http';
import { jwtVerify } from 'jose';

const accountUrl = process.env.ACCOUNT_URL ?? 'http://localhost:8081';
const billingUrl = process.env.BILLING_URL ?? 'http://localhost:4003';
const aiUrl = process.env.AI_URL ?? 'http://localhost:8002';
const serviceKey = requireEnvironmentVariable('SERVICE_KEY');
const jwtSecret = new TextEncoder().encode(process.env.JWT_SECRET ?? 'dev-secret-change-me');

function requireEnvironmentVariable(name: string) {
  const value = process.env[name];
  if (!value?.trim()) throw new Error(`${name} must be set`);
  return value;
}

type Viewer = { sub: string; role?: string; email?: string };
type Context = { viewer: Viewer };

function privileged(viewer: Viewer) {
  return ['support_agent', 'supervisor', 'admin'].includes(viewer.role ?? '');
}

async function authorizeAccount(accountId: string, viewer: Viewer) {
  if (privileged(viewer)) return;
  const owner = await internalJson(`${accountUrl}/accounts/${accountId}/owner`);
  if (String(owner.user_id) !== viewer.sub) throw new Error('forbidden_account');
}

async function authorizeInvoice(invoiceId: string, viewer: Viewer) {
  if (privileged(viewer)) return;
  const result = await internalJson(`${billingUrl}/invoices/${invoiceId}/account`);
  await authorizeAccount(String(result.account_id), viewer);
}

const schema = createSchema<Context>({
  typeDefs: /* GraphQL */ `
    type Device { id: ID!, line_number: String!, device_identifier: String!, model: String!, financed: Boolean!, payoff_amount: Float, eligible: Boolean }
    type Plan { id: ID!, code: String!, name: String!, monthly_price: Float!, description: String }
    type Order { id: ID!, type: String!, status: String!, total: Float!, created_at: String }
    type Account { id: ID!, account_number: String!, full_name: String!, phone: String, billing_address: String, status: String!, devices: [Device!]!, plans: [Plan!]! }
    type Invoice { id: ID!, total: Float!, status: String!, due_at: String }
    type Citation { id: ID!, title: String!, score: Float! }
    type SupportAnswer { answer: String!, citations: [Citation!]! }
    type PaymentResult { paymentId: ID!, invoiceId: ID!, status: String! }
    type PlanChange { id: ID!, status: String!, effectiveAt: String! }
    type Query {
      account(id: ID!): Account!
      plans: [Plan!]!
      orders(accountId: ID!): [Order!]!
      upgradeEligibility(accountId: ID!): [Device!]!
      invoices(accountId: ID!): [Invoice!]!
      supportAsk(question: String!, accountId: ID): SupportAnswer!
    }
    type Mutation {
      updateAccount(id: ID!, phone: String, billingAddress: String): Account!
      payInvoice(invoiceId: ID!, amount: Float!): PaymentResult!
      requestPlanChange(accountId: ID!, toPlanId: ID!): PlanChange!
    }
  `,
  resolvers: {
    Query: {
      account: async (_p, { id }, ctx) => { await authorizeAccount(id, ctx.viewer); return internalJson(`${accountUrl}/accounts/${id}`); },
      plans: async () => internalJson(`${accountUrl}/accounts/plans/catalog`),
      orders: async (_p, { accountId }, ctx) => { await authorizeAccount(accountId, ctx.viewer); return internalJson(`${accountUrl}/accounts/${accountId}/orders`); },
      upgradeEligibility: async (_p, { accountId }, ctx) => { await authorizeAccount(accountId, ctx.viewer); return internalJson(`${accountUrl}/accounts/${accountId}/upgrade-eligibility`); },
      invoices: async (_p, { accountId }, ctx) => { await authorizeAccount(accountId, ctx.viewer); return internalJson(`${billingUrl}/accounts/${accountId}/invoices`); },
      supportAsk: async (_p, { question, accountId }, ctx) => {
        if (accountId) await authorizeAccount(accountId, ctx.viewer);
        return json(`${aiUrl}/support/ask`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ question, account_id: accountId }) });
      },
    },
    Mutation: {
      updateAccount: async (_p, { id, phone, billingAddress }, ctx) => {
        await authorizeAccount(id, ctx.viewer);
        return internalJson(`${accountUrl}/accounts/${id}`, { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ phone, billingAddress }) });
      },
      payInvoice: async (_p, { invoiceId, amount }, ctx) => {
        await authorizeInvoice(invoiceId, ctx.viewer);
        return internalJson(`${billingUrl}/invoices/${invoiceId}/pay`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ amount, provider: 'sandbox' }) });
      },
      requestPlanChange: async (_p, { accountId, toPlanId }, ctx) => {
        await authorizeAccount(accountId, ctx.viewer);
        return internalJson(`${billingUrl}/accounts/${accountId}/plan-changes`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ toPlanId, requestedBy: ctx.viewer.sub }) });
      },
    },
  },
});

async function json(url: string, init?: RequestInit) {
  const response = await fetch(url, init);
  if (!response.ok) throw new Error(`upstream_${response.status}`);
  return response.json();
}

async function internalJson(url: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  headers.set('x-service-key', serviceKey);
  return json(url, { ...init, headers });
}

const yoga = createYoga<Context>({
  schema,
  graphqlEndpoint: '/graphql',
  context: async ({ request }) => {
    const auth = request.headers.get('authorization');
    if (!auth?.startsWith('Bearer ')) throw new Error('unauthorized');
    const { payload } = await jwtVerify(auth.slice(7), jwtSecret);
    return { viewer: { sub: String(payload.sub), role: payload.role as string | undefined, email: payload.email as string | undefined } };
  },
});

createServer(yoga).listen(Number(process.env.PORT ?? 4000), '0.0.0.0');
