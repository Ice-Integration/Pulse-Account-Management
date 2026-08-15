# Pulse Platform Architecture

Pulse evolves the existing account-management simulator into a deployable telecommunications account-management platform.

## Product surfaces

- Web: React + TypeScript + Vite
- Mobile: React Native + Expo for iOS and Android
- Desktop: Tauri + React + TypeScript for Windows, macOS and Linux
- Admin portal: Vue 3 + TypeScript

## Backend services

- Identity Service: Node.js + TypeScript + Fastify
- Account Service: Java 21 + Spring Boot
- Billing and Plan Service: Java 21 + Spring Boot
- Notification Service: Node.js + TypeScript
- AI Support Service: Python + FastAPI, RAG and MCP
- Edge/Device Utility Service: Rust + Axum
- API Gateway: Node.js + TypeScript + GraphQL Yoga

## Data layer

- PostgreSQL as system of record
- Redis for caching, sessions, rate limits and jobs
- pgvector for knowledge-base embeddings
- S3-compatible object storage for statements and documents

## Core user flows

1. Sign in with email/password or OAuth.
2. View account profile, lines, devices, plans and balances.
3. Update contact and billing information.
4. Check device upgrade eligibility.
5. Compare and change service plans.
6. Add/remove features.
7. View orders and billing history.
8. Chat with an AI support assistant grounded in account and knowledge data.
9. Escalate cases to human support.
10. Receive push/email/SMS notifications.

## Security

- OIDC/JWT authentication
- RBAC: customer, support_agent, supervisor, admin
- service-to-service tokens
- audit log for mutations
- rate limiting
- secrets supplied through environment/secret manager
- row-level authorization in service layer
- AI tool calls require explicit policy checks

## Deployment

Local development uses Docker Compose. Production targets Kubernetes with Helm charts and GitHub Actions pipelines. Each service has its own Docker image and health checks.
