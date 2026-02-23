# Projection v0.1 Contract Fixtures

This directory is the language-neutral Projection v0.1 contract source.

It freezes Projection v0.1 runtime behavior as tested by `gtaf-runtime`.

`expected.now` must be used as the deterministic evaluation timestamp.

Wall-clock evaluation is not permitted.

Consumers must assert exact `outcome` and exact `reason_code`.
