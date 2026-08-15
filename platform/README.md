# Pulse Multi-Platform Account Management

Pulse is a deployable sandbox and production-reference account-management platform spanning browser, mobile and desktop clients with a polyglot backend, PostgreSQL/pgvector, authenticated GraphQL, billing workflows, notifications and AI support.

## Applications

| Surface | Stack | Target |
|---|---|---|
| Web | React + TypeScript + Vite | Browsers |
| Mobile | React Native + Expo | iOS + Android |
| Desktop | Tauri + Rust + React/TypeScript | Windows + macOS + Linux |
| Admin | Vue 3 + TypeScript | Support/admin browser console |

## Services

| Service | Stack | Responsibility |
|---|---|---|
| Identity | Node.js + TypeScript + Fastify | Registration, JWT access/refresh sessions, MFA and password reset |
| Account | Java 21 + Spring Boot | Accounts, devices, plans, orders and audited mutations |
| Gateway | Node.js + TypeScript + GraphQL Yoga | JWT-protected client API, ownership checks and service composition |
| Billing | Node.js + TypeScript + Fastify | Invoices, sandbox payments and scheduled plan changes |
| Notification | Node.js + TypeScript | Durable queued email/SMS/push/in-app delivery worker |
| AI Support | Python + FastAPI + OpenAI + pgvector + MCP | Grounded RAG answers, citations, safety checks and support tools |

## Infrastructure

- PostgreSQL 16 + pgvector
- Redis
- deterministic demo seed data
- Docker Compose
- Kubernetes base manifests
- OpenTelemetry Collector + Prometheus + Grafana development stack
- GitHub Actions CI, E2E, security, AI eval and release workflows

## Local start

```bash
cd platform
cp .env.example .env
# Add OPENAI_API_KEY if you want live AI support.
docker compose up --build
```

With observability:

```bash
docker compose -f docker-compose.yml -f docker-compose.observability.yml up --build
```

Core services:

- GraphQL gateway: `http://localhost:4000/graphql`
- Identity API: `http://localhost:4001`
- Billing API: `http://localhost:4003`
- AI support API: `http://localhost:8002`
- Account API: `http://localhost:8081`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`

## Authentication and authorization

1. Register or log in through Identity.
2. Send `Authorization: Bearer <token>` to GraphQL.
3. The gateway verifies the JWT before executing operations.
4. Customer-scoped account and invoice requests are checked against account ownership.
5. Support/admin roles can receive controlled elevated access.
6. Internal account and billing calls require `X-Service-Key`.
7. State-changing workflows carry the authenticated actor identity into downstream audit/workflow records.

Access tokens are short lived. Refresh sessions rotate and can be revoked. Password-reset flows invalidate sessions. Optional MFA challenges are persisted and delivered through the notification queue.

## Product workflows

The current vertical slice supports account profile reads/updates, plan catalog, device upgrade eligibility, orders, invoices, sandbox invoice settlement, scheduled plan-change requests, queued notifications and grounded support questions.

## AI support

AI support retrieves from `knowledge_documents`, rejects known prompt-injection patterns, instructs the model to use only retrieved context and returns citations. The MCP server exposes read-only account/invoice tools plus an approval-required plan-change draft tool. MCP does not directly mutate sensitive production state.

Run offline AI safety evals:

```bash
cd services/ai
python evals/run.py
```

When `PULSE_AI_BASE_URL` points to a running AI service, the same evaluator reports retrieval source hit rate, answer term coverage and citation presence against `evals/golden.json`.

## Demo

Follow `docs/DEMO.md` for a 5-10 minute walkthrough covering auth, ownership denial, billing, AI/RAG, MCP safety, observability and CI. The guide also lists the genuine screenshots to capture from a running system.

## CI and security

Repository-level GitHub Actions validate:

- TypeScript services
- React and Vue clients
- Java Maven tests/package
- Python AI installation/compilation and offline evals
- Docker Compose and observability configuration
- full-stack authorization smoke tests
- CodeQL analysis
- Trivy filesystem scanning
- production Node dependency audits
- optional live RAG quality gates
- release builds for service images and client artifacts

Dependabot monitors npm, pip, Maven and GitHub Actions dependencies.

## Production deployment

A real deployment should provision managed PostgreSQL/pgvector and Redis, run migrations through a controlled release job, store secrets in a cloud secret manager, publish immutable OCI images, deploy backend services behind TLS/WAF/API gateway controls and configure public clients with only the gateway URL.

Replace the sandbox payment flow and logged notification adapters with providers appropriate to the deployment market. Build signed iOS/Android releases with Expo/EAS or equivalent and signed desktop installers through Tauri release tooling.

## Security boundaries

AI is never an authorization authority. Customer ownership is enforced before account-scoped operations. Internal services do not trust arbitrary network callers. The development shared service key and local JWT secret are examples only and must be replaced by environment-managed secrets or workload identity in production.

## Remaining environment-specific launch work

Before serving real telecom customers, complete carrier/provisioning integration, real payment-provider webhooks and reconciliation, outbound email/SMS/push providers, secret rotation, production telemetry export/alerting, backup/restore drills, signed store releases and environment-specific infrastructure hardening.

The legacy `APIs/pulse_account_management` simulator remains a behavioral reference and regression source while the production implementation evolves.
