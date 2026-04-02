# Versioning Guide

This guide explains how to release new versions of the BRZ API documentation using Fern's versioning system.

## How Versioning Works

Fern supports multiple documentation versions through a dropdown selector on the documentation site. Each version has its own navigation structure and can have its own pages, while also sharing common content across versions.

### Current Structure

```
fern/
├── docs.yml                  # Main config — defines versions list
├── versions/
│   └── v1.yml                # Version 1 navigation
├── docs/
│   └── pages/                # Shared pages (used by all versions)
│       ├── introduction.mdx
│       ├── authentication.mdx
│       └── ...
```

## Releasing a New Version (Step-by-Step)

### Step 1 — Create the Version File

Create a new YAML file in `fern/versions/` for the new version. For example, to create version 2:

```bash
cp fern/versions/v1.yml fern/versions/v2.yml
```

### Step 2 — Create Version-Specific Pages (Optional)

If the new version has different content, create a version-specific pages directory:

```bash
mkdir -p fern/docs/pages/v2
```

Then create or copy pages that differ between versions:

```bash
cp fern/docs/pages/introduction.mdx fern/docs/pages/v2/introduction.mdx
```

Edit the new page with version-specific content.

### Step 3 — Update the Version Navigation

Edit `fern/versions/v2.yml` to point to the correct pages. You can mix shared pages and version-specific pages:

```yaml
navigation:
  - section: Getting Started
    contents:
      - page: Introduction
        path: ../docs/pages/v2/introduction.mdx    # Version-specific page
      - page: Authentication
        path: ../docs/pages/authentication.mdx      # Shared page (same for all versions)
      - page: Onboarding Guide
        path: ../docs/pages/onboarding.mdx          # Shared page
  - section: Guides
    contents:
      - page: Cash-In (Receiving Payments)
        path: ../docs/pages/guide-cash-in.mdx       # Shared page
      # ... add more pages as needed
  - api: API Reference
```

### Step 4 — Update `docs.yml`

Add the new version to the `versions` list in `fern/docs.yml`. The **first version in the list is the default** (shown without a version prefix in the URL):

```yaml
versions:
  - display-name: v2 (Current)
    path: ./versions/v2.yml
    availability: stable
  - display-name: v1
    path: ./versions/v1.yml
    availability: deprecated
```

### Step 5 — Remove Top-Level Navigation (If First Time)

If this is the first time you are adding versioning and your `docs.yml` still has a top-level `navigation` field, **remove it**. Navigation should now live exclusively in the version files.

Before (remove this):
```yaml
# docs.yml — REMOVE these fields
navigation:
  - section: Getting Started
    contents: ...
```

After (keep only versions):
```yaml
# docs.yml — versions handle navigation
versions:
  - display-name: v2 (Current)
    path: ./versions/v2.yml
    availability: stable
  - display-name: v1
    path: ./versions/v1.yml
    availability: deprecated
```

### Step 6 — Validate and Preview

```bash
# Validate the configuration
fern check

# Preview locally
fern docs dev
```

### Step 7 — Commit and Push

```bash
git add .
git commit -m "docs: release v2 documentation"
git push origin main
```

The GitHub Action will automatically publish the updated documentation.

## Version Availability Options

| Value | Description |
|-------|-------------|
| `stable` | Current stable version |
| `ga` | Generally available |
| `beta` | Beta version |
| `deprecated` | Deprecated version |

## Customizing Version URLs

By default, Fern generates URL slugs from the `display-name`. To customize:

```yaml
versions:
  - display-name: v2 (Current)
    path: ./versions/v2.yml
    slug: v2                    # URL will be /v2/...
    availability: stable
  - display-name: v1 (Legacy)
    path: ./versions/v1.yml
    slug: v1                    # URL will be /v1/...
    availability: deprecated
```

## Hiding Old Versions

To hide a version from the navigation dropdown while keeping it accessible via direct URL:

```yaml
versions:
  - display-name: v2 (Current)
    path: ./versions/v2.yml
    availability: stable
  - display-name: v1 (Legacy)
    path: ./versions/v1.yml
    availability: deprecated
    hidden: true                # Hidden from dropdown, accessible via URL
```

## Using Version-Specific Content Within a Page

Use the `<If>` component to conditionally render content based on the current version:

```mdx
<If versions={["v2"]}>
  This content only appears in version 2.
</If>

<If versions={["v1"]}>
  This content only appears in version 1.
</If>
```

Or use the `<Versions>` component for a tabbed version selector within a page:

```mdx
<Versions>
  <Version title="v2">
    Version 2 specific content here.
  </Version>
  <Version title="v1">
    Version 1 specific content here.
  </Version>
</Versions>
```

## Using Different OpenAPI Specs Per Version

If your API spec changes between versions, create version-specific specs:

```
fern/
├── openapi/
│   ├── v1.yaml
│   └── v2.yaml
```

Update `generators.yml`:

```yaml
api:
  path: openapi/v2.yaml
```

And reference the correct spec in each version file if needed.

## Best Practices

1. **Keep the default version first** in the `versions` list in `docs.yml`.
2. **Share pages when possible** — only create version-specific pages when content actually differs.
3. **Use `slug` for clean URLs** — especially when display names include extra text like "(Current)" or "(Legacy)".
4. **Mark old versions as `deprecated`** — this shows a visual indicator to users.
5. **Test locally before pushing** — always run `fern docs dev` to preview changes.
6. **Use semantic versioning** — align documentation versions with your API versions.

## Quick Reference Commands

| Command | Description |
|---------|-------------|
| `fern check` | Validate all configuration files |
| `fern docs dev` | Start local preview server |
| `fern generate --docs` | Publish to production |
| `fern generate --docs --preview` | Generate a preview URL |
| `fern token` | Generate a CI/CD token |
