# ADR-004: Use React, React Native, Vue and Tauri for client surfaces

Status: Accepted

## Context

Pulse targets customer web, iOS/Android, support/admin browser workflows and desktop use. The goal is broad platform coverage without building four unrelated backend contracts.

## Decision

Use React/TypeScript for customer web, React Native + Expo for iOS/Android, Vue 3 for the support/admin console and Tauri/Rust with a React shell for desktop distribution.

## Rationale

- TypeScript remains the dominant client language across surfaces.
- React Native/Expo provides one mobile codebase for iOS and Android.
- Tauri keeps the desktop shell small while demonstrating Rust-native integration.
- Vue gives the admin surface an independently evolvable application boundary.
- All clients depend on the same authenticated GraphQL contract.

## Consequences

There are multiple client build systems and release channels. Shared design tokens and generated GraphQL types should be introduced as the UI matures. Platform-specific signing remains a release-environment responsibility.
