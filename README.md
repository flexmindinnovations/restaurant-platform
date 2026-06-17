# Restaurant Platform

AI-Powered Multi-Vendor Restaurant Ordering Platform.

## Architecture

- **Backend**: Python 3.13+ / FastAPI / SQLAlchemy 2.x / PostgreSQL 17 / Redis / Celery
- **Frontend**: Angular v22 / Angular Material / TailwindCSS / Nx
- **Mobile**: Flutter / Riverpod / GoRouter (Customer, Restaurant, Delivery apps)
- **AI**: OpenAI / LangGraph / pgvector
- **Infrastructure**: AWS (ECS Fargate, RDS, ElastiCache) / Terraform / GitHub Actions

## Repository Structure

```
restaurant-platform/
├── backend/          — FastAPI modular monolith
├── frontend/         — Angular v22 admin dashboard (Nx workspace)
├── mobile/           — Flutter apps + shared packages (Melos workspace)
├── ai/               — AI platform module
├── infrastructure/   — Terraform + Docker Compose
├── docs/             — Architecture specs & guides
├── scripts/          — Developer convenience scripts
├── tools/            — Code generators, git hooks, templates
└── .github/          — CI/CD workflows, issue templates
```

## Quick Start

### Prerequisites

- Docker Desktop >= 4.30
- Python 3.13+ with [uv](https://docs.astral.sh/uv/)
- Node.js 22 LTS
- Flutter (stable)

### Setup

```bash
# 1. Start local services
make infra-up

# 2. Setup and start backend
make backend-install
make backend-migrate
make backend-dev

# 3. Setup and start frontend
make frontend-install
make frontend-dev

# 4. Setup mobile
make mobile-install
```

## Documentation

- [Project Bootstrap Specification](docs/Project_Bootstrap_and_Repository_Setup_Specification_v1.md)
- [Development Setup Guide](docs/guides/development-setup.md)
- [Coding Standards](docs/guides/coding-standards.md)

## License

Proprietary. All rights reserved.
