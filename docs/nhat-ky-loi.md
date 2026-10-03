# Nhật ký lỗi (FAIL-IMP / sự cố triển khai)

Mỗi lỗi liên kết với một Git issue/commit. Báo Nhựt/Thoại nếu lỗi ảnh hưởng số liệu đo.

| #   | Ngày       | Hiện tượng                                                                    | Nguyên nhân                                                          | Cách khắc phục                                                       | Issue/Commit                    | Ảnh hưởng số liệu?                       |
| --- | ---------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------- | ---------------------------------------- |
| 1   | 03/10/2026 | `docker compose up` báo "pull access denied" với minio/minio; quay.io trả 401 | MinIO không còn phát hành image công khai trên Docker Hub và Quay.io | Đổi sang pgsty/minio:latest (cùng lệnh khởi động và biến môi trường) | (điền mã commit sau khi commit) | Không (chỉ đổi image, API S3 giữ nguyên) |
