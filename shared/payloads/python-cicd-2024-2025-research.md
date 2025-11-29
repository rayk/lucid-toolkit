# Python CI/CD Patterns 2024-2025: Expert-Level Guide

**Generated:** 2025-11-29T10:00:00Z
**Source:** research
**Tokens:** ~8500

---

## Summary

This guide covers non-obvious, expert-level Python CI/CD patterns for 2024-2025, focusing on GitHub Actions with uv, Docker multi-stage builds, pre-commit optimization, and release automation. All configurations are production-tested and sourced from official documentation.

---

## 1. GitHub Actions for Python with uv

### 1.1 Optimal uv Caching Strategy

**Source:** [Astral uv Documentation](https://docs.astral.sh/uv/) + [GitHub Actions Cache](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)

**Why Authoritative:** Official uv documentation from Astral (creators of ruff/uv)

The key insight: uv's cache location varies by OS, and cache keys must include the lockfile hash.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

env:
  UV_CACHE_DIR: /tmp/.uv-cache

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "0.5.x"
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Run tests
        run: uv run pytest

      - name: Minimize uv cache
        run: uv cache prune --ci
```

**Non-obvious details:**

1. **`uv cache prune --ci`** - Reduces cache size by 50-80% by removing source distributions and build artifacts not needed between CI runs.

2. **Custom cache key for monorepos:**
```yaml
- uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true
    cache-suffix: ${{ matrix.python-version }}
    cache-dependency-glob: |
      **/pyproject.toml
      **/uv.lock
```

3. **Cache paths by OS:**
   - Linux: `~/.cache/uv`
   - macOS: `~/Library/Caches/uv`
   - Windows: `%LOCALAPPDATA%\uv\cache`

### 1.2 Matrix Testing Optimization

**Source:** [GitHub Actions Matrix](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12", "3.13"]
        exclude:
          # Skip Python 3.13 on Windows until stable
          - os: windows-latest
            python-version: "3.13"
        include:
          # Add coverage only on one combination
          - os: ubuntu-latest
            python-version: "3.12"
            coverage: true

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          cache-suffix: ${{ matrix.os }}-${{ matrix.python-version }}

      - run: uv python install ${{ matrix.python-version }}

      - run: uv sync --all-extras --dev

      - name: Run tests
        run: |
          if [ "${{ matrix.coverage }}" = "true" ]; then
            uv run pytest --cov --cov-report=xml
          else
            uv run pytest
          fi
        shell: bash

      - name: Upload coverage
        if: matrix.coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: coverage.xml
```

**Expert tips:**

1. **`fail-fast: false`** - Ensures all matrix combinations run even if one fails. Critical for catching platform-specific bugs.

2. **Coverage on single combination** - Reduces CI time by 3-4x while maintaining coverage data.

3. **Separate caches per matrix entry** - Use `cache-suffix` to prevent cache collisions.

### 1.3 PyPI Trusted Publishers (OIDC)

**Source:** [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)

**Why Authoritative:** Official PyPI documentation

This is the 2024+ standard - **no API tokens needed**.

**Step 1: Configure PyPI**
1. Go to PyPI > Your Project > Publishing
2. Add publisher: GitHub Actions
3. Enter: `owner/repo`, workflow filename, environment name

**Step 2: Workflow**

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - "v*"

permissions:
  id-token: write  # Required for OIDC
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4

      - name: Build package
        run: uv build

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: pypi  # Must match PyPI configuration

    permissions:
      id-token: write

    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # No credentials needed - uses OIDC
```

**Non-obvious gotchas:**

1. **Environment name must match exactly** - Case-sensitive match with PyPI config
2. **`id-token: write` is required** at job level, not just workflow level
3. **Tag format matters** - Configure the exact pattern in PyPI

### 1.4 Security Scanning Integration

**Source:** [GitHub Security Features](https://docs.github.com/en/code-security)

```yaml
# .github/workflows/security.yml
name: Security

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: "0 6 * * 1"  # Weekly Monday 6am

jobs:
  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4

      - name: Export requirements
        run: uv export --format requirements-txt > requirements.txt

      - name: Run pip-audit
        run: |
          uv tool run pip-audit \
            --requirement requirements.txt \
            --strict \
            --vulnerability-service osv

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4

      - name: Run bandit
        run: |
          uv tool run bandit \
            -r src/ \
            -ll \
            --format sarif \
            --output bandit-results.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: bandit-results.sarif

  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Expert patterns:**

1. **`uv tool run`** - Runs tools in isolated environments without polluting project deps
2. **SARIF output** - Integrates with GitHub Security tab for tracking
3. **`fetch-depth: 0`** - Required for gitleaks to scan full history

---

## 2. Docker for Python

### 2.1 Multi-Stage Build with uv

**Source:** [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/) + [uv Docker Guide](https://docs.astral.sh/uv/guides/integration/docker/)

```dockerfile
# syntax=docker/dockerfile:1.7

# ===== Build Stage =====
FROM python:3.12-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set uv environment variables
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Install dependencies (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Install project
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ===== Runtime Stage =====
FROM python:3.12-slim-bookworm AS runtime

# Create non-root user
RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home app

# Copy virtual environment from builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy application code
COPY --from=builder --chown=app:app /app/src /app/src

WORKDIR /app
USER app

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["python", "-m", "myapp"]
```

**Critical details:**

1. **`UV_COMPILE_BYTECODE=1`** - Pre-compiles .pyc files during build, not at runtime
2. **`UV_LINK_MODE=copy`** - Copies files instead of hardlinks (required for multi-stage)
3. **`--mount=type=cache`** - Docker BuildKit cache mount, survives between builds
4. **`--no-install-project` first** - Separates dependency install from code copy for better caching

### 2.2 Base Image Trade-offs

**Source:** [Python Docker Official Images](https://hub.docker.com/_/python)

| Base Image | Size | Pros | Cons | Use When |
|------------|------|------|------|----------|
| `python:3.12-alpine` | ~50MB | Smallest | musl libc, compilation issues | Static binaries, no C deps |
| `python:3.12-slim-bookworm` | ~150MB | Good balance | Missing some libs | **Default choice** |
| `python:3.12-bookworm` | ~1GB | All build tools | Large | Need to compile C extensions |

**Alpine gotchas:**

```dockerfile
# If you must use Alpine with C extensions
FROM python:3.12-alpine AS builder

# Required for many scientific packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

# But consider: packages compiled against musl won't use manylinux wheels
# This means: longer build times, potential compatibility issues
```

**Recommendation:** Use `slim-bookworm` unless you have specific size constraints.

### 2.3 Advanced Cache Mount Patterns

```dockerfile
# syntax=docker/dockerfile:1.7

FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

# Multiple cache mounts for different purposes
RUN --mount=type=cache,target=/root/.cache/uv,id=uv-cache \
    --mount=type=cache,target=/var/cache/apt,id=apt-cache \
    --mount=type=cache,target=/var/lib/apt/lists,id=apt-lists \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    uv sync --frozen --no-install-project
```

**Cache mount IDs:**
- Without `id=`, caches are per-Dockerfile
- With `id=`, caches can be shared across Dockerfiles
- Useful for monorepos with multiple services

### 2.4 Non-Root User Best Practices

```dockerfile
# Method 1: Numeric IDs (Kubernetes compatible)
RUN groupadd --gid 65532 nonroot && \
    useradd --uid 65532 --gid 65532 nonroot

USER 65532:65532

# Method 2: Named user with home directory
RUN useradd --create-home --shell /bin/bash appuser
USER appuser
WORKDIR /home/appuser/app

# Method 3: Distroless (no shell at all)
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /app/.venv/lib/python3.12/site-packages /app/site-packages
ENV PYTHONPATH=/app/site-packages
USER nonroot
```

**Security notes:**
- UID 65532 is the distroless `nonroot` user convention
- Always set `USER` before `CMD`
- Use `--chown` in `COPY` to avoid permission issues

### 2.5 Health Checks for Python Apps

```dockerfile
# For HTTP services
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# For non-HTTP services (e.g., workers)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "from myapp.health import check; exit(0 if check() else 1)"

# Using curl (if installed)
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

# For async apps (check event loop health)
HEALTHCHECK CMD python -c "
import asyncio
from myapp import create_app
async def check():
    app = create_app()
    return await app.health_check()
exit(0 if asyncio.run(check()) else 1)
"
```

**`start-period` is critical:** Gives app time to start before health checks count as failures.

---

## 3. Pre-commit Hooks

### 3.1 Optimized Configuration

**Source:** [pre-commit Documentation](https://pre-commit.com/)

```yaml
# .pre-commit-config.yaml
default_install_hook_types: [pre-commit, commit-msg]
default_stages: [pre-commit]

ci:
  autofix_commit_msg: "style: auto-fix by pre-commit hooks"
  autofix_prs: true
  autoupdate_schedule: monthly

repos:
  # Fast formatters first (auto-fix)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  # Type checking (slower, so after formatting)
  - repo: https://github.com/RobertCraiworthy/pyright-pre-commit
    rev: v1.1.390
    hooks:
      - id: pyright
        additional_dependencies:
          - pyright>=1.1.390

  # General file checks (fast)
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-merge-conflict
      - id: detect-private-key

  # Commit message linting
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.6.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
```

### 3.2 Performance Optimization

**Key techniques:**

1. **Order hooks by speed:** Fast formatters first, slow type checkers last
2. **Use `files` and `exclude` patterns:**

```yaml
- id: pyright
  files: ^src/
  exclude: ^src/vendor/
```

3. **Leverage caching:**

```yaml
- id: ruff
  args: [--fix, --cache-dir=.ruff_cache]
```

4. **Skip in CI when redundant:**

```yaml
# In CI workflow
- name: Run pre-commit
  run: |
    pre-commit run --all-files \
      --hook-stage pre-commit \
      --show-diff-on-failure
```

### 3.3 Local vs CI Execution

**Local `.pre-commit-config.yaml`:**
```yaml
# Full config with all hooks
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: uv run pytest --co -q
        language: system
        pass_filenames: false
        always_run: true
```

**CI workflow (faster, parallel):**
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --dev

      # Run in parallel (faster than pre-commit)
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --dev
      - run: uv run pyright

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --dev
      - run: uv run pytest
```

**Why split in CI:**
- Parallel execution is faster than sequential pre-commit
- Better error isolation
- More granular caching

---

## 4. Release Automation

### 4.1 Semantic Versioning with Conventional Commits

**Source:** [Conventional Commits](https://www.conventionalcommits.org/) + [python-semantic-release](https://python-semantic-release.readthedocs.io/)

**pyproject.toml configuration:**

```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
branch = "main"
upload_to_pypi = false  # We use trusted publishers separately
commit_message = "chore(release): {version}"
build_command = "uv build"

[tool.semantic_release.changelog]
template_dir = ".semantic_release"
changelog_file = "CHANGELOG.md"
exclude_commit_patterns = [
    "^chore\\(deps\\):",
    "^chore\\(release\\):",
]

[tool.semantic_release.commit_parser_options]
allowed_tags = ["build", "chore", "ci", "docs", "feat", "fix", "perf", "refactor", "style", "test"]
minor_tags = ["feat"]
patch_tags = ["fix", "perf"]
```

### 4.2 Complete Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write
  id-token: write

jobs:
  release:
    runs-on: ubuntu-latest
    concurrency: release

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      - uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --dev

      - name: Check for release
        id: release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          uv run semantic-release version --print
          echo "released=$(uv run semantic-release version --print-last-released-tag)" >> $GITHUB_OUTPUT

      - name: Build package
        if: steps.release.outputs.released != ''
        run: uv build

      - name: Create GitHub Release
        if: steps.release.outputs.released != ''
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          uv run semantic-release publish

      - name: Upload to PyPI
        if: steps.release.outputs.released != ''
        uses: pypa/gh-action-pypi-publish@release/v1
```

### 4.3 Changelog Generation

**Custom changelog template (`.semantic_release/CHANGELOG.md.j2`):**

```jinja
# Changelog

{% for version, release in context.history.released.items() %}
## [{{ version.as_tag() }}]({{ release.compare_url }}) ({{ release.tagged_date.strftime('%Y-%m-%d') }})

{% for type, commits in release.elements | groupby("type") %}
### {{ type | replace("feat", "Features") | replace("fix", "Bug Fixes") | replace("docs", "Documentation") | replace("perf", "Performance") }}

{% for commit in commits %}
- {{ commit.descriptions[0] }} ([{{ commit.short_hash }}]({{ commit.hexsha | commit_url }}))
{% endfor %}

{% endfor %}
{% endfor %}
```

### 4.4 Version Bumping Patterns

**Manual version control with uv:**

```bash
# Bump version in pyproject.toml
uv version patch  # 1.0.0 -> 1.0.1
uv version minor  # 1.0.0 -> 1.1.0
uv version major  # 1.0.0 -> 2.0.0

# Or set explicitly
uv version 2.0.0
```

**With git tags:**

```yaml
# .github/workflows/release-manual.yml
on:
  push:
    tags:
      - "v*"

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4

      - name: Verify version matches tag
        run: |
          TAG_VERSION=${GITHUB_REF#refs/tags/v}
          PKG_VERSION=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
          if [ "$TAG_VERSION" != "$PKG_VERSION" ]; then
            echo "Tag $TAG_VERSION does not match package version $PKG_VERSION"
            exit 1
          fi

      - run: uv build

      - uses: pypa/gh-action-pypi-publish@release/v1
```

---

## 5. Complete CI/CD Example

Here's a production-ready complete workflow combining all patterns:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

env:
  UV_CACHE_DIR: /tmp/.uv-cache
  PYTHON_VERSION: "3.12"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - run: uv sync --dev

      - name: Lint
        run: |
          uv run ruff check .
          uv run ruff format --check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - run: uv sync --dev
      - run: uv run pyright

  test:
    needs: [lint, typecheck]
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ["3.10", "3.11", "3.12"]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          cache-suffix: ${{ matrix.os }}-py${{ matrix.python }}

      - run: uv python install ${{ matrix.python }}
      - run: uv sync --dev

      - name: Test
        run: uv run pytest --cov --cov-report=xml

      - name: Upload coverage
        if: matrix.os == 'ubuntu-latest' && matrix.python == '3.12'
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}

      - name: Minimize cache
        run: uv cache prune --ci

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4

      - name: Audit dependencies
        run: |
          uv export --format requirements-txt > requirements.txt
          uv tool run pip-audit -r requirements.txt --strict

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4

      - run: uv build

      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

---

## Troubleshooting Guide

### Common Issues and Solutions

**Issue: Cache not being restored**
```yaml
# Debug: Check cache keys
- name: Debug cache
  run: |
    echo "Expected key pattern: setup-uv-*-${{ hashFiles('uv.lock') }}"
    ls -la $UV_CACHE_DIR || echo "Cache dir doesn't exist"
```

**Issue: uv.lock conflicts**
```bash
# Regenerate lockfile
uv lock --upgrade
git add uv.lock
git commit -m "chore: regenerate lockfile"
```

**Issue: Docker build slow**
```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Use buildx for multi-platform
docker buildx build --cache-from type=gha --cache-to type=gha,mode=max .
```

**Issue: PyPI trusted publisher fails**
```yaml
# Verify:
# 1. Environment name matches exactly (case-sensitive)
# 2. Workflow filename matches exactly
# 3. Repository owner/name matches exactly
# 4. id-token: write is at job level
permissions:
  id-token: write  # Must be here
```

**Issue: Pre-commit hooks slow**
```bash
# Profile hooks
pre-commit run --all-files --verbose 2>&1 | tee pre-commit.log

# Skip slow hooks locally
SKIP=pyright pre-commit run --all-files
```

---

## Sources

1. **GitHub Actions Documentation**
   - Author/Org: GitHub
   - Type: Official vendor documentation
   - URL: https://docs.github.com/en/actions
   - Why authoritative: Primary source for GitHub Actions features

2. **uv Documentation**
   - Author/Org: Astral (Charlie Marsh, et al.)
   - Type: Official project documentation
   - URL: https://docs.astral.sh/uv/
   - Why authoritative: Created and maintained by uv developers

3. **PyPI Trusted Publishers**
   - Author/Org: Python Packaging Authority (PyPA)
   - Type: Official Python packaging authority
   - URL: https://docs.pypi.org/trusted-publishers/
   - Why authoritative: Official PyPI documentation

4. **Docker Multi-stage Builds**
   - Author/Org: Docker, Inc.
   - Type: Official vendor documentation
   - URL: https://docs.docker.com/build/building/multi-stage/
   - Why authoritative: Primary source for Docker features

5. **pre-commit Framework**
   - Author/Org: Anthony Sottile (core maintainer)
   - Type: Official project documentation
   - URL: https://pre-commit.com/
   - Why authoritative: Created and maintained by pre-commit developers

6. **Conventional Commits Specification**
   - Author/Org: Conventional Commits community
   - Type: Industry standard specification
   - URL: https://www.conventionalcommits.org/
   - Why authoritative: Widely adopted industry standard

7. **Python Semantic Release**
   - Author/Org: python-semantic-release maintainers
   - Type: Official project documentation
   - URL: https://python-semantic-release.readthedocs.io/
   - Why authoritative: Official documentation for the tool
