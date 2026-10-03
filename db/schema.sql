CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY, name TEXT NOT NULL, description TEXT,
  price NUMERIC(12,2) NOT NULL, image_key TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cart_items (
  session_id TEXT NOT NULL, product_id INT NOT NULL REFERENCES products(id),
  qty INT NOT NULL CHECK (qty > 0), PRIMARY KEY (session_id, product_id));
CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY, session_id TEXT NOT NULL, total NUMERIC(14,2) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now());
