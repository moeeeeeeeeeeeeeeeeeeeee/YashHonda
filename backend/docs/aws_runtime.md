# AWS Runtime Notes

This backend is aligned to the mandatory-only AWS deployment path locked in the
current technical specification.

## Required AWS services

- `AWS Amplify Hosting` for the frontend web app
- `Amazon Route 53` for DNS
- `AWS App Runner` for the FastAPI backend runtime
- `Amazon RDS for PostgreSQL` for transactional storage
- `Amazon S3` for private PDF/document storage
- `AWS Secrets Manager` for runtime secrets

## What is intentionally excluded

The current web-only phase does not require:

- `Amazon ECS`
- `Application Load Balancer`
- `Amazon VPC / NAT Gateway`
- `AWS WAF`
- dedicated AWS CI/CD infrastructure

## Backend implications

- The app should stay stateless so it can run cleanly on App Runner.
- Runtime config should come from environment variables and Secrets Manager.
- Quote PDFs should be stored in S3 and exposed through time-limited URLs.
- PostgreSQL is the system of record for masters, inquiries, quotes, and audit
  history.
