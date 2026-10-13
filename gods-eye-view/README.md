# God's Eye View (MCP server)

A stdio [Model Context Protocol](https://modelcontextprotocol.io) server that lets Claude drive the
[`2d-3d-mapper`](../2d-3d-mapper) API: upload 2D maps, analyze them, convert them to 3D terrain
models and download the result. No npm dependencies; Node >= 20.

## Register with Claude Code

```bash
claude mcp add gods-eye-view -- node /abs/path/gods-eye-view/server/mcp/stdio.js --api-base http://localhost:4173
```

Replace `/abs/path` with the absolute path to this directory. Verify with `claude mcp list`.

## Options

| Flag | Env var | Default | Purpose |
|------|---------|---------|---------|
| `--api-base` | `GODS_EYE_API_BASE` | `http://localhost:4173` | Base URL of the map-converter API |
| `--out-dir` | `GODS_EYE_OUT_DIR` | `./gods-eye-output` | Where `download_model` saves files |

The mapper's Flask backend listens on port 5000 by default (`2d-3d-mapper/backend/app.py`). Either pass
`--api-base http://localhost:5000` or put a proxy/preview server on 4173 that forwards `/api/*` to it.

## Tools

| Tool | Maps to | Notes |
|------|---------|-------|
| `health` | `GET /api/health` | Connectivity check |
| `upload_map` | `POST /api/maps/upload` | Takes a local `file_path`; returns `map_id` |
| `batch_upload_maps` | `POST /api/maps/batch-upload` | Several `file_paths` |
| `preview_map` | `GET /api/maps/{id}/preview` | Returned as an inline image |
| `analyze_map` | `POST /api/maps/{id}/analyze` | |
| `convert_to_3d` | `POST /api/maps/{id}/convert3d` | scale, exaggeration, resolution, format, smooth, colors, decimation |
| `download_model` | `GET /api/models/{id}/download` | Saved to `--out-dir`; returns the path |

Typical flow: `upload_map` -> `analyze_map` -> `convert_to_3d` -> `download_model`.

## Develop

```bash
npm test   # runs the server against a mock API
```

Logs go to stderr; stdout is reserved for the protocol.
