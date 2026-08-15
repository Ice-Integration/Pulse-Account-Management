# Pulse Multi-Platform Account Management

Pulse is a deployable account-management platform spanning browser, mobile and desktop clients with a polyglot backend, PostgreSQL/pgvector data layer, authenticated GraphQL gateway, billing workflows, notifications and AI support.

## Applications

| Surface | Stack | Target |
|---|---|---|
| Web | React + TypeScript + Vite | Browsers |
| Mobile | React Native + Expo | iOS + Android |
| Desktop | Tauri + Rust + React/TypeScript shell | Windows + macOS + Linux |
| Admin | Vue 3 + TypeScript | Support/admin browser console |

## Services

| Service | Stack | Responsibility |
|---|---|---|
| Identity | Node.js + TypeScript + Fastify | Registration, login and JWT issuance |
| Account | Java 21 + Spring Boot | Accounts, devices, plans, orders and audited mutations |
| Gateway | Node.js + TypeScript + GraphQL Yoga | JWT-protected client API and service composition |
| Billing | Node.js + TypeScript + Fastify | Invoices, sandbox payments and scheduled plan changes |
| Notification | Node.js + TypeScript | Durable queued email/SMS/push/in-app delivery worker |
| AI Support | Python + FastAPI + OpenAI + pgvector + MCP | Grounded RAG answers, citations and support tools |

## Infrastructure

- PostgreSQL 16 + pgvector
- Redis
- SQL migrations and deterministic demo seed data
- Docker Compose
- Kubernetes base manifests
- GitHub Actions multi-stack CI

## Local start

```bash
cd platform
cp .env.example .env
# Add OPENAI_API_KEY if you want live AI support.
docker compose up --build
```

Fresh Docker volumes execute `001-init.sql`, the production feature migration and `seed.sql` in order. If you already created the database volume before these migrations existed, recreate the local volume or apply the migration manually.

Services:

- GraphQL gateway: http://localhost:4000/graphql
- Identity API: http://localhost:4001
- Billing API: http://localhost:4003
- AI support API: http://localhost:8002
- Account API: http://localhost:8081
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Authentication

1. Register or log in through the identity service.
2. Send `Authorization: Bearer <token>` to `/graphql`.
3. The gateway verifies JWT signature before executing GraphQL operations.
4. State-changing operations pass the authenticated user ID to downstream audit/workflow services.

The development secret in Docker Compose is intentionally local-only. Production must use a rotated secret or asymmetric signing keys stored outside source control.

## Product workflows

The current vertical slice supports account profile reads/updates, plan catalog, device upgrade eligibility, orders, invoices, sandbox invoice settlement, scheduled plan-change requests, queued notifications and grounded support questions.

AI support retrieves from `knowledge_documents`, rejects known prompt-injection patterns, instructs the model to use only retrieved context and returns citations. The accompanying MCP server exposes read-only account/invoice tools plus an approval-required plan-change draft tool. MCP does not directly mutate production service state.

## Demo data

`infra/postgres/seed.sql` creates a deterministic customer, support agent, account, plans, device, invoice and support knowledge. It exists for local development and automated demos only. Do not run demo seed data in a production database.

## CI

`.github/workflows/platform-ci.yml` validates:

- TypeScript builds for identity, gateway, billing and notification services
- Maven build/tests for the Java account service
- installation and bytecode compilation for the Python AI service
- Docker Compose configuration validity

## Production deployment

1. Provision managed PostgreSQL with pgvector and managed Redis.
2. Run database migrations through a controlled release job.
3. Store JWT/OpenAI/database secrets in a cloud secret manager.
4. Build immutable OCI images and push them to your registry.
5. Deploy backend services with Kubernetes or another container platform.
6. Put the GraphQL gateway behind TLS, WAF/rate limits and an API gateway/load balancer.
7. Configure web/mobile/desktop apps with the public gateway URL.
8. Replace the sandbox payment adapter with Stripe, Adyen, Paystack or another provider appropriate to the deployment market.
9. Connect notification adapters such as SES/SendGrid, Twilio and FCM/APNs.
10. Build signed iOS/Android releases through Expo EAS and signed desktop installers through Tauri release tooling.

## Security boundaries

This repository demonstrates production patterns but still requires deployment-specific security configuration. Account ownership/tenant authorization should be enforced at both gateway and downstream service layers before serving real customers. Payment processing is a sandbox adapter, notification delivery currently logs the outbound event instead of contacting a provider, and AI must never be treated as an authorization authority.

## Remaining launch work

Before handling real customer traffic, complete provider integrations, MFA/password-reset flows, service-to-service authentication, database migration automation for long-lived environments, end-to-end browser/mobile tests, rate limiting, centralized telemetry/alerts, object storage for statements, secrets rotation and signed release pipelines.

The legacy `APIs/pulse_account_management` simulator remains a behavioral reference and regression source while the production implementation evolves.
