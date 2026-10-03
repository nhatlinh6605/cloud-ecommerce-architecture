// Ứng dụng TMĐT mẫu: xem sản phẩm, giỏ hàng, đặt hàng, ảnh sản phẩm (MinIO)
const express = require('express');
const { Pool } = require('pg');
const Minio = require('minio');
const client = require('prom-client');

const INSTANCE = process.env.INSTANCE || 'app';
const PORT = +process.env.PORT || 3000;
const BUCKET = process.env.MINIO_BUCKET || 'product-images';

const pool = new Pool({
  host: process.env.DB_HOST, port: +process.env.DB_PORT || 5432,
  user: process.env.DB_USER, password: process.env.DB_PASSWORD, database: process.env.DB_NAME,
  max: 10, connectionTimeoutMillis: 3000,
});
const minio = new Minio.Client({
  endPoint: process.env.MINIO_HOST, port: +process.env.MINIO_PORT || 9000, useSSL: false,
  accessKey: process.env.MINIO_ACCESS_KEY, secretKey: process.env.MINIO_SECRET_KEY,
});

client.collectDefaultMetrics();
const httpDur = new client.Histogram({
  name: 'http_request_duration_seconds', help: 'Thời gian xử lý request',
  labelNames: ['method', 'route', 'status'], buckets: [0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
});
const orders = new client.Counter({ name: 'orders_created_total', help: 'Số đơn hàng tạo' });

const app = express();
app.use(express.json());
app.use((req, res, next) => {
  const end = httpDur.startTimer();
  res.setHeader('X-Instance', INSTANCE);
  res.on('finish', () => end({ method: req.method, route: req.route ? req.route.path : req.path, status: res.statusCode }));
  next();
});
const wrap = fn => (req, res) => fn(req, res).catch(e => {
  console.error(JSON.stringify({ level: 'error', instance: INSTANCE, msg: e.message }));
  res.status(500).json({ error: 'internal' });
});

app.get('/health', async (_req, res) => {
  try { await pool.query('SELECT 1'); res.json({ status: 'ok', instance: INSTANCE }); }
  catch { res.status(503).json({ status: 'db_unavailable', instance: INSTANCE }); }
});
app.get('/metrics', async (_req, res) => {
  res.set('Content-Type', client.register.contentType); res.end(await client.register.metrics());
});

app.get('/products', wrap(async (req, res) => {
  const { rows } = await pool.query('SELECT id,name,price,image_key FROM products ORDER BY id LIMIT 50');
  res.json(rows);
}));
app.get('/products/:id', wrap(async (req, res) => {
  const { rows } = await pool.query('SELECT id,name,description,price,image_key FROM products WHERE id=$1', [req.params.id]);
  rows[0] ? res.json(rows[0]) : res.status(404).json({ error: 'not_found' });
}));
app.get('/products/:id/image', wrap(async (req, res) => {
  const { rows } = await pool.query('SELECT image_key FROM products WHERE id=$1', [req.params.id]);
  if (!rows[0]) return res.status(404).end();
  const stream = await minio.getObject(BUCKET, rows[0].image_key);
  res.type('image/svg+xml'); stream.pipe(res);
}));

app.post('/cart/:sid/items', wrap(async (req, res) => {
  const { product_id, qty = 1 } = req.body;
  await pool.query(`INSERT INTO cart_items(session_id,product_id,qty) VALUES($1,$2,$3)
    ON CONFLICT (session_id,product_id) DO UPDATE SET qty = cart_items.qty + EXCLUDED.qty`, [req.params.sid, product_id, qty]);
  res.status(201).json({ ok: true });
}));
app.get('/cart/:sid', wrap(async (req, res) => {
  const { rows } = await pool.query(`SELECT p.id,p.name,p.price,c.qty FROM cart_items c JOIN products p ON p.id=c.product_id WHERE c.session_id=$1`, [req.params.sid]);
  res.json(rows);
}));

app.post('/orders', wrap(async (req, res) => {
  const { session_id } = req.body;
  const c = await pool.connect();
  try {
    await c.query('BEGIN');
    const items = (await c.query('SELECT 1 FROM cart_items WHERE session_id=$1', [session_id])).rows;
    if (!items.length) { await c.query('ROLLBACK'); return res.status(400).json({ error: 'empty_cart' }); }
    const o = await c.query(`INSERT INTO orders(session_id,total) SELECT $1, SUM(p.price*c.qty) FROM cart_items c JOIN products p ON p.id=c.product_id WHERE c.session_id=$1 RETURNING id,total`, [session_id]);
    await c.query('DELETE FROM cart_items WHERE session_id=$1', [session_id]);
    await c.query('COMMIT'); orders.inc();
    res.status(201).json(o.rows[0]);
  } catch (e) { await c.query('ROLLBACK'); throw e; } finally { c.release(); }
}));

// Tạo bucket + ảnh mẫu (idempotent)
async function initStorage(retries = 20) {
  for (let i = 0; i < retries; i++) {
    try {
      if (!(await minio.bucketExists(BUCKET))) await minio.makeBucket(BUCKET);
      const { rows } = await pool.query('SELECT image_key FROM products');
      for (const r of rows) {
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200"><rect width="100%" height="100%" fill="#dbeafe"/><text x="50%" y="50%" text-anchor="middle" font-size="22" fill="#1e3a8a">${r.image_key}</text></svg>`;
        await minio.putObject(BUCKET, r.image_key, Buffer.from(svg), { 'Content-Type': 'image/svg+xml' });
      }
      return console.log(JSON.stringify({ level: 'info', instance: INSTANCE, msg: 'storage_ready' }));
    } catch (e) { console.log(`initStorage retry ${i + 1}: ${e.message}`); await new Promise(r => setTimeout(r, 3000)); }
  }
}
app.listen(PORT, () => { console.log(JSON.stringify({ level: 'info', instance: INSTANCE, msg: `listening ${PORT}` })); initStorage(); });
