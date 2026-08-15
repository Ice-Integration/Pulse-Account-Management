# ADR-002: Use GraphQL as the client-facing composition layer

Status: Accepted

## Context

Web, mobile and desktop clients need account, device, billing and AI data without coupling directly to internal services.

## Decision

Expose a GraphQL Yoga gateway as the public application API while keeping internal services HTTP-based and independently deployable.

## Rationale

- Clients can request the exact cross-domain data they need.
- Authentication and customer ownership checks live at one public boundary.
- Internal service URLs and service credentials remain private.
- Backend services can evolve independently without forcing each client to orchestrate them.

## Consequences

The gateway becomes a security-sensitive component and must not become a second business-logic monolith. Domain rules remain downstream. The gateway owns authentication, authorization orchestration, schema composition and client-facing error boundaries.
