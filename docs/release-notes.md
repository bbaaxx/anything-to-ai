# Release Notes

## Unreleased

### Document Converter Bridge Contracts

- Stabilized deterministic routing precedence for local and HTTP/HTTPS inputs, including explicit unknown-extension and non-HTTP scheme handling.
- Added bridge contract test coverage across unit, integration, and contract suites, including stable required output fields and allowed variance fields.
- Added minimal `document-converter` CLI entry point with API parity for source input and `--include-metadata`, including stdout/stderr separation and non-zero failure exits.
- Hardened conversion error semantics by preserving typed conversion errors and wrapping unexpected backend failures with route/source context.
