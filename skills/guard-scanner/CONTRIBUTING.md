# Contributing to guard-scanner

First off, thank you for considering contributing to `guard-scanner`! It's people like you that make open-source such a great community to learn, inspire, and create. 

We are building this tool out of goodwill to provide a zero-dependency safety net for developers exploring Agentic AI. We rely heavily on the community to help identify new threat vectors and false positives.

## How to Contribute

### Adding Threat Patterns

The easiest way to contribute is adding new detection patterns to our TypeScript source `ts-src/patterns.ts` (or `src/patterns.js` for the compiled version):

```javascript
{
    id: 'YOUR_ID',           // Unique ID (CATEGORY_NAME format)
    cat: 'category-name',    // Threat category
    regex: /your-pattern/gi, // Detection regex
    severity: 'HIGH',        // CRITICAL | HIGH | MEDIUM | LOW
    desc: 'Description',     // Human-readable description
    codeOnly: true           // or docOnly: true, or all: true
}
```

### Adding IoCs

Add known malicious indicators to `src/ioc-db.js`:
- IPs, domains, URLs, usernames, filenames, or typosquat names

### Development

```bash
# Run tests (zero deps, just Node)
npm test

# Scan the test fixtures
node src/cli.js test/fixtures/ --verbose --check-deps

# Run with all output formats
node src/cli.js test/fixtures/ --json --sarif --html --verbose
```

### Pull Request Checklist

- [ ] Tests pass (`npm test` — 225+ tests)
- [ ] New patterns have test coverage in `test/scanner.test.js`
- [ ] No false positives against `test/fixtures/clean-skill/`
- [ ] Severity level is appropriate (see `docs/THREAT_TAXONOMY.md`)
- [ ] Description is clear and references source (Snyk, OWASP, CVE, etc.)

## Reporting Security Issues

See [SECURITY.md](SECURITY.md) for responsible disclosure procedures.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Be respectful. We're all here to make AI agents safer.

## License

By contributing, you agree your contributions will be licensed under the MIT License.
