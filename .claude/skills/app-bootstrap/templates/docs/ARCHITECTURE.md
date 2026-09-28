# Architecture

## Context

{APP_NAME} is starting as a {PLATFORM} app.

## Principles

- Start with the smallest architecture that supports the first vertical slice.
- Prefer local framework conventions over custom abstractions.
- Add external services by phase, after the product need is clear.
- Record major architecture decisions in `docs/decisions/`.

## Initial Boundaries

Application:

- UI and navigation
- Domain state
- Data access boundary
- Verification boundary

Backend/API:

- Deferred unless required for the first vertical slice.

Persistence:

- Deferred until the data model is clear.

## Deferred Decisions

- Authentication
- Analytics
- Error monitoring
- Payments
- Deployment target
- Database/provider

