GitHub Actions workflow files - automation scripts that run on GitHub's servers.

**Why do we need it?** Every time you update code, you want to run the same processes:

- Run tests to ensure nothing broke
- Check code formatting
- Re-deploy documentation website if docs changed
- When releasing, build the package and upload to PyPI

**These processes are always identical** - they're deterministic recipes you can write down once. Instead of running them manually every time, you define them in workflow files and tell GitHub: "Run these when certain events happen (push, release, etc.)."

**That's what CI/CD is** - automating repetitive tasks that follow the same steps every time. GitHub Actions runs them on their servers automatically.

See [CI/CD](ci_cd.md) for details on RenderCV's workflows.