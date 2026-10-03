# Topic 1 – Cloud: Ứng dụng TMĐT mẫu, kiến trúc cơ sở và cải tiến

Phần của Võ Nhật Linh: ứng dụng, CSDL, script vận hành, workload/tải, kịch bản lỗi, tích hợp, Git, lý thuyết phần B, demo.

## Yêu cầu
Docker + Docker Compose v2, curl, [k6](https://k6.io/docs/get-started/installation/), Git.

## Chạy nhanh
```bash
cp .env.example .env        # điền mật khẩu/khóa của riêng nhóm (không commit .env)
bash scripts/base-up.sh     # kiến trúc cơ sở: app01 + db01 + obj01 + prometheus
curl localhost:8080/health
bash scripts/improved-up.sh # kiến trúc cải tiến: lb01 + app01/app02 + db01 + obj01 + prometheus + grafana
bash scripts/down.sh        # dừng; thêm --purge để xóa dữ liệu
```

## API
| Endpoint | Mô tả |
|---|---|
| GET /products, /products/:id | Danh sách / chi tiết sản phẩm |
| GET /products/:id/image | Ảnh sản phẩm (lấy từ MinIO OBJ01) |
| POST /cart/:sid/items `{product_id, qty}` · GET /cart/:sid | Giỏ hàng |
| POST /orders `{session_id}` | Đặt hàng |
| GET /health | 200 khi kết nối được DB, 503 nếu không |
| GET /metrics | Prometheus: `http_request_duration_seconds`, `orders_created_total`, metrics tiến trình |

Mọi response có header `X-Instance` (app01/app02) để kiểm tra LB phân phối.

## Dữ liệu
`db/schema.sql` tạo bảng, `db/seed.sql` nạp 50 sản phẩm tổng hợp. Reset: `bash scripts/reset-data.sh [base|improved]` (chạy lại bao nhiêu lần cũng cho cùng kết quả).

## Chạy thí nghiệm
```bash
bash scripts/base-up.sh     && bash scripts/run-load.sh baseline 3
bash scripts/improved-up.sh && bash scripts/run-load.sh improved 3
bash scripts/fail-imp-01.sh          # dừng APP02 khi có tải rồi bật lại (kiến trúc cải tiến)
```
Kết quả thô nằm trong `results/` (đã gitignore; nộp kèm minh chứng riêng). Cùng một `load/load.js` cho cả hai kiến trúc.
**Lưu ý:** VUs/thời lượng trong `load/load.js` là giá trị tạm, cần thay bằng tham số trong bảng NFR của Thoại.

## Danh mục phiên bản
Xem `docs/danh-muc-phien-ban.md`. Bảo mật: không đưa secret vào Git; chỉ commit `.env.example`.
