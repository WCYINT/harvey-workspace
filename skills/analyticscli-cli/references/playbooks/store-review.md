# Store Review Playbook

## Goal

Measure where review prompts are shown and which placements correlate with positive outcomes.

## Credential Source

- Get `readonly_token` (CLI) and publishable ingest API key (SDK) in project **API Keys** at [dash.analyticscli.com](https://dash.analyticscli.com).
- Optional: get `project_id` from project context for explicit `--project` overrides.
- Preferred: set the CLI default project once with `analyticscli projects select` (arrow-key picker).

## Recommended Events

- `review_prompt:eligible`
- `review_prompt:shown`
- `review_prompt:requested`
- `review_prompt:result`

## Recommended Properties

- `screen`
- `trigger`
- `fromScreen`
- `paywallId`
- `sessionCount`
- `daysSinceInstall`
- `hasPurchased`
- `plan`
- `appVersion`
- `platform`

## Key Questions

- Which screen has the best review completion rate?
- Does prompting near paywall help or hurt purchase conversion?
- Which trigger performs best by country or appVersion?

## CLI Queries

Completion after shown:

```bash
analyticscli conversion-after --from review_prompt:shown --to review_prompt:result --last 30d
```

Breakdown by screen:

```bash
analyticscli breakdown --type conversion_after --from review_prompt:shown --to review_prompt:result --by screen --last 30d
```
