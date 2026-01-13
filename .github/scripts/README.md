# GitHub Scripts

This directory contains scripts used by GitHub Actions workflows.

## purge-jsdelivr-cache.js

Purges jsDelivr CDN cache for all theme files in the repository after a release.

### How it works

1. **Identifies files to purge**: The script purges all theme CSS files for multiple URL variants:
   - Specific version: `/gh/repo@v1.0.0/theme/theme.css`
   - Latest tag: `/gh/repo@latest/theme/theme.css`
   - Default branch: `/gh/repo/theme/theme.css`

2. **Submits purge request**: Makes a POST request to `https://purge.jsdelivr.net/` with all paths to purge

3. **Polls for completion**: Checks the purge status every second until the operation completes or times out (max 60 seconds)

4. **Reports results**: Displays detailed results and fails if any paths couldn't be purged

### Usage

The script is automatically run by the [`release-and-purge.yml`](../.github/workflows/release-and-purge.yml) workflow when a new version tag is pushed.

**Required environment variables:**
- `GITHUB_REPOSITORY`: The repository name (e.g., `owner/repo`)
- `GITHUB_REF_NAME`: The tag name (e.g., `v1.0.0`)

**Manual usage:**
```bash
GITHUB_REPOSITORY=owner/repo GITHUB_REF_NAME=v1.0.0 node .github/scripts/purge-jsdelivr-cache.js
```

### Adding new themes

To add a new theme to the purge list, update the `themes` array in the script:

```javascript
const themes = ['leaf', 'lessflowery', 'letterpress', 'superstack', 'your-new-theme'];
```

### API Reference

The script uses the [jsDelivr Purge API](https://www.jsdelivr.com/tools/purge):
- **Purge endpoint**: `POST https://purge.jsdelivr.net/`
- **Status endpoint**: `GET https://purge.jsdelivr.net/status/{id}`

### Throttling

jsDelivr may throttle purge requests if the same path is purged too many times within an hour. The script will report any throttled paths in the output.
