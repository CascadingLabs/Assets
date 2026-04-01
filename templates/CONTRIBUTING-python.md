# Contributing to {{PROJECT_NAME}}

Thanks for your interest in contributing to {{PROJECT_NAME}}! This guide covers how to get set up and what we expect from pull requests.

## Objectives

{{OBJECTIVES}}

## Clone & Setup

```bash
git clone https://github.com/CascadingLabs/{{REPO_NAME}}.git
cd {{REPO_NAME}}
uv sync --group dev
```

**Prerequisites:**

| Tool | Version | Install |
|------|---------|---------|
| Python | >= 3.10 | System or [mise](https://mise.jdx.dev) |
| uv | Latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

### Install pre-commit hooks

```bash
uvx prek install
```

[Prek](https://github.com/thesuperzapper/prek) is a Rust-based pre-commit runner that executes git hooks automatically on every `git commit`, catching issues before they reach CI. It reads the same `.pre-commit-config.yaml` format. In this repo the hooks run ruff (lint + format), mypy, check for secrets via gitleaks, and enforce conventional commit messages via commitizen. To run all hooks manually:

```bash
uvx prek run --all-files
```

### Run tests

```bash
uv run poe ci-test
```

### Full CI check

```bash
uv run poe ci-check
```

## Linting & Formatting

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting, and [Mypy](https://mypy.readthedocs.io/) for type checking. Config lives in `pyproject.toml`.

**Key rules:**

- Single quotes, 120-char line length
- Google-style docstrings
- Strict mypy with Python 3.10 target

### Commands

| Tool | Purpose | Command |
|------|---------|---------|
| Ruff lint | Linting | `uv run ruff check .` |
| Ruff format | Formatting | `uv run ruff format .` |
| Mypy | Type checking | `uv run mypy .` |
| Prek | All hooks | `uvx prek run --all-files` |

CI runs ruff, mypy, and tests on every push and PR. Your PR must pass all checks.

## Issues

We use [GitHub issue forms](https://github.com/CascadingLabs/{{REPO_NAME}}/issues/new/choose) for all issues. Pick the template that fits:

- **Bug Report** -something is broken or behaving unexpectedly.
- **Feature Request** -suggest a new feature or improvement.
- **Question** -ask a question about usage or internals.
- **Ticket** -internal planning ticket for tracked work.

Blank issues are disabled -please use a template so we have the context we need to help.

## Pull Request Rules

1. **Branch from `main`** -create a feature branch (`feat/...`, `fix/...`, `docs/...`).
2. **Keep PRs focused** -one logical change per PR.
3. **Pass CI** -lint, type check, and tests must all pass.
4. **Use the PR template** -every PR auto-fills a template. Fill in all sections:
   - **Intent** -what the PR does and why.
   - **Changes** -a summary of what was changed.
   - **GenAI usage** -check the box and describe how AI was used, if applicable. All AI-generated code must be reviewed line-by-line.
   - **Risks** -any risks or side effects this PR might introduce.
5. **Link an issue** -reference the issue your PR addresses with `Closes #<number>`.

### Commit Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/) enforced by Commitizen:

```
feat: add new feature
fix: handle edge case
docs: update README with examples
test: add integration tests
```

## Code Style

- Never use `unittest` -always `pytest`
- Use `tenacity` for retries -never `time.sleep()` in loops
- Always use `uv run` to execute commands -never bare `python` or `pip`

## License

Contributions are licensed under Apache-2.0, matching the project.
