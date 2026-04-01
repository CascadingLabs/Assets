# Contributing to {{PROJECT_NAME}}

Thanks for your interest in contributing to {{PROJECT_NAME}}! This guide covers how to get set up and what we expect from pull requests.

## Objectives

{{OBJECTIVES}}

## Clone & Setup

```bash
git clone https://github.com/CascadingLabs/{{REPO_NAME}}.git
cd {{REPO_NAME}}
```

**Prerequisites:**

| Tool | Version | Install |
|------|---------|---------|
| Rust | >= {{MSRV}} | [rustup.rs](https://rustup.rs) |

{{ADDITIONAL_PREREQUISITES}}

### Install pre-commit hooks

```bash
uvx prek install
```

[Prek](https://github.com/thesuperzapper/prek) is a Rust-based pre-commit runner that executes git hooks automatically on every `git commit`, catching issues before they reach CI. It reads the same `.pre-commit-config.yaml` format. In this repo the hooks run cargo fmt on commit, check for secrets via gitleaks, and enforce conventional commit messages via commitizen. Clippy and cargo deny are run in the manual stage (CI). To run all hooks manually:

```bash
uvx prek run --all-files
```

### Build

```bash
cargo build
```

### Run tests

```bash
cargo test
```

## Linting & Formatting

### Rust

```bash
cargo check --workspace
cargo clippy --workspace
cargo fmt --check
```

- Follow standard Rust conventions (`rustfmt` defaults)
- Clippy config lives in `clippy.toml`
- `print!`/`println!` are disallowed -use `tracing` instead
- Use `thiserror` for error types

{{ADDITIONAL_LINT_SECTIONS}}

CI runs clippy and tests on every push and PR. Your PR must pass all checks.

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
3. **Pass CI** -compilation, clippy, and tests must all pass.
4. **Use the PR template** -every PR auto-fills a template. Fill in all sections:
   - **Intent** -what the PR does and why.
   - **Changes** -a summary of what was changed.
   - **GenAI usage** -check the box and describe how AI was used, if applicable. All AI-generated code must be reviewed line-by-line.
   - **Risks** -any risks or side effects this PR might introduce.
5. **Link an issue** -reference the issue your PR addresses with `Closes #<number>`.

### Commit Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new capability
fix: handle edge case
test: add integration test
```

## License

Contributions are licensed under Apache-2.0, matching the project.
