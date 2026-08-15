# ADR-003: Use PostgreSQL + pgvector for support RAG

Status: Accepted

## Context

Pulse needs grounded AI support over operational and policy knowledge. The platform already depends on PostgreSQL for transactional data.

## Decision

Store support knowledge and embeddings in PostgreSQL using pgvector instead of introducing a separate vector database for the current scale.

## Rationale

- One operational datastore reduces infrastructure overhead for the reference implementation.
- Vector search and relational metadata can be queried together.
- Knowledge ACL/category metadata can remain close to the document record.
- The design can later move to a dedicated retrieval system if corpus size, latency or tenancy requirements justify it.

## Consequences

PostgreSQL must be sized and indexed for both transactional and retrieval workloads. Retrieval quality is treated as measurable behavior through golden datasets and evals rather than assumed from architecture alone.
