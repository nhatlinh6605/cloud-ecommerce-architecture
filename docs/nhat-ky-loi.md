# Nhật ký lỗi (FAIL-IMP / sự cố triển khai)

Mỗi lỗi liên kết với một Git issue/commit. Báo Nhựt/Thoại nếu lỗi ảnh hưởng số liệu đo.

| # | Ngày | Hiện tượng | Nguyên nhân | Cách khắc phục | Issue/Commit | Ảnh hưởng số liệu? |
|---|---|---|---|---|---|---|
| 1 | 03/10/2026 | `docker compose up` báo "pull access denied" với minio/minio; quay.io trả 401 | MinIO không còn phát hành image công khai trên Docker Hub và Quay.io | Đổi sang pgsty/minio:latest (cùng lệnh khởi động và biến môi trường) | 470a4b8 | Không (chỉ đổi image, API S3 giữ nguyên) |
| 2 | 04/10/2026 | fail-imp-01.sh báo "date: invalid argument 's' for -I", log thiếu mốc thời gian | macOS dùng date của BSD, không hỗ trợ tùy chọn -Is | Đổi sang date +%Y-%m-%dT%H:%M:%S%z | 276efc8 | Có thể: lần chạy cũ không có mốc giờ nên phải chạy lại |
| 3 | 04/10/2026 | fail-imp-01.sh không đo được thời điểm APP02 nhận lại request | Vòng chờ gọi /health qua LB nên thành công ngay nhờ APP01 | Chờ đến khi header X-Instance: app02 xuất hiện lại | add0bf3 | Không (chỉ thêm mốc đo; recovery time lần đo đầu là 6 giây) |
