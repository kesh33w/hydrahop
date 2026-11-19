## What and why

<!-- What changes for an operator, and why. Link core/repeater PRs if this depends on them. -->

## How it was tested

<!-- Tests added or updated; bench or hardware checks and their limits. -->

## Checklist

- [ ] `pytest -p bench_test_guard private_link/tests tests` passes against core and repeater `kesh/bridge`
- [ ] `CHANGELOG.md` updated under **Unreleased**
- [ ] `docs/upgrade.md` updated if deployment steps change
- [ ] No keys, certificates, enrollment state or credentials committed
