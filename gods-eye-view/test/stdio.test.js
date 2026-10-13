import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { spawn } from 'node:child_process';
import { mkdtemp, writeFile, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const STDIO = join(dirname(fileURLToPath(import.meta.url)), '../server/mcp/stdio.js');
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==', 'base64');

let api, base, tmp, child, buf = '', nextId = 1;
const waiters = new Map();

before(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'gev-'));
  api = http.createServer(async (req, res) => {
    const chunks = [];
    for await (const c of req) chunks.push(c);
    const body = Buffer.concat(chunks);
    const json = (code, o) => { res.writeHead(code, { 'content-type': 'application/json' }); res.end(JSON.stringify(o)); };
    if (req.url === '/api/health') return json(200, { status: 'healthy' });
    if (req.url === '/api/maps/upload') {
      assert.match(req.headers['content-type'], /multipart/);
      assert.ok(body.includes('name="type"') && body.includes('terrain'));
      return json(200, { status: 'success', map_id: 'abc-123' });
    }
    if (req.url === '/api/maps/abc-123/preview') { res.writeHead(200, { 'content-type': 'image/png' }); return res.end(PNG); }
    if (req.url === '/api/maps/abc-123/convert3d') return json(200, { echo: JSON.parse(body), model_id: 'm-1' });
    if (req.url.startsWith('/api/models/m-1/download')) { res.writeHead(200); return res.end('GLB'); }
    json(404, { status: 'error', message: 'Map not found' });
  });
  await new Promise((r) => api.listen(0, '127.0.0.1', r));
  base = `http://127.0.0.1:${api.address().port}`;
  child = spawn('node', [STDIO, '--api-base', base, '--out-dir', join(tmp, 'out')]);
  child.stdout.on('data', (d) => {
    buf += d;
    let i;
    while ((i = buf.indexOf('\n')) >= 0) {
      const msg = JSON.parse(buf.slice(0, i)); buf = buf.slice(i + 1);
      waiters.get(msg.id)?.(msg);
    }
  });
});

after(() => { child.kill(); api.close(); });

const rpc = (method, params) => new Promise((resolve) => {
  const id = nextId++;
  waiters.set(id, resolve);
  child.stdin.write(`${JSON.stringify({ jsonrpc: '2.0', id, method, params })}\n`);
});
const call = (name, args) => rpc('tools/call', { name, arguments: args });

test('initialize and list tools', async () => {
  const init = await rpc('initialize', { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 't', version: '0' } });
  assert.equal(init.result.serverInfo.name, 'gods-eye-view');
  assert.equal(init.result.protocolVersion, '2025-06-18');
  child.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n');
  const list = await rpc('tools/list');
  assert.deepEqual(list.result.tools.map((t) => t.name),
    ['health', 'upload_map', 'batch_upload_maps', 'preview_map', 'analyze_map', 'convert_to_3d', 'download_model']);
});

test('health, upload, preview, convert, download', async () => {
  assert.match((await call('health', {})).result.content[0].text, /healthy/);

  const file = join(tmp, 'm.png');
  await writeFile(file, PNG);
  const up = await call('upload_map', { file_path: file, type: 'terrain' });
  assert.match(up.result.content[0].text, /abc-123/);

  const prev = await call('preview_map', { map_id: 'abc-123' });
  assert.equal(prev.result.content[0].type, 'image');
  assert.equal(Buffer.from(prev.result.content[0].data, 'base64').equals(PNG), true);

  const conv = await call('convert_to_3d', { map_id: 'abc-123', exaggeration: 3, format: 'glb' });
  assert.deepEqual(JSON.parse(conv.result.content[0].text).echo, { exaggeration: 3, format: 'glb' });

  const dl = JSON.parse((await call('download_model', { model_id: 'm-1' })).result.content[0].text);
  assert.equal((await readFile(dl.saved_to)).toString(), 'GLB');
});

test('errors are reported as tool errors, bad ids rejected', async () => {
  const missing = await call('analyze_map', { map_id: 'nope' });
  assert.equal(missing.result.isError, true);
  assert.match(missing.result.content[0].text, /404.*Map not found/);
  const bad = await call('preview_map', { map_id: '../etc/passwd' });
  assert.equal(bad.result.isError, true);
  const unknown = await call('nope', {});
  assert.equal(unknown.error.code, -32602);
});
