# Tooling Stack

## Principle

Add tooling by phase. Avoid connecting services before the product need is
clear.

## Initial Phase

Required:

- source control
- local verification
- basic docs

Deferred until needed:

- error monitoring
- analytics
- auth
- database
- payments
- deployment
- release automation

## Candidate Services

| Category | Candidate | When To Add |
|---|---|---|
| Error monitoring | Sentry | Before external beta |
| Analytics | PostHog or equivalent | When funnel learning starts |
| Database/auth | Supabase or equivalent | When persistence/user identity is needed |
| Mobile release | EAS/TestFlight | When native beta is needed |
| Payments | RevenueCat/Stripe | After pricing decision |
| Web deploy | Vercel/Cloudflare | When public pages or web app are needed |

## Secret Rules

- Never commit secrets.
- Keep server-only keys out of client bundles.
- Use ignored local env files for development.
- Use provider secret stores for CI and production.

