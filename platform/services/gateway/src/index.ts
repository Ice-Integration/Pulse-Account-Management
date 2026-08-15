import { createSchema, createYoga } from 'graphql-yoga';
import { createServer } from 'node:http';

const accountUrl = process.env.ACCOUNT_URL ?? 'http://localhost:8081';

const schema = createSchema({
  typeDefs: /* GraphQL */ `
    type Device { id: ID!, line_number: String!, device_identifier: String!, model: String!, financed: Boolean!, payoff_amount: Float, eligible: Boolean }
    type Plan { id: ID!, code: String!, name: String!, monthly_price: Float!, description: String }
    type Order { id: ID!, type: String!, status: String!, total: Float!, created_at: String }
    type Account { id: ID!, account_number: String!, full_name: String!, phone: String, billing_address: String, status: String!, devices: [Device!]!, plans: [Plan!]! }
    type Query {
      account(id: ID!): Account!
      plans: [Plan!]!
      orders(accountId: ID!): [Order!]!
      upgradeEligibility(accountId: ID!): [Device!]!
    }
    type Mutation { updateAccount(id: ID!, phone: String, billingAddress: String): Account! }
  `,
  resolvers: {
    Query: {
      account: async (_p, { id }) => json(`${accountUrl}/accounts/${id}`),
      plans: async () => json(`${accountUrl}/accounts/plans/catalog`),
      orders: async (_p, { accountId }) => json(`${accountUrl}/accounts/${accountId}/orders`),
      upgradeEligibility: async (_p, { accountId }) => json(`${accountUrl}/accounts/${accountId}/upgrade-eligibility`),
    },
    Mutation: {
      updateAccount: async (_p, { id, phone, billingAddress }) => json(`${accountUrl}/accounts/${id}`, {
        method: 'PATCH',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ phone, billingAddress }),
      }),
    },
  },
});

async function json(url: string, init?: RequestInit) {
  const response = await fetch(url, init);
  if (!response.ok) throw new Error(`upstream_${response.status}`);
  return response.json();
}

const yoga = createYoga({ schema, graphqlEndpoint: '/graphql' });
createServer(yoga).listen(Number(process.env.PORT ?? 4000), '0.0.0.0');
