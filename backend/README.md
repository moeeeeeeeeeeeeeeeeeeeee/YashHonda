# Yash Honda Backend

This folder contains the initial backend foundation for the Yash Honda quote
generation platform. The implementation follows the surviving technical spec,
the stakeholder PDFs, the legacy workbook structure, the current pricing
reference, and the locked mandatory-only AWS deployment path.

## Included in this foundation

- A normalized domain model for masters, inquiries, quotes, and audit data.
- A deterministic additive quote engine driven by master data.
- A FastAPI app exposing the first quote and inquiry endpoints.
- A SQLAlchemy-backed persistence layer for customers, inquiries, quotes, and
  audit logs.
- Environment-driven settings aligned to App Runner, RDS, S3, and Secrets
  Manager.
- A quote PDF metadata flow that mirrors private S3 storage with time-limited
  download links.
- An OpenAPI document capturing the MVP contract surface.
- Lightweight tests for quote calculation and API behavior.

## Run locally

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Database migrations

Alembic migrations live in `alembic/versions`. To apply them:

```bash
set DATABASE_URL=postgresql://user:pass@host:5432/dbname
alembic upgrade head
```

For local SQLite:

```bash
set DATABASE_URL=sqlite:///./yash_honda.db
alembic upgrade head
```

## Seed reference masters (optional)

The repository includes a seed routine that loads the sample variant rows from
`app/masters.py` into `vehicle_variants`, plus demo interchangeable accessories
(modifications and styling packages) with compatibility and exclusion groups.

```bash
python scripts/seed_reference_data.py
```

## India tax and charge modeling (current phase)

The price list you provided is already expressed as discrete charge buckets (for
example ex-showroom, RTO, insurance, standard charges, optional accessories,
and BigWing columns such as TCS when applicable). The engine models those as
individual `ChargeLine` rows so quotes stay auditable.

GST is not modeled as a separate line item yet because your source documents
appear to roll tax into the published ex-showroom and statutory components. If
finance or accounting requires an explicit GST split, we can add additional
master-driven lines once the exact breakdown is confirmed.

TCS is supported as its own line when `vehicle_variants.tcs` is non-zero.

## Interchangeable accessories and modifications

Accessory and modification SKUs live in `accessory_masters` with
`accessory_compatibility` mapping which variants they apply to. Each accessory
can belong to an `exclusion_group` with `max_per_group` to enforce mutually
exclusive packages (for example only one graphics package) while still allowing
multiple independent modifications (for example up to three items in a `mods`
group).

## Current scope

This is a backend MVP skeleton. It now persists inquiry and quote data through
SQLAlchemy, using a local SQLite database by default for development and tests.
Production is intended to switch the same codepath to PostgreSQL on RDS through
`DATABASE_URL`. The deployment target is:

- `AWS Amplify Hosting` for the frontend
- `Amazon Route 53` for DNS
- `AWS App Runner` for the FastAPI runtime
- `Amazon RDS for PostgreSQL` for persistence
- `Amazon S3` for quote PDFs
- `AWS Secrets Manager` for runtime secrets
