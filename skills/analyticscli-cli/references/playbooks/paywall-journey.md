# Paywall Journey Playbook

## Goal

Understand conversion from paywall entry to purchase success and identify dropoff steps.

## Credential Source

- Get `readonly_token` (CLI) and publishable ingest API key (SDK) in project **API Keys** at [dash.analyticscli.com](https://dash.analyticscli.com).
- Optional: get `project_id` from project context for explicit `--project` overrides.
- Preferred: set the CLI default project once with `analyticscli projects select` (arrow-key picker).

## Recommended Events

- `paywall:shown`
- `purchase:started`
- `purchase:success`
- `purchase:failed`
- `paywall:skip`
- `purchase:cancel`

## Recommended Properties

- `fromScreen`
- `paywallId`
- `packageId`
- `price`
- `currency`
- `experimentVariant`
- `entitlementKey`
- `appVersion`

## Key Questions

- Which entry screens produce highest paywall conversion?
- Where is the largest drop before purchase success?
- Which package or variant performs best?
- How often do users skip paywall versus purchase?
- How does conversion differ by onboarding flow version?

## CLI Queries

Funnel:

```bash
analyticscli funnel --steps paywall:shown,purchase:started,purchase:success --last 30d
```

Entry-screen conversion:

```bash
analyticscli breakdown --type conversion_after --from paywall:shown --to purchase:success --by fromScreen --last 30d
```

Dismiss trend:

```bash
analyticscli timeseries --metric event_count --event paywall:skip --interval 1d --last 30d --viz table
```
