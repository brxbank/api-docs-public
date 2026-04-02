# BRZ API Documentation

This repository contains the source files for the **BRZ Public API** documentation, built with [Fern](https://buildwithfern.com/).

## Project Overview

The BRZ API is a complete PIX gateway (`gw-core-pix`) with direct BACEN/JDPI integration. This documentation covers all public endpoints including Cash-In, Cash-Out, PIX Keys, Webhooks, P2P Transfers, MED, and more.

## Repository Structure

```
api-docs/
├── .github/
│   └── workflows/
│       ├── publish-docs.yml      # Auto-publish on push to main
│       └── preview-docs.yml      # Preview on pull requests
├── fern/
│   ├── fern.config.json          # Fern organization and CLI version
│   ├── generators.yml            # API spec configuration
│   ├── docs.yml                  # Main docs configuration (navigation, theme, versions)
│   ├── openapi.yaml              # OpenAPI 3.0 specification (converted from Postman)
│   ├── docs/
│   │   ├── pages/                # MDX documentation pages
│   │   │   ├── introduction.mdx
│   │   │   ├── authentication.mdx
│   │   │   ├── onboarding.mdx
│   │   │   ├── rate-limits.mdx
│   │   │   ├── error-handling.mdx
│   │   │   ├── guide-cash-in.mdx
│   │   │   ├── guide-cash-out.mdx
│   │   │   ├── guide-pix-keys.mdx
│   │   │   ├── guide-webhooks.mdx
│   │   │   ├── guide-p2p.mdx
│   │   │   └── guide-med.mdx
│   │   └── assets/               # Static assets (logos, favicons)
│   └── versions/
│       └── v1.yml                # Version 1 navigation config
├── VERSIONING.md                 # Guide for releasing new documentation versions
├── .gitignore
└── README.md
```

## Prerequisites

- [Node.js](https://nodejs.org/) v18 or later
- [Fern CLI](https://buildwithfern.com/learn/docs/getting-started/quickstart): `npm install -g fern-api`

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/brxbank/api-docs.git
cd api-docs
```

### 2. Install Fern CLI

```bash
npm install -g fern-api
```

### 3. Validate Configuration

```bash
fern check
```

### 4. Preview Locally

```bash
fern docs dev
```

This starts a local preview server at `http://localhost:3000`.

### 5. Publish to Production

```bash
fern generate --docs
```

## Configuration Files

### `fern.config.json`

Contains the Fern organization name and CLI version. Update the `version` field when upgrading the Fern CLI.

### `docs.yml`

The main configuration file that controls:
- **Instances**: Hosting URLs (production and staging)
- **Colors**: Brand colors for the documentation theme
- **Typography**: Font configuration
- **Navigation**: Sidebar structure with sections, pages, and API reference
- **Versions**: Documentation version definitions

### `openapi.yaml`

The OpenAPI 3.0 specification that powers the API Reference section. This was converted from the original Postman collection and contains all endpoint definitions, request/response schemas, and descriptions.

### `generators.yml`

Points Fern to the OpenAPI specification file for generating the API reference.

## CI/CD Workflows

### Automatic Publishing (`publish-docs.yml`)

Triggered on every push to `main`. Automatically publishes the documentation to the Fern-hosted site.

### Preview on PRs (`preview-docs.yml`)

Triggered on pull requests to `main`. Generates a preview URL so reviewers can see documentation changes before merging.

### Required Secret

Both workflows require the `FERN_TOKEN` repository secret. Generate it with:

```bash
fern token
```

Then add it as a repository secret named `FERN_TOKEN` in GitHub Settings > Secrets and variables > Actions.

## Editing Documentation

### Adding a New Page

1. Create a new `.mdx` file in `fern/docs/pages/`
2. Add the page to the navigation in `fern/docs.yml` (and version files if using versioning)
3. Commit and push to `main`

### Updating the API Spec

1. Update `fern/openapi.yaml` with the new endpoint definitions
2. Run `fern check` to validate
3. Commit and push to `main`

### Releasing New Versions

See [VERSIONING.md](./VERSIONING.md) for a detailed guide on how to release new documentation versions.

## Key Technologies

- **[Fern](https://buildwithfern.com/)**: Documentation platform for API docs
- **OpenAPI 3.0**: API specification standard
- **MDX**: Markdown with JSX components for rich documentation pages
- **GitHub Actions**: CI/CD for automated publishing

## Support

For questions about the BRZ API, contact the engineering team. For documentation platform issues, refer to the [Fern documentation](https://buildwithfern.com/learn/docs/getting-started/quickstart).
