#!/usr/bin/env node
// God's Eye View - MCP server (stdio transport, newline-delimited JSON-RPC 2.0).
// Wraps the 2d-3d-mapper HTTP API so Claude can upload maps, analyze them and
// convert them to 3D models. Zero dependencies; requires Node >= 20.
//
// Usage: node stdio.js [--api-base http://localhost:4173] [--out-dir ./gods-eye-output]
// Env fallbacks: GODS_EYE_API_BASE, GODS_EYE_OUT_DIR. stdout is protocol-only; logs go to stderr.

import { readFile, writeFile, mkdir, stat } from 'node:fs/promises';
import { basename, extname, resolve, join } from 'node:path';
import { createInterface } from 'node:readline';

const SERVER_INFO = { name: 'gods-eye-view', version: '0.1.0' };
const SUPPORTED_PROTOCOLS = ['2025-06-18', '2025-03-26', '2024-11-05'];
const MAX_INLINE_IMAGE_BYTES = 5 * 1024 * 1024;
const REQUEST_TIMEOUT_MS = 120_000;

const MIME = {
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.tif': 'image/tiff',
  '.tiff': 'image/tiff', '.geotiff': 'image/tiff', '.bmp': 'image/bmp', '.webp': 'image/webp',
};

function parseArgs(argv) {
  const opts = {
    apiBase: process.env.GODS_EYE_API_BASE || 'http://localhost:4173',
    outDir: process.env.GODS_EYE_OUT_DIR || './gods-eye-output',
  };
  for (let i = 0; i < argv.length; i++) {
    const [flag, inline] = argv[i].split(/=(.*)/s);
    const val = () => inline ?? argv[++i];
    if (flag === '--api-base') opts.apiBase = val();
    else if (flag === '--out-dir') opts.outDir = val();
    else if (flag === '--help' || flag === '-h') {
      process.stderr.write('Usage: stdio.js [--api-base <url>] [--out-dir <dir>]\n');
      process.exit(0);
    }
  }
  opts.apiBase = opts.apiBase.replace(/\/+$/, '');
  return opts;
}

const opts = parseArgs(process.argv.slice(2));
const log = (...a) => process.stderr.write(`[gods-eye-view] ${a.join(' ')}\n`);

async function api(path, init = {}) {
  const res = await fetch(`${opts.apiBase}${path}`, { ...init, signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS) });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    let msg = text;
    try { msg = JSON.parse(text).message ?? text; } catch { /* not JSON */ }
    throw new Error(`API ${init.method || 'GET'} ${path} -> ${res.status}: ${msg.slice(0, 500)}`);
  }
  return res;
}

const apiJson = async (path, init) => (await api(path, init)).json();
const jsonPost = (body) => ({
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body ?? {}),
});
const id = (v, name) => {
  if (typeof v !== 'string' || !/^[\w-]+$/.test(v)) throw new Error(`${name} must be an id string`);
  return v;
};

async function fileBlob(path) {
  const abs = resolve(path);
  const info = await stat(abs).catch(() => null);
  if (!info?.isFile()) throw new Error(`File not found: ${abs}`);
  const type = MIME[extname(abs).toLowerCase()] || 'application/octet-stream';
  return { name: basename(abs), blob: new Blob([await readFile(abs)], { type }) };
}

const text = (obj) => ({ content: [{ type: 'text', text: typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2) }] });

const MAP_TYPES = ['elevation', 'satellite', 'terrain', 'custom'];
const FORMATS = ['glb', 'gltf', 'obj', 'ply', 'stl'];

const TOOLS = [
  {
    name: 'health',
    description: 'Check that the map-converter API behind this server is reachable.',
    inputSchema: { type: 'object', properties: {}, additionalProperties: false },
    run: async () => text(await apiJson('/api/health')),
  },
  {
    name: 'upload_map',
    description: 'Upload a local 2D map image (png, jpg, tiff, geotiff, bmp, webp) and get back a map_id.',
    inputSchema: {
      type: 'object',
      properties: {
        file_path: { type: 'string', description: 'Path to the image on the machine running this server.' },
        type: { type: 'string', enum: MAP_TYPES, description: 'Kind of map. Default: elevation.' },
      },
      required: ['file_path'],
      additionalProperties: false,
    },
    run: async ({ file_path, type = 'elevation' }) => {
      if (!MAP_TYPES.includes(type)) throw new Error(`type must be one of ${MAP_TYPES.join(', ')}`);
      const { name, blob } = await fileBlob(file_path);
      const form = new FormData();
      form.set('file', blob, name);
      form.set('type', type);
      return text(await apiJson('/api/maps/upload', { method: 'POST', body: form }));
    },
  },
  {
    name: 'batch_upload_maps',
    description: 'Upload several local map images at once. Returns per-file map_ids and failures.',
    inputSchema: {
      type: 'object',
      properties: {
        file_paths: { type: 'array', items: { type: 'string' }, minItems: 1 },
        type: { type: 'string', enum: MAP_TYPES, description: 'Default: elevation.' },
      },
      required: ['file_paths'],
      additionalProperties: false,
    },
    run: async ({ file_paths, type = 'elevation' }) => {
      if (!Array.isArray(file_paths) || !file_paths.length) throw new Error('file_paths must be a non-empty array');
      if (!MAP_TYPES.includes(type)) throw new Error(`type must be one of ${MAP_TYPES.join(', ')}`);
      const form = new FormData();
      for (const p of file_paths) {
        const { name, blob } = await fileBlob(p);
        form.append('files', blob, name);
      }
      form.set('type', type);
      return text(await apiJson('/api/maps/batch-upload', { method: 'POST', body: form }));
    },
  },
  {
    name: 'list_maps',
    description: 'List all uploaded maps (map_id, filename, size, upload time), newest first.',
    inputSchema: { type: 'object', properties: {}, additionalProperties: false },
    run: async () => text(await apiJson('/api/maps')),
  },
  {
    name: 'preview_map',
    description: 'Fetch the preview image of an uploaded map and return it as an image.',
    inputSchema: {
      type: 'object',
      properties: { map_id: { type: 'string' } },
      required: ['map_id'],
      additionalProperties: false,
    },
    run: async ({ map_id }) => {
      const res = await api(`/api/maps/${id(map_id, 'map_id')}/preview`);
      const buf = Buffer.from(await res.arrayBuffer());
      if (buf.length > MAX_INLINE_IMAGE_BYTES) {
        throw new Error(`Preview is ${buf.length} bytes, over the ${MAX_INLINE_IMAGE_BYTES} byte inline limit.`);
      }
      const mimeType = (res.headers.get('content-type') || 'image/png').split(';')[0];
      return { content: [{ type: 'image', data: buf.toString('base64'), mimeType }] };
    },
  },
  {
    name: 'analyze_map',
    description: 'Analyze an uploaded map (elevation range, dimensions, suggested conversion settings).',
    inputSchema: {
      type: 'object',
      properties: { map_id: { type: 'string' } },
      required: ['map_id'],
      additionalProperties: false,
    },
    run: async ({ map_id }) => text(await apiJson(`/api/maps/${id(map_id, 'map_id')}/analyze`, { method: 'POST' })),
  },
  {
    name: 'convert_to_3d',
    description: 'Convert an uploaded 2D map into a 3D terrain model. Returns model_id, mesh stats and download_url.',
    inputSchema: {
      type: 'object',
      properties: {
        map_id: { type: 'string' },
        scale: { type: 'number', description: 'Horizontal scale. Default 1.0.' },
        exaggeration: { type: 'number', description: 'Vertical exaggeration. Default 2.0.' },
        resolution: { type: 'integer', description: 'Mesh resolution. Default 256.' },
        format: { type: 'string', enum: FORMATS, description: 'Default glb.' },
        smooth: { type: 'boolean' },
        colors: { type: 'boolean', description: 'Apply terrain coloring. Default true.' },
        decimation: { type: 'number', description: 'Mesh decimation factor. Default 1.0.' },
      },
      required: ['map_id'],
      additionalProperties: false,
    },
    run: async ({ map_id, ...params }) =>
      text(await apiJson(`/api/maps/${id(map_id, 'map_id')}/convert3d`, jsonPost(params))),
  },
  {
    name: 'download_model',
    description: 'Download a converted 3D model to the local output directory and return its path.',
    inputSchema: {
      type: 'object',
      properties: {
        model_id: { type: 'string' },
        format: { type: 'string', enum: FORMATS, description: 'Default glb.' },
      },
      required: ['model_id'],
      additionalProperties: false,
    },
    run: async ({ model_id, format = 'glb' }) => {
      if (!FORMATS.includes(format)) throw new Error(`format must be one of ${FORMATS.join(', ')}`);
      const res = await api(`/api/models/${id(model_id, 'model_id')}/download?format=${format}`);
      const buf = Buffer.from(await res.arrayBuffer());
      const dir = resolve(opts.outDir);
      await mkdir(dir, { recursive: true });
      const out = join(dir, `map_model_${model_id}.${format}`);
      await writeFile(out, buf);
      return text({ saved_to: out, bytes: buf.length, format });
    },
  },
];

const toolByName = new Map(TOOLS.map((t) => [t.name, t]));

async function handle(msg) {
  const { method, params = {} } = msg;
  switch (method) {
    case 'initialize': {
      const wanted = params.protocolVersion;
      return {
        protocolVersion: SUPPORTED_PROTOCOLS.includes(wanted) ? wanted : SUPPORTED_PROTOCOLS[0],
        capabilities: { tools: { listChanged: false } },
        serverInfo: SERVER_INFO,
        instructions: `Tools for the 2D-to-3D map converter API at ${opts.apiBase}. Typical flow: upload_map -> analyze_map -> convert_to_3d -> download_model.`,
      };
    }
    case 'ping':
      return {};
    case 'tools/list':
      return { tools: TOOLS.map(({ name, description, inputSchema }) => ({ name, description, inputSchema })) };
    case 'tools/call': {
      const tool = toolByName.get(params.name);
      if (!tool) throw Object.assign(new Error(`Unknown tool: ${params.name}`), { code: -32602 });
      try {
        return await tool.run(params.arguments ?? {});
      } catch (err) {
        return { isError: true, content: [{ type: 'text', text: err.message }] };
      }
    }
    default:
      throw Object.assign(new Error(`Method not found: ${method}`), { code: -32601 });
  }
}

const send = (obj) => process.stdout.write(`${JSON.stringify(obj)}\n`);

const rl = createInterface({ input: process.stdin, crlfDelay: Infinity });
const pending = new Set();
rl.on('line', (line) => {
  if (!line.trim()) return;
  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    send({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } });
    return;
  }
  if (msg.id === undefined) return; // notification (e.g. notifications/initialized): no reply
  if (!msg.method) return; // stray response; this server sends no requests
  const p = handle(msg)
    .then((result) => send({ jsonrpc: '2.0', id: msg.id, result }))
    .catch((err) => send({ jsonrpc: '2.0', id: msg.id, error: { code: err.code ?? -32603, message: err.message } }))
    .finally(() => pending.delete(p));
  pending.add(p);
});
rl.on('close', async () => {
  await Promise.allSettled(pending);
  process.exit(0);
});

log(`ready, api-base=${opts.apiBase}`);
