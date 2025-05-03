# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Build: `uv build`
- Run: `uv run xlsx_value_picker <excel_file> --config <config_file>`
- Lint: `uv run ruff check src/ test/`
- Type check: `uv run mypy src/ test/`
- Test (all): `uv run pytest test/`
- Test (single): `uv run pytest test/test_file.py::TestClass::test_method -v`

## Style Guidelines

- **Line Length**: Max 120 chars
- **Modules**: Snake case (e.g., `excel_processor.py`)
- **Classes**: PascalCase (e.g., `ValidationContext`)
- **Functions/Variables**: Snake case (e.g., `load_config`)
- **Error Handling**: Base exception is `XlsxValuePickerError`, inherit for module-specific errors
- **Types**: Use strict typing and type annotations (mypy strict mode)
- **Imports**: Sorted via isort/ruff (known third-party: fastapi, pydantic, starlette)
- **Package Structure**: Separate concerns into distinct modules based on functionality
- **Pydantic Models**: Follow SRP (separate data structure from business logic) with exceptions for highly cohesive functionality

## Version Control

- Branch naming: `feature/name` for new features, `fix/issue` for bug fixes
- Semantic versioning for releases
