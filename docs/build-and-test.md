# Build and test HydraHop

## Backend

Use Python 3.14 for the recorded environment. From a new checkout:

```sh
python3 tools/materialize.py --manifest components.current.json
python3 -m venv .venv
.venv/bin/pip install -r requirements-test.txt
.venv/bin/pip install --no-deps -e sources/openhop_core -e sources/openhop_repeater
PYTHONPATH=.:sources/openhop_core/src:sources/openhop_repeater:tools .venv/bin/python -m pytest -p bench_test_guard private_link/tests tests -q --timeout=10
```

Without `--manifest`, the materializer continues to use the historical `components.json`. For an original release reconstruction, check out that release's hub commit and use its original manifest. The tool refuses existing component destinations; use a separate clean checkout for a different snapshot.

The tests use loopback sockets and simulated radios. They do not require credentials or connected hardware. An operating-system sandbox that blocks socket wakeups can prevent the threaded event-loop test from finishing.

## Repeater UI

Use Node 22 and the UI fork's package lock. In the UI checkout, run:

```sh
npm ci
npm run type-check
npm run test:unit -- --run --maxWorkers=2
npm run build-only
```

To install a release on a Pi, follow the [upgrade guide](upgrade.md). For firmware and enrollment, see [Internet Link](ilink.md).
