# GitHub Actions Setup Guide

## Step-by-Step Instructions

### Step 1: Commit and Push Your Code

First, make sure all files are committed and pushed to GitHub:

```bash
# Check status
git status

# Add all new files
git add .

# Commit
git commit -m "Add CI/CD pipeline with GitHub Actions"

# Push to GitHub
git push origin master
```

If you don't have a remote repository yet:

```bash
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M master
git push -u origin master
```

### Step 2: Enable GitHub Actions

1. Go to your repository on GitHub: `https://github.com/YOUR_USERNAME/YOUR_REPO`
2. Click on the **"Actions"** tab at the top
3. If you see a message about workflows, click **"I understand my workflows, go ahead and enable them"**

### Step 3: Verify Workflows Are Detected

After pushing, you should see three workflows in the Actions tab:

- ✅ CI Pipeline
- ✅ Quick Check
- ✅ Security Scan

If you don't see them:
1. Check that `.github/workflows/` directory exists
2. Verify the YAML files are valid
3. Make sure you pushed to the correct branch (master or develop)

### Step 4: Trigger Your First Workflow Run

Workflows will automatically run on:
- Push to `master` or `develop` branches
- Pull requests to `master` or `develop` branches

To trigger manually:
```bash
# Make a small change
echo "# CI/CD Pipeline" >> CI_TEST.md

# Commit and push
git add CI_TEST.md
git commit -m "Test CI/CD pipeline"
git push origin master
```

### Step 5: Monitor Workflow Execution

1. Go to the **Actions** tab
2. You'll see your workflows running (yellow dot = in progress)
3. Click on any workflow to see detailed logs
4. Each job (test, lint, type-check) will show its progress

**Expected Timeline:**
- Quick Check: ~2-3 minutes
- CI Pipeline: ~5-7 minutes
- Security Scan: ~3-4 minutes

### Step 6: Fix Any Issues

If workflows fail:

1. **Click on the failed workflow**
2. **Click on the failed job** (e.g., "test", "lint")
3. **Expand the failed step** to see error details
4. **Fix the issue locally:**
   ```bash
   # Run the same checks locally
   make ci
   
   # Or specific checks
   make test
   make lint
   make type-check
   ```
5. **Commit and push the fix**

### Step 7: Update README Badges

Once workflows are running, update your README.md:

Replace these placeholders:
- `YOUR_USERNAME` → Your GitHub username
- `YOUR_REPO` → Your repository name

Example:
```markdown
# Before
[![CI Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)]

# After
[![CI Pipeline](https://github.com/johndoe/ics-threat-detection-backend/actions/workflows/ci.yml/badge.svg)]
```

### Step 8: Set Up Branch Protection (Optional but Recommended)

Protect your master branch to require CI checks before merging:

1. Go to **Settings** → **Branches**
2. Click **"Add rule"** or edit existing rule for `master`
3. Enable these options:
   - ✅ **Require a pull request before merging**
   - ✅ **Require status checks to pass before merging**
   - ✅ **Require branches to be up to date before merging**
4. In "Status checks that are required", search and select:
   - `test` (from CI Pipeline)
   - `lint` (from CI Pipeline)
   - `type-check` (from CI Pipeline)
   - `quick-test` (from Quick Check)
5. Click **"Create"** or **"Save changes"**

Now all PRs must pass CI before merging! 🎉

## Optional Integrations

### Codecov (Code Coverage Reporting)

**For Public Repositories:**
1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Click "Add new repository"
4. Select your repository
5. Done! No token needed for public repos

**For Private Repositories:**
1. Follow steps above
2. Copy the upload token
3. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
4. Click **"New repository secret"**
5. Name: `CODECOV_TOKEN`
6. Value: Paste your token
7. Click **"Add secret"**

### Safety API (Security Scanning)

1. Go to [pyup.io/safety](https://pyup.io/safety/)
2. Sign up for free account
3. Get your API key
4. Add as GitHub secret:
   - Name: `SAFETY_API_KEY`
   - Value: Your API key

Note: The free tier is sufficient for most projects.

## Troubleshooting

### Issue: Workflows Not Running

**Symptoms:** No workflows appear in Actions tab

**Solutions:**
1. Check that files are in `.github/workflows/` directory
2. Verify YAML syntax is valid
3. Ensure you pushed to `main` or `develop` branch
4. Check if Actions are enabled in Settings → Actions

### Issue: PostgreSQL Connection Fails

**Symptoms:** Tests fail with database connection errors

**Solutions:**
1. The workflow includes PostgreSQL service with health checks
2. Check the logs for the "Wait for PostgreSQL" step
3. Verify DATABASE_URL in workflow matches service config

### Issue: Tests Pass Locally but Fail in CI

**Symptoms:** `make test` works but GitHub Actions fails

**Common Causes:**
1. **Different Python version** - CI uses 3.11
2. **Missing dependencies** - Check poetry.lock is committed
3. **Environment variables** - Add to workflow if needed
4. **Timezone differences** - Use UTC in tests

**Debug Steps:**
```bash
# Match CI environment
pyenv install 3.11
pyenv local 3.11
poetry env use 3.11
poetry install

# Run tests
make test
```

### Issue: Linting Fails

**Symptoms:** Lint job fails in CI

**Solution:**
```bash
# Auto-fix locally
make format

# Verify
make lint

# Commit and push
git add .
git commit -m "Fix linting issues"
git push
```

### Issue: Dependency Cache Not Working

**Symptoms:** Slow workflow runs, dependencies reinstalled every time

**Solution:**
1. Go to **Actions** tab
2. Click **"Caches"** in left sidebar
3. Delete old caches
4. Re-run workflow

## Verification Checklist

Use this checklist to verify everything is working:

- [ ] Code pushed to GitHub
- [ ] Actions tab shows three workflows
- [ ] At least one workflow run completed
- [ ] All jobs in CI Pipeline pass (test, lint, type-check)
- [ ] Quick Check passes
- [ ] Security Scan completes (warnings are OK)
- [ ] README badges updated with correct URLs
- [ ] Badges show "passing" status
- [ ] Branch protection configured (optional)
- [ ] Codecov integration working (optional)

## Quick Commands Reference

```bash
# Test everything locally before pushing
make ci

# Run individual checks
make test          # Run tests
make lint          # Check code quality
make format        # Auto-fix formatting
make type-check    # Type checking

# Git workflow
git add .
git commit -m "Your message"
git push origin main

# View workflow status (requires GitHub CLI)
gh run list
gh run view <run-id>
gh run watch
```

## What Happens on Each Push

```
1. Push to GitHub
   ↓
2. GitHub Actions triggered
   ↓
3. Three workflows start in parallel:
   
   CI Pipeline:
   ├─ Test Job (5-7 min)
   │  ├─ Setup Python & Poetry
   │  ├─ Start PostgreSQL
   │  ├─ Run migrations
   │  ├─ Run tests with coverage
   │  └─ Upload to Codecov
   ├─ Lint Job (2-3 min)
   │  ├─ Check Black formatting
   │  ├─ Check isort imports
   │  └─ Run flake8
   └─ Type Check Job (2-3 min)
      └─ Run mypy
   
   Quick Check (2-3 min):
   └─ API tests only
   
   Security Scan (3-4 min):
   ├─ Safety dependency scan
   └─ Bandit code scan
   ↓
4. Results appear in:
   - Actions tab (detailed logs)
   - PR checks (if PR)
   - Email notifications (if enabled)
   - Status badges in README
```

## Success Indicators

You'll know everything is working when:

1. ✅ Actions tab shows green checkmarks
2. ✅ README badges show "passing"
3. ✅ No error emails from GitHub
4. ✅ PRs show required checks
5. ✅ Coverage reports appear (if Codecov enabled)

## Getting Help

If you encounter issues:

1. **Check workflow logs** - Most detailed information
2. **Review [CI_CD.md](docs/CI_CD.md)** - Comprehensive documentation
3. **Run locally** - `make ci` to reproduce issues
4. **Check GitHub Actions docs** - [docs.github.com/actions](https://docs.github.com/en/actions)

## Next Steps After Setup

Once CI is working:

1. ✅ Install pre-commit hooks: `make pre-commit`
2. ✅ Configure notifications in GitHub settings
3. ✅ Set up branch protection rules
4. ✅ Add team members to repository
5. ✅ Document CI process for team
6. ✅ Start developing with confidence!

---

**Need Help?** Open an issue with the `ci/cd` label or check the troubleshooting section above.

**Last Updated:** November 11, 2025
