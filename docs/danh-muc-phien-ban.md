# Danh mục phiên bản

| Thành phần                         | Phiên bản                                                                                                                 |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Node.js                            | 20 (alpine)                                                                                                               |
| express / pg / minio / prom-client | 4.19.2 / 8.11.5 / 7.1.3 / 15.1.2                                                                                          |
| PostgreSQL                         | 16-alpine                                                                                                                 |
| MinIO (object storage)             | pgsty/minio:latest, tạo ngày 2026-08-04, image ID sha256:b6bfe7239bfc83fb90d31612d9704d86039dd714f7904b3f1ad68f211e602372 |
| Nginx                              | 1.27-alpine                                                                                                               |
| Prometheus / Grafana               | v2.52.0 / 11.0.0                                                                                                          |
| k6                                 | ≥ 0.50 (ghi phiên bản thực tế khi chạy)                                                                                   |
| Docker Compose                     | v5.1.2                                                                                                                    |
| Docker Engine                      | 29.4.0                                                                                                                    |

Ghi chú: image `minio/minio` chính thức không còn tải được (xem `nhat-ky-loi.md`, lỗi #1), nên nhóm dùng bản fork `pgsty/minio`.


## Môi trường chạy của Nhựt

Cập nhật 09/10/2026. Máy này dùng để rà soát hạ tầng và chạy thử. Số liệu đo chính thức chỉ lấy trên một máy đã chốt và ghi rõ cấu hình máy đó.

| Hạng mục | Giá trị |
|---|---|
| Hệ điều hành | Windows 11 Home 26H2 (OS build 26300.9550) |
| CPU | Intel Core i5-12500H, 12 nhân / 16 luồng, bật ảo hóa |
| RAM | 16 GB DDR4 |
| Ổ đĩa | SSD NVMe 477 GB; dữ liệu Docker lưu ở `D:\WSL` |
| Giới hạn cấp cho WSL2 (`.wslconfig`) | `memory=8GB`, `processors=8` |
| Docker thấy được | 8 CPU, 7,758 GiB RAM (theo `docker info`) |

| Công cụ | Phiên bản trên máy Nhựt | Ghi chú |
|---|---|---|
| Docker Desktop | v4.94.0 | Backend WSL 2 |
| Docker Engine | 29.8.2 | |
| Docker Compose | v5.5.1 | |
| WSL | 3.0.1.0 (kernel 6.18.40.1-1) | |
| Git | 2.53.0.windows.2 | |
| draw.io | v32.3.0 (bản web) | Vẽ sơ đồ kiến trúc |
| k6 | _điền sau khi cài_ | Cài khi cần chạy tải trên máy này |

Lưu ý: Docker Engine và Docker Compose ở bảng phía trên khác bản ở máy Nhựt. Nhóm chốt một máy đo chính thức và ghi phiên bản của máy đó.

## Ngân sách và cảnh báo chi phí

| Hạng mục | Nội dung |
|---|---|
| Chi phí thực tế | 0 đồng: toàn bộ thí nghiệm chạy cục bộ bằng Docker, không dùng tài nguyên đám mây có phí |
| Trần ngân sách giả định (NFR-09) | ≤ 50 USD/tháng (kiến trúc cơ sở); ≤ 100 USD/tháng (kiến trúc cải tiến) khi triển khai trên đám mây. Chỉ dùng để ước tính chi phí, không phát sinh khoản thu thật |
| Nếu dùng tài nguyên có phí | Đặt ngân sách và bật cảnh báo chi phí trước khi tạo; xóa tài nguyên ngay sau mỗi lần thử |
| Dọn tài nguyên cục bộ | `bash scripts/down.sh --purge` xóa container và dữ liệu |
