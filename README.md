# Medical Consulting Platform Monorepo

This repository contains a Next.js web application, FastAPI backend, and Prisma database package for a medical consulting marketplace. The stack is containerised with Docker Compose and includes MailHog for transactional email testing.

## Structure

```
apps/
  web/      # Next.js front-end
  api/      # FastAPI back-end
pkg/
  db/       # Prisma schema, migrations, and seed data
```

## Getting started

1. Create a `.env` file or export environment variables as needed.
2. Run database migrations and seed data:
   ```bash
   docker compose run --rm api prisma migrate deploy --schema ../../pkg/db/schema.prisma
   docker compose run --rm api python pkg/db/seed.py
   ```
3. Start the stack:
   ```bash
   docker compose up --build
   ```
4. Access the apps:
   - Web: http://localhost:3000
   - API: http://localhost:8000/docs
   - MailHog: http://localhost:8025

## Testing

```bash
cd apps/api
pip install -r requirements.txt
pytest

cd ../web
npm install
npm run lint
npm run build
```

## GitHub Actions

CI runs API tests and Next.js lint/build on each push and pull request.
