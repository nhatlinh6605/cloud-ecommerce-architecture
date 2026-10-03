-- Dữ liệu tổng hợp, chạy lại được (reset)
TRUNCATE orders, cart_items, products RESTART IDENTITY CASCADE;
INSERT INTO products(name, description, price, image_key)
SELECT 'Sản phẩm ' || g, 'Mô tả tổng hợp cho sản phẩm ' || g,
       (10000 + (g * 7919) % 490000), 'product-' || g || '.svg'
FROM generate_series(1, 50) g;
