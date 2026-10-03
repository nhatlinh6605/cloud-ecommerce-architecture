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
