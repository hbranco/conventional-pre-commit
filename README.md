# conventional-pre-commit - Custom Fork

This project is a fork of the [compilerla/conventional-pre-commit](https://github.com/compilerla/conventional-pre-commit) repository, which applies pre-commit hooks to enforce the use of Conventional Commits.

## New Features

This fork adds the following features:

1. **Ignore Conventional Commits Check on MERGE:**
   - The Conventional Commits check is automatically ignored when the git stage involves a MERGE. This prevents unnecessary failures during branch integration.

2. **Prohibit Commits on the `main` Branch:**
   - Commits are blocked when attempting to commit directly to the `main` branch, enforcing best practices by encouraging the use of feature branches.
A [`pre-commit`](https://pre-commit.com) hook to check commit messages for
[Conventional Commits](https://conventionalcommits.org) formatting.

Works with Python >= 3.8.

## Usage

Make sure `pre-commit` is [installed](https://pre-commit.com#install).

Create a blank configuration file at the root of your repo, if needed:

```console
touch .pre-commit-config.yaml
```

Add a new repo entry to your configuration file:

```yaml
repos:
  # - repo: ...

  - repo: https://github.com/hbranco/conventional-pre-commit
    rev: <git sha or tag>
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: []
```

Install the `pre-commit` script:

```console
pre-commit install --hook-type commit-msg
```

Unistall the `pre-commit` script:

```console
pre-commit unistall
```
## License

[Apache 2.0](LICENSE)

Inspired by matthorgan's [`pre-commit-conventional-commits`](https://github.com/matthorgan/pre-commit-conventional-commits).
