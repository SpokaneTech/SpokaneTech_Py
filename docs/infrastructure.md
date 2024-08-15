# Infrastructure

Spokane Tech uses a few different platforms for its infrastructure needs:

## Azure
- [Azure Web App / App Service](https://learn.microsoft.com/en-us/azure/app-service/overview)
    - We are using an [Azure Container Registry](https://learn.microsoft.com/en-us/azure/container-registry/) to store our container images
    - These container images are deployed to the app service automatically
    - We use a [sidecar app](https://learn.microsoft.com/en-us/azure/app-service/tutorial-custom-container-sidecar) to run a Celery worker and beat scheduler
- [Azure Database for PostgreSQL - Flexible Server](https://learn.microsoft.com/en-us/azure/postgresql/)
    - Hosted PostgreSQL database (currently version 16) for use with Django
- [Azure Cache for Redis](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/)
    - Currently just used as a message queue for Celery
    - May be used for caching in the future
- [Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/common/storage-introduction)
    - Media and static file storage

## Other
- [Sentry](https://spokane-tech.sentry.io/issues/)
    - Error tracking and reporting
    - We are currently on the [free tier](https://sentry.io/pricing/?) which only allows one account per project. If you have questions about access, reach out to [organizers@spokanetech.org](mailto:https://spokane-tech.sentry.io/issues/).

## CI/CD
- The production environment is available at [https://spokanetech.org](https://spokanetech.org)
    - The production environment is deployed to Azure using `Dockerfile` and [GitHub Actions](https://docs.github.com/actions)
    - Production is automatically updated when a pull request is merged to the main branch via the [`deploy`](../.github/workflows/deploy_azure.yml) workflow
