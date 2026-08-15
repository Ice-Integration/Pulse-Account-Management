# ADR-001: Use a polyglot service architecture

Status: Accepted

## Context

Pulse spans identity, telecom account operations, billing, notifications and AI support. These workloads have different maturity, ecosystem and runtime requirements.

## Decision

Use Java 21/Spring Boot for the account domain, Node.js/TypeScript for identity, billing, notifications and API composition, and Python/FastAPI for AI/RAG/MCP workloads.

## Rationale

- Java gives the core account domain a strongly typed, mature transactional service foundation.
- TypeScript provides fast API development and shared language familiarity with client applications.
- Python has the strongest ecosystem fit for OpenAI integration, RAG evaluation and MCP experimentation.
- Service boundaries prevent one language choice from leaking across every domain.

## Consequences

The system gains workload-appropriate tooling at the cost of more build pipelines, dependency ecosystems and operational conventions. CI therefore validates each runtime independently and Docker provides a common deployment contract.
