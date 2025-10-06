# Research: Prepare Repository for Python Packaging

**Date**: 2025-10-06  
**Feature**: Prepare Repository for Python Packaging  
**Status**: Complete

## Python Packaging Standards Research

### Decision: Use setuptools with pyproject.toml
**Rationale**: 
- Modern Python packaging standard (PEP 517/518)
- Declarative configuration in pyproject.toml
- Supports optional dependencies (extras)
- Compatible with existing build tools
- PyPI requires this format for distribution

**Alternatives considered**:
- setup.py only (legacy, less maintainable)
- Poetry (additional dependency, overkill for this project)
- Hatch (newer, less ecosystem support)

### Package Structure Research

### Decision: Flat package structure with anyfile_to_ai as root
**Rationale**:
- Maintains existing module organization
- Clear import paths: `from anyfile_to_ai.pdf_extractor import ...`
- Supports optional extras: `anyfile_to_ai[pdf]`
- PyPI best practices for multi-module packages

**Alternatives considered**:
- Namespace package (complex, unnecessary)
- Separate packages (loses unified distribution)
- Monolithic package (violates modularity)

### Dependency Management Research

### Decision: Exclude ML model dependencies from package
**Rationale**:
- ML models are large and platform-specific
- Users may prefer different model versions
- Reduces package size significantly
- Documentation can guide model installation
- Follows modular design principles

**Alternatives considered**:
- Include all dependencies (large package size)
- Make all ML deps optional (complex dependency graph)

### Entry Points Research

### Decision: Maintain separate CLI commands per module
**Rationale**:
- Users can install only needed modules
- Preserves existing CLI interfaces
- Clear separation of concerns
- Supports modular installation patterns

**Alternatives considered**:
- Unified CLI with subcommands (breaking change)
- Both approaches (confusing user experience)

## PyPI Distribution Requirements

### Build System Requirements
- Must use PEP 517 compatible build backend (setuptools)
- Must generate source distribution (sdist) and wheel (bdist_wheel)
- Must include all required metadata in pyproject.toml
- Must pass twine check before upload

### Metadata Requirements
- Package name: anyfile_to_ai (Python naming convention)
- Version: Semantic versioning (starting at 0.1.0)
- Description: Clear, concise package description
- Author/maintainer information
- License specification
- Project URLs (repository, documentation)
- Classifiers for PyPI discovery

### Testing Requirements
- Must test package installation in clean environment
- Must test CLI entry points after installation
- Must test Python API imports
- Must test optional extras installation

## Implementation Strategy

### Phase 1: Configuration
1. Create new pyproject.toml with proper package metadata
2. Configure optional dependencies for each module
3. Set up CLI entry points for each module
4. Update package structure to anyfile_to_ai/

### Phase 2: Build and Test
1. Test local package build
2. Test installation in virtual environment
3. Test CLI functionality after installation
4. Test Python API imports

### Phase 3: Distribution
1. Generate distribution archives
2. Validate with twine check
3. Test PyPI test upload
4. Document installation procedures

## Compliance Check

### Constitution Compliance
- ✅ Composition-First: Modular package design with optional extras
- ✅ 250-Line Rule: Configuration files only, no large files
- ✅ Minimal Dependencies: Only essential packaging tools
- ✅ Experimental Mindset: Learning Python packaging best practices
- ✅ Modular Architecture: Each module maintains single responsibility

### PyPI Standards Compliance
- ✅ PEP 517/518 compliance
- ✅ Proper metadata structure
- ✅ Optional dependencies support
- ✅ CLI entry points configuration
- ✅ Package naming conventions

## Risk Assessment

### Low Risk
- Package configuration (well-documented standards)
- Build process (standard Python tooling)
- Local testing (existing test infrastructure)

### Medium Risk
- Module structure changes (requires careful migration)
- Dependency management (ML model exclusion)
- CLI entry point configuration

### Mitigation Strategies
- Incremental testing at each phase
- Backup existing configuration
- Comprehensive test coverage
- Documentation for migration path