# Repository Agent Guidelines

## Code Style
- Follow standard Python style (PEP 8).
- Keep code readable with clear variable names and comments when useful.

## Dependency Management
- Python dependencies are listed in `requirements.txt`. Add new packages there when needed.
- Node dependencies are managed through `package.json`.

## Development
- Ensure Python files at least compile before committing:
  ```bash
  python -m py_compile $(git ls-files '*.py')
  ```
- The project does not include automated tests.
- To run the FastAPI application locally:
  ```bash
  uvicorn backend.app:app --reload
  ```
