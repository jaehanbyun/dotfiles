# Conventions

## General

- Keep changes scoped to the active plan.
- Prefer simple, direct code over premature abstraction.
- Use structured parsers/APIs instead of ad hoc string manipulation where
  practical.
- Add comments only where they clarify non-obvious behavior.

## Naming

- Use descriptive names tied to product behavior.
- Avoid generic helper names when a domain term is clearer.

## Testing

- Add focused tests for logic and shared boundaries.
- Broaden tests when changing cross-module contracts or user-facing flows.

## Documentation

- Update `HANDOFF.md` when a session changes the project state.
- Add ADRs for dependency, infrastructure, data model, auth, and payment
  decisions.

