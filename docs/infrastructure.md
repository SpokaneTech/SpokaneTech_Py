# Infrastructure

Spokane Tech uses a few different platforms for its infrastructure needs:

- [Fly.io](https://fly.io)
    - Hosted app service
    - [PostgresSQL](https://www.postgresql.org/) database ([not managed](https://fly.io/docs/postgres/getting-started/what-you-should-know/))
    - [Upstash for Redis](https://fly.io/docs/reference/redis/) for the Celery broker (managed)
- [Azure](https://azure.microsoft.com)
    - Media and static file storage
- [Sentry](https://spokane-tech.sentry.io/issues/)
    - Error tracking and reporting
    - We are currently on the [free tier](https://sentry.io/pricing/?) which only allows one account per project. If you have questions about access, reach out to [organizers@spokanetech.org](mailto:https://spokane-tech.sentry.io/issues/).

### Deployment
- The production environment is available at [https://spokanetech.org](https://spokanetech.org)
    - The production environment is deployed to [Fly.io](https://fly.io) using `fly.toml`, `Dockerfile`, and [GitHub Actions](https://docs.github.com/actions)
    - Production is automatically updated when a pull request is merged to the main branch via the [`deploy`](../.github/workflows/deploy.yml) workflow
