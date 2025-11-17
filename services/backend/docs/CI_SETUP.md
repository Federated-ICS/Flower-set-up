# CI/CD Setup Guide

This guide will help you set up the CI/CD pipeline for your forked repository.

## Prerequisites

- GitHub account
- Repository pushed to GitHub
- Basic understanding of GitHub Actions

## Step 1: Update Badge URLs

Replace the placeholder URLs in `README.md` with your actual repository information:

```markdown
# Before (in README.md)
[![CI Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)]...

# After
[![CI Pipeline](https://github.com/yourusername/ics-threat-detection-backend/actions/workflows/ci.yml/badge.svg)]...
```

Replace:
- `YOUR_USERNAME` with your GitHub username
- `YOUR_REPO` with your repository name

## Step 2: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. If prompted, click "I understand my workflows, go ahead and enable them"

## Step 3: First Push

Push your code to trigger the workflows:

```bash
git add .
git commit -m "Add CI/CD pipeline"
git push origin main
```

## Step 4: Monitor Workflow Runs

1. Go to the "Actions" tab in your repository
2. You should see three workflows running:
   - CI Pipeline
   - Quick Check
   - Security Scan

3. Click on any workflow to see detailed logs

## Step 5: Set Up Codecov (Optional)

For code coverage reporting:

### For Public Repositories
1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Add your repository
4. No token needed for public repos!

### For Private Repositories
1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Add your repository
4. Copy the upload token
5. Add it as a GitHub secret:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CODECOV_TOKEN`
   - Value: Your token from Codecov

## Step 6: Set Up Safety API (Optional)

For dependency vulnerability scanning:

1. Go to [pyup.io/safety](https://pyup.io/safety/)
2. Sign up for a free account
3. Get your API key
4. Add it as a GitHub secret:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `SAFETY_API_KEY`
   - Value: Your API key

Note: The free tier is sufficient for most projects.

## Step 7: Set Up Pre-commit Hooks (Recommended)

Install pre-commit hooks to run checks before committing:

```bash
# Install pre-commit
make pre-commit
# or
poetry run pre-commit install

# Test it
make pre-commit-run
# or
poetry run pre-commit run --all-files
```

This will automatically:
- Format code with Black
- Sort imports with isort
- Run linting checks
- Check for common issues

## Step 8: Configure Branch Protection (Recommended)

Protect your main branch to require CI checks before merging:

1. Go to Settings → Branches
2. Click "Add rule" or edit existing rule for `main`
3. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
4. Select required status checks:
   - `test` (from CI Pipeline)
   - `lint` (from CI Pipeline)
   - `type-check` (from CI Pipeline)
   - `quick-test` (from Quick Check)
5. Save changes

## Workflow Files Overview

### `.github/workflows/ci.yml`
Main CI pipeline with three jobs:
- **test**: Runs full test suite with PostgreSQL
- **lint**: Code formatting and linting checks
- **type-check**: Static type checking with mypy

### `.github/workflows/quick-check.yml`
Fast feedback for API tests only.

### `.github/workflows/security.yml`
Security scanning with Safety and Bandit.

## Troubleshooting

### Workflows Not Running

**Problem**: Workflows don't trigger on push

**Solutions**:
1. Check if Actions are enabled (Settings → Actions)
2. Verify workflow files are in `.github/workflows/`
3. Check branch name matches trigger (main/develop)
4. Look for syntax errors in YAML files

### PostgreSQL Connection Fails

**Problem**: Tests fail with database connection errors

**Solutions**:
1. Check service configuration in workflow file
2. Verify health check is working
3. Ensure correct DATABASE_URL in workflow
4. Add wait step if needed:
   ```yaml
   - name: Wait for PostgreSQL
     run: |
       until pg_isready -h localhost -p 5432 -U ics_user; do
         sleep 2
       done
   ```

### Tests Pass Locally but Fail in CI

**Problem**: Tests work on your machine but fail in GitHub Actions

**Common causes**:
1. **Different Python version**: CI uses 3.11, check your local version
2. **Missing environment variables**: Add them to workflow file
3. **Timezone differences**: Use UTC in tests
4. **File path issues**: Use relative paths
5. **Cached dependencies**: Clear cache in Actions

**Debug steps**:
```bash
# Match CI environment locally
pyenv install 3.11
pyenv local 3.11
poetry env use 3.11
poetry install

# Use same database URL as CI
export DATABASE_URL=postgresql+asyncpg://ics_user:ics_password@localhost:5432/ics_threat_detection_test

# Run tests
poetry run pytest tests/ -v
```

### Coverage Upload Fails

**Problem**: Codecov upload fails

**Solutions**:
1. For private repos, add `CODECOV_TOKEN` secret
2. Check if coverage.xml is generated
3. Verify Codecov service status
4. Note: Upload failure won't block CI (set to continue-on-error)

### Linting Fails

**Problem**: Black or isort checks fail

**Solutions**:
```bash
# Auto-fix formatting issues
make format
# or
poetry run black app/ tests/
poetry run isort app/ tests/

# Commit the changes
git add .
git commit -m "Fix formatting"
git push
```

### Security Scan Warnings

**Problem**: Bandit or Safety reports issues

**Solutions**:
1. Review the security report in Actions artifacts
2. Update vulnerable dependencies:
   ```bash
   poetry update
   ```
3. For false positives, add to ignore list
4. Security scans are set to continue-on-error

## Local CI Simulation

Run all CI checks locally before pushing:

```bash
# Quick check
make ci

# Or run individually
make format      # Auto-fix formatting
make lint        # Check code quality
make type-check  # Type checking
make test-cov    # Tests with coverage
```

## Monitoring and Maintenance

### Regular Tasks

**Weekly**:
- Check security scan results
- Review dependency updates
- Monitor test coverage trends

**Monthly**:
- Update dependencies: `poetry update`
- Review and update workflow versions
- Check for deprecated GitHub Actions

### Useful Commands

```bash
# View workflow runs
gh run list

# View specific run
gh run view <run-id>

# Re-run failed jobs
gh run rerun <run-id>

# Download artifacts
gh run download <run-id>
```

## Best Practices

1. **Always run tests locally** before pushing
2. **Use pre-commit hooks** to catch issues early
3. **Keep dependencies updated** regularly
4. **Monitor CI performance** and optimize slow tests
5. **Review security reports** promptly
6. **Maintain high test coverage** (>80%)
7. **Write meaningful commit messages**
8. **Keep workflows simple** and maintainable

## Next Steps

After setting up CI:

1. ✅ Verify all workflows pass
2. ✅ Set up branch protection
3. ✅ Install pre-commit hooks
4. ✅ Configure Codecov (optional)
5. ✅ Set up Safety API (optional)
6. 📝 Update README badges with your URLs
7. 🎉 Start developing with confidence!

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.com/)
- [Pre-commit Documentation](https://pre-commit.com/)

---

**Need Help?**

If you encounter issues not covered here:
1. Check the [CI/CD Documentation](CI_CD.md)
2. Review workflow logs in GitHub Actions
3. Open an issue with the `ci/cd` label

**Last Updated:** November 11, 2025
