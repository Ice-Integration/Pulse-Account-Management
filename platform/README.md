# Pulse Multi-Platform Account Management

This directory turns the original account-management simulator into a deployable product architecture with web, mobile, desktop and admin applications backed by production services.

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
| Account | Java 21 + Spring Boot | Accounts, devices, plans, orders and mutations |
| Gateway | Node.js + TypeScript + GraphQL Yoga | Unified GraphQL API |
| AI Support | Python/FastAPI planned integration | RAG, MCP, support automation |

## Infrastructure

- PostgreSQL 16 + pgvector
- Redis
- Docker Compose
- Kubernetes manifests
- GitHub Actions CI

## Local start

```bash
cd platform
cp .env.example .env
docker compose up --build
```

Services:

- GraphQL gateway: http://localhost:4000/graphql
- Identity API: http://localhost:4001
- Account API: http://localhost:8081
- PostgreSQL: localhost:5432
- Redis: localhost:6379

Run the web application separately:

```bash
cd platform/apps/web
npm install
npm run dev
```

Run mobile:

```bash
cd platform/apps/mobile
npm install
npm start
```

Run admin:

```bash
cd platform/apps/admin
npm install
npm run dev
```

## Production deployment

1. Provision managed PostgreSQL and Redis.
2. Store database credentials and JWT signing key in a secret manager.
3. Build and push service images to GHCR or another OCI registry.
4. Replace image tags in `infra/k8s/base.yaml` with immutable release tags.
5. Create the `pulse-secrets` Kubernetes secret through the deployment environment, never from committed plaintext.
6. Apply the database migration/schema.
7. Deploy the Kubernetes resources.
8. Place the GraphQL gateway behind TLS ingress/API gateway.
9. Configure client applications with the public GraphQL URL.
10. Build mobile releases using EAS/App Store Connect/Google Play Console and desktop releases with Tauri signing.

## What is usable now

The committed vertical slice supports:

- customer registration and login
- persistent users in PostgreSQL
- JWT issuance
- persistent accounts
- account detail retrieval
- account contact/billing-address updates
- plan catalog
- devices and device upgrade eligibility
- order history
- audit logging of account mutations
- GraphQL access to account operations
- React customer dashboard
- React Native account dashboard
- Vue support/admin console
- Tauri desktop foundation
- local Docker stack
- Kubernetes deployment base
- multi-language CI

## Next production milestones

The platform architecture intentionally leaves these as the next implementation layer rather than pretending they already work:

- authenticated JWT verification at the GraphQL gateway and downstream services
- refresh tokens, password reset and MFA
- real plan-change/add-on transactions
- invoices, payments and billing provider integration
- notification service for push/email/SMS
- AI support service using the OpsMind RAG/MCP patterns
- object storage for statements/documents
- database migrations with Flyway
- end-to-end tests
- seeded development data
- observability dashboards and alerts
- release/signing pipelines for iOS, Android and desktop

The legacy `APIs/pulse_account_management` package remains useful as a behavioral simulation and reference while the production services are implemented incrementally.
