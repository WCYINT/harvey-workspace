# Dedicated Events Playbook

## Goal

Provide a stable, predefined event taxonomy for the onboarding to paywall to purchase journey, so teams can build a dedicated dropoff chart without schema drift.

## Credential Source

- Get `readonly_token` (CLI) and publishable ingest API key (SDK) in project **API Keys** at [dash.analyticscli.com](https://dash.analyticscli.com).
- Optional: get `project_id` from project context for explicit `--project` overrides.
- Preferred: set the CLI default project once with `analyticscli projects select` (arrow-key picker).

## Canonical Event Names

- `onboarding:start`
- `onboarding:step_view`
- `onboarding:step_complete` (optional; only for steps with explicit completion semantics)
- `onboarding:complete`
- `onboarding:skip`
- `paywall:shown`
- `paywall:skip`
- `purchase:started`
- `purchase:success`
- `purchase:failed`
- `purchase:cancel`

## Required Properties

All funnel events:

- `platform`
- `runtimeEnv` (auto-attached by SDK)

Onboarding flow events (`onboarding:*`):

- `isNewUser`
- `onboardingFlowId`
- `onboardingFlowVersion`

Onboarding step events:

- `stepKey`
- `stepIndex`
- `stepCount`

Paywall and purchase events:

- `source`
- `paywallId`
- `packageId`
- `experimentVariant`
- `entitlementKey`
- `currency`

`appVersion` recommendation:
- Prefer setting `appVersion` once in SDK init/tracker defaults.
- Do not treat per-event `appVersion` payload repetition as mandatory.

## Dedicated Bar Chart Contract

Use this formula for percent of new users who executed event X:

- Denominator: distinct new users with `onboarding:start` in range
- Numerator: distinct users from the same cohort who fired event X
- Percentage: `numerator / denominator`

## Handling Onboarding Structure Changes

- Segment charts by `onboardingFlowId`.
- Keep `stepKey` stable within a flow.
- Do not merge different `stepCount` flows into one linear step chart.
- If multiple flows exist in the same window, render one chart per flow or grouped bars by flow.
