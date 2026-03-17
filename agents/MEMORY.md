# Agent Memory

## Packaging

- Modern setuptools validation can reject `mailto:` values inside `project.urls` in `pyproject.toml`; use HTTPS support URLs in package metadata and keep email addresses in documentation instead.

## GitHub Actions

- Scheduled integrations can fail on third-party API deprecations without any repo code change; isolate the HTTP call behind a small function and add a regression test for the exact endpoint/method contract before re-running the workflow.

## Config And Tests

- When configuration can trigger live network authentication from environment variables, add an autouse test fixture that clears the trigger vars so unit suites never accidentally hit real shared services from CI or developer shells.
