# Contributing to Neo4j Google ADK Investment Agent

Thank you for your interest in contributing! We welcome contributions of all kinds.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/neo4j-google-adk.git`
3. Create a virtual environment: `uv venv`
4. Activate it: `source .venv/bin/activate`
5. Install dependencies: `uv pip install -r requirements.txt`
6. Create a new branch for your feature: `git checkout -b feature/your-feature-name`

## Setting Up Your Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your Neo4j credentials and configuration

3. Never commit `.env` - it's in `.gitignore` for security

## Making Changes

- Write clear, descriptive commit messages
- Include docstrings for new functions
- Update the README if you add new features or change configuration
- Test your changes thoroughly

## Code Style

- Follow PEP 8 conventions
- Use type hints for function parameters and return types
- Add docstrings to all functions and classes

## Testing Your Changes

```bash
# Verify the module imports without errors
python -c "from investment_agent import agent; print('Success!')"

# Run the web server locally
uv run adk web
```

## Submitting a Pull Request

1. Push your branch to your fork
2. Create a pull request against the main branch
3. Describe your changes clearly in the PR description
4. Reference any related issues
5. Wait for review and address any feedback

## Reporting Issues

- Use descriptive titles for bug reports
- Include steps to reproduce
- Share relevant error messages and logs
- Specify your Python version and environment

## Questions?

Feel free to open an issue for any questions or discussions!

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
