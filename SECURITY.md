# Security

## Supported deployment mode

DataPilot is currently intended for local development and controlled portfolio
demonstrations. Do not expose the development scripts directly to untrusted users.

For hosted demos:

- keep model API keys in backend environment variables;
- set `DATAPILOT_ALLOW_CLIENT_PROVIDER_CONFIG=false` when visitors must not supply providers;
- use HTTPS and an authenticating reverse proxy;
- keep `DATAPILOT_ALLOW_EXTERNAL_PROXY=false` unless a reviewed allow-list is added;
- limit upload size, request rate, execution time, CPU, and memory;
- run generated Python in an isolated container or external sandbox;
- never mount host secrets or broad host directories into the execution environment;
- delete expired workspaces automatically.

The default Docker Compose stack is an evaluation stack. Its backend container is
an isolation boundary from the host, but it is not a hardened multi-tenant sandbox.

## Reporting a vulnerability

Please open a private GitHub security advisory for the repository rather than a
public issue when the report includes an exploitable security problem.
