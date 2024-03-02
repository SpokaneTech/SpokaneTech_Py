# Infrastructure

[spokanetech.org](https://spokanetech.org/) uses a few different platforms for its infrastructure needs:

- [Fly.io](https://fly.io)
    - Hosted app service
    - [PostgresSQL](https://www.postgresql.org/) database ([not managed](https://fly.io/docs/postgres/getting-started/what-you-should-know/))
- [Azure](https://azure.microsoft.com)
    - Media and static file storage

### Deployment
- The production environment is available at [spokanetech.org](https://spokanetech.org)
- The production environment is deployed to [Fly.io](https://fly.io) using `fly.toml`, `Dockerfile`, and [GitHub Actions](https://docs.github.com/actions)
- Production is automatically updated when a pull request is merged to the main branch via the [`deploy`](../.github/workflows/deploy.yml) workflow
