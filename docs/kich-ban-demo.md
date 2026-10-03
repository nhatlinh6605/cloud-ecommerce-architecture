# Kịch bản demo & video (8–12 phút)
Người tham gia: Linh (thao tác), Nhựt (kiến trúc/LB), Thoại (số liệu). Quay màn hình có hiển thị đồng hồ/terminal; ảnh chụp không thay thế log/số liệu.

| Phút | Nội dung | Thao tác / lệnh | Người nói |
|---|---|---|---|
| 0:00–1:00 | Giới thiệu đề tài, hai kiến trúc | Mở sơ đồ kiến trúc | Nhựt |
| 1:00–2:30 | Kiến trúc cơ sở chạy bình thường | `bash scripts/base-up.sh`; duyệt `/products`, ảnh, đặt hàng | Linh |
| 2:30–4:00 | Chạy tải cơ sở | `PROFILE=normal k6 run load/load.js`; mở Grafana/Prometheus | Linh, Thoại |
| 4:00–5:30 | Kiến trúc cải tiến + LB | `bash scripts/improved-up.sh`; gọi `/health` nhiều lần, thấy `X-Instance` xen kẽ app01/app02 | Nhựt, Linh |
| 5:30–8:30 | **Lỗi – phục hồi (FAIL-IMP-01)** | `bash scripts/fail-imp-01.sh`: dừng APP02 khi có tải → chỉ còn app01 phục vụ → bật lại → xen kẽ trở lại | Linh, Nhựt |
| 8:30–10:00 | Số liệu so sánh p95, error rate, recovery time | Mở bảng kết quả / biểu đồ | Thoại |
| 10:00–11:00 | Kết luận, hạn chế | — | Cả nhóm |

Checklist trước khi quay: `.env` đã điền; `docker compose pull` xong; `k6 version`; dọn `results/`; đóng thông báo hệ thống; chạy thử một lượt.
