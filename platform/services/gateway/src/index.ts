import { createSchema, createYoga } from 'graphql-yoga';
import { createServer } from 'node:http';
import { jwtVerify } from 'jose';

const accountUrl = process.env.ACCOUNT_URL ?? 'http://localhost:8081';
const billingUrl = process.env.BILLING_URL ?? 'http://localhost:4003';
const aiUrl = process.env.AI_URL ?? 'http://localhost:8002';
const jwtSecret = new TextEncoder().encode(process.env.JWT_SECRET ?? 'dev-secret-change-me');

type Viewer = { sub: string; role?: string; email?: string };
type Context = { viewer: Viewer };

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
      account: async (_p, { id }) => json(`${accountUrl}/accounts/${id}`),
      plans: async () => json(`${accountUrl}/accounts/plans/catalog`),
      orders: async (_p, { accountId }) => json(`${accountUrl}/accounts/${accountId}/orders`),
      upgradeEligibility: async (_p, { accountId }) => json(`${accountUrl}/accounts/${accountId}/upgrade-eligibility`),
      invoices: async (_p, { accountId }) => json(`${billingUrl}/accounts/${accountId}/invoices`),
      supportAsk: async (_p, { question, accountId }) => json(`${aiUrl}/support/ask`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ question, account_id: accountId }) }),
    },
    Mutation: {
      updateAccount: async (_p, { id, phone, billingAddress }) => json(`${accountUrl}/accounts/${id}`, {
        method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ phone, billingAddress }),
      }),
      payInvoice: async (_p, { invoiceId, amount }) => json(`${billingUrl}/invoices/${invoiceId}/pay`, {
        method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ amount, provider: 'sandbox' }),
      }),
      requestPlanChange: async (_p, { accountId, toPlanId }, ctx) => json(`${billingUrl}/accounts/${accountId}/plan-changes`, {
        method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ toPlanId, requestedBy: ctx.viewer.sub }),
      }),
    },
  },
});

async function json(url: string, init?: RequestInit) {
  const response = await fetch(url, init);
  if (!response.ok) throw new Error(`upstream_${response.status}`);
  return response.json();
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
