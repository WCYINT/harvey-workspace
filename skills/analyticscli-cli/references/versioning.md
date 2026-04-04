# Versioning Notes

## Separate Two Kinds of Version

- `metadata.version` is the version of the skill instructions.
- `analyticscli-supported-range` is the CLI version range those instructions were written against.

These are different and should stay different.

## Recommended Policy

- Keep `analyticscli-cli` as the current stable skill.
- Update its supported range as long as the command surface stays compatible.
- If a future major CLI release breaks commands or workflows, create a new sibling skill such as `analyticscli-cli-v1`.
- Keep the older skill published for teams that still run the older CLI.

## What Not To Do

- Do not stuff multiple incompatible major-version workflows into one `SKILL.md`.
- Do not encode the product version only in prose without a machine-readable hint.
- Do not rename the default skill on every minor release.
