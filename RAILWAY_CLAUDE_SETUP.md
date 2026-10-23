# Railway + Claude mobile setup

This repository is prepared as a Docker-based Railway service. The remote MCP endpoint is `https://<your-railway-domain>/mcp` and the health endpoint is `/health`.

## Deploy

1. Push this repository to GitHub and connect it as a new Railway project/service, selecting the repository root. Railway will detect `railway.toml` and build `Dockerfile`.
2. In Railway service Variables, set `PIXELMOTION_API_TOKEN` to a long random secret (at least 32 random bytes). Do not commit it or share it in a public repository. The process deliberately refuses to start in Railway without this variable.
3. Add a public Railway domain in the service Networking settings. Check `/health` returns `{"status":"ok","service":"pixelmotion-mcp"}`.
4. Note: Railway usage may incur charges according to the account's current plan/usage. Check Railway's current pricing and project usage before enabling a service.

## Connect Claude

In Claude's web settings, add a custom remote MCP connector/server at `https://<your-railway-domain>/mcp`. Select bearer-token authentication if offered and use the `PIXELMOTION_API_TOKEN` value stored in Railway Variables. Then open Claude mobile with the same account and enable that connector in a conversation. Claude's remote connector management and mobile availability vary by plan/app version; configure it on the web first if mobile does not expose connector setup.

The service is stateless and supports the MCP JSON-RPC initialize, tools/list, and tools/call requests over POST. API routes require the same bearer token in Railway. `/health`, `/`, and static companion assets remain unauthenticated; do not place secrets in them.

## Local smoke test

Install project requirements and run from the directory containing the `pixelmotion/` repository folder:

```sh
PIXELMOTION_API_TOKEN='local-test-token' PYTHONPATH="$PWD" uvicorn pixelmotion.server.api_service:app --host 127.0.0.1 --port 8000
```

Then send an MCP initialize POST to `/mcp` with `Authorization: Bearer local-test-token` and JSON body:

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke-test","version":"1.0"}}}
```
