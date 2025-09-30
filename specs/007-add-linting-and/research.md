# Pre-commit Hooks, Linting, and Testing Infrastructure Research

## Executive Summary

This research document provides decision guidance for implementing a robust pre-commit hook infrastructure for a Python 3.13 project. The recommendations prioritize developer experience, performance, and code quality while acknowledging the trade-offs between different approaches.

---

## 1. Pre-commit Framework Best Practices for Python

### Decision: Use pre-commit framework with remote hook configuration and strategic hook selection

**Recommended Configuration:**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.13.2
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### Rationale:

1. **Remote Hook Downloads**: Using remote repositories ensures team consistency and portability
2. **Hook Execution Order**: Ruff's lint hook must run before the formatter
3. **Caching Strategy**: Pre-commit automatically caches hook environments in `~/.cache/pre-commit/`
4. **Cross-Platform Compatibility**: Pre-commit works on macOS and Linux
5. **Performance Optimization**: Pre-commit runs hooks in parallel by default

### Alternatives Considered:

- **Local Hook Installation**: Rejected - portability and consistency outweigh offline capability
- **All-in-One Git Hooks**: Rejected - pre-commit framework provides superior developer experience
- **Husky (JavaScript-based)**: Rejected - pre-commit is the Python community standard

---

## 2. pytest-cov Configuration

### Decision: Configure 70% minimum coverage threshold with strategic exclusions in pyproject.toml

**Recommended Configuration:**
```toml
[tool.coverage.run]
source = ["pdf_extractor", "audio_processor", "image_processor"]
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/conftest.py",
    "*/.venv/*",
]

[tool.coverage.report]
fail_under = 70
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
show_missing = true
```

### Rationale:

1. **70% Threshold**: Balances code quality with development velocity
2. **Strategic Exclusions**: Test files, __init__ files, and boilerplate shouldn't be included
3. **Exclusion Patterns**: `pragma: no cover` allows surgical exclusion of untestable code
4. **Reporting Formats**: Terminal + HTML for comprehensive feedback
5. **pyproject.toml Integration**: Consolidate configuration in single modern standard file

### Alternatives Considered:

- **80-90% Coverage**: Rejected - diminishing returns, encourages trivial tests
- **No Minimum Threshold**: Rejected - some enforcement necessary
- **Per-File Coverage**: Rejected - complex configuration, not well-supported
- **Separate .coveragerc**: Rejected - pyproject.toml consolidation preferred

---

## 3. Ruff Auto-fix Capabilities

### Decision: Use hybrid approach with `ruff check --fix` in pre-commit and `ruff format` separately

**Recommended Hook Configuration:**
```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.13.2
  hooks:
    - id: ruff
      args: [--fix]
      name: ruff-lint-fix
    - id: ruff-format
      name: ruff-format
```

### Rationale:

1. **Ruff Check vs Format Distinction**: Separate tools that must run in sequence
2. **Auto-fixable Rules (Safe Fixes)**: F401 (unused imports), F841 (unused variables), UP (upgrades), I (import sorting), all format rules
3. **Manual Intervention Required**: C901 (complexity), E501 (line length in some cases), naming violations, logic errors
4. **Safe vs Unsafe Fixes**: By default, Ruff applies only "safe" fixes
5. **Execution Order**: `ruff check --fix` must run before `ruff format`

### Alternatives Considered:

- **Ruff Format Only**: Rejected - misses code quality issues
- **Ruff Check Without Auto-fix**: Rejected - poor developer experience
- **Auto-fix All Issues Including Unsafe**: Rejected - can introduce bugs
- **Black + Flake8 + isort**: Rejected - Ruff is now the community standard (2025)

---

## 4. Hook Bypass Mechanisms

### Decision: Allow bypass with `--no-verify` but discourage through documentation and CI enforcement

**Recommended Approach:**
1. Document when bypass is appropriate in project README
2. Enforce all checks in CI regardless of bypass
3. Use CI to catch bypassed checks
4. Monitor bypass usage (optional) through git hooks that log bypass events

### Rationale:

1. **Git --no-verify Mechanism**: `git commit --no-verify` bypasses all client-side hooks (cannot be prevented)
2. **Appropriate Bypass Scenarios**: Emergency hotfix, tool malfunction, work-in-progress, dependency updates
3. **Inappropriate Bypass Scenarios**: Avoiding linting errors, skipping tests to save time
4. **CI Enforcement Strategy**: Run identical checks in CI pipeline, prevent PR merge until CI passes
5. **SKIP Environment Variable**: Pre-commit supports `SKIP=hook-id git commit` for granular control

### Alternatives Considered:

- **Server-Side Hook Enforcement**: Rejected - doesn't work with GitHub/GitLab workflows
- **Block Bypass Attempts**: Rejected - technically infeasible
- **No Bypass Documentation**: Rejected - explicit guidance reduces misuse
- **Log All Bypass Events**: Considered but optional

---

## 5. Test Execution in Pre-commit

### Decision: Run NO tests in pre-commit hooks; execute all tests in CI only

### Rationale:

1. **Performance Considerations**: Full test suite takes 30-60+ seconds, pre-commit should be 2-5 seconds
2. **Best Practice Consensus (2025)**: Tests in CI, linting in pre-commit
3. **Developer Workflow**: Developers should run relevant tests locally before committing
4. **CI as Enforcement Layer**: CI runs full test suite on every PR
5. **Alternative Approaches**: Post-commit hook, watch mode, pre-push hook, subset testing

### Alternatives Considered:

- **Run All Tests in Pre-commit**: Rejected - destroys developer velocity
- **Run Fast Unit Tests Only**: Rejected - still too slow, incomplete coverage
- **pytest-testmon for Changed Files**: Rejected - complexity outweighs benefits
- **Pre-push Hook Instead**: Viable alternative - consider implementing as optional
- **Post-commit Hook with Notification**: Viable alternative - good for test-conscious teams
- **pytest-watch in Development**: Recommended as complement

### Recommended Test Strategy:

```markdown
## Local Development
- Run relevant tests before committing: `pytest tests/unit/test_<module>.py -v`
- Optional: Use pytest-watch for continuous testing: `ptw`
- Pre-commit runs linting and formatting only (fast feedback)

## Continuous Integration
- Full test suite runs on every PR
- Required checks: pytest, coverage >= 70%
- Blocks merge until passing
```

---

## Implementation Recommendations

### Phase 1: Basic Pre-commit Setup
1. Install pre-commit: `uv pip install pre-commit`
2. Create `.pre-commit-config.yaml` with Ruff hooks
3. Run `pre-commit install`
4. Run `pre-commit run --all-files` to validate

### Phase 2: Coverage Configuration
1. Add coverage configuration to `pyproject.toml`
2. Test locally: `pytest --cov --cov-fail-under=70`
3. Update CI to use same configuration

### Phase 3: Team Adoption
1. Document bypass guidelines in README
2. Add pre-commit status badge to README (if using pre-commit.ci)
3. Team training on when bypass is appropriate

---

## Configuration File Templates

### Complete .pre-commit-config.yaml
```yaml
# Pre-commit hooks configuration for Python 3.13 project
default_language_version:
  python: python3.13

repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.13.2
    hooks:
      - id: ruff
        args: [--fix]
        name: ruff-lint-fix
      - id: ruff-format
        name: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-case-conflict
      - id: detect-private-key
      - id: check-merge-conflict
```

### Complete pyproject.toml Coverage Section
```toml
[tool.coverage.run]
source = ["pdf_extractor", "audio_processor", "image_processor"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/conftest.py",
    "*/.venv/*",
    "*/__main__.py",
]

[tool.coverage.report]
fail_under = 70
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]

[tool.coverage.html]
directory = "htmlcov"

[tool.pytest.ini_options]
addopts = [
    "-v",
    "--tb=short",
    "--cov=pdf_extractor",
    "--cov=audio_processor",
    "--cov=image_processor",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=70",
]
```

---

## Summary of Decisions

| Topic | Decision | Key Rationale |
|-------|----------|---------------|
| **Pre-commit Framework** | Use remote hooks with Ruff + standard hooks | Portability, auto-updates, performance |
| **Coverage Threshold** | 70% minimum via pyproject.toml | Balanced quality/velocity |
| **Coverage Exclusions** | Tests, __init__.py, pragmas | Focus on application logic |
| **Ruff Auto-fix** | Hybrid: `--fix` for safe fixes | Developer experience with safety |
| **Ruff Execution** | Check before format | Proper sequencing |
| **Bypass Mechanism** | Allow --no-verify, enforce in CI | Pragmatic approach |
| **Test Execution** | NO tests in pre-commit, all in CI | Performance optimization |

---

**Document Version**: 1.0
**Date**: 2025-09-29
**Project**: makeme-a-podcast-from-docs
**Python Version**: 3.13