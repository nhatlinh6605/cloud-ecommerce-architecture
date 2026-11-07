# Hạ tầng dưới dạng mã (IaC) và hướng dẫn dọn tài nguyên

- Người thực hiện: Lê Văn Nhựt
- Phạm vi: dòng 12 – chuẩn hóa cấu hình triển khai và hướng dẫn dọn tài nguyên
- Ngày cập nhật: 05/11/2026

## 1. Lựa chọn công cụ IaC

Hạ tầng của kiến trúc cải tiến được mô tả bằng **Docker Compose** ở file `docker-compose.improved.yml` (mô hình khai báo: mô tả trạng thái mong muốn, Compose tự tạo hoặc cập nhật cho khớp).

Không dùng Terraform hoặc OpenTofu vì đồ án chạy hoàn toàn trên máy cá nhân bằng Docker, không có tài nguyên cloud thật cần quản lý. Do đó dự án không có file trạng thái (`*.tfstate`) nào. Nếu sau này chuyển sang Terraform thì các file state và biến đã được chặn sẵn trong `.gitignore`.

## 2. Thành phần triển khai

Tên project Compose là `improved`, nên tài nguyên có tiền tố `improved-` (container, image) hoặc `improved_` (volume, mạng).

| Service | Image | Mạng | Cổng mở ra máy host |
|---|---|---|---|
| lb01 | `nginx:1.27-alpine` | frontend | `8080` |
| app01, app02 | build từ `./app` (Node 20 Alpine) | frontend, backend, monitoring | không |
| db01 | `postgres:16-alpine` | backend | không |
| obj01 | `pgsty/minio@sha256:b6bfe723…2372` (ghim digest) | backend | không |
| prometheus | `prom/prometheus:v2.52.0` | monitoring | `127.0.0.1:9090` |
| grafana | `grafana/grafana:11.0.0` | monitoring | `127.0.0.1:3001` |

Mạng `backend` đặt `internal: true` nên `db01` và `obj01` không ra được Internet. Mỗi service giới hạn 512 MiB RAM và có `restart: unless-stopped`.

Volume dữ liệu: `improved_dbdata` (Postgres) và `improved_objdata` (MinIO).

## 3. Cấu hình và bí mật

| Mục | Quy định |
|---|---|
| File mẫu | `.env.example` (chỉ chứa giá trị giữ chỗ, được commit) |
| File thật | `.env` (chứa mật khẩu, **không commit**, đã nằm trong `.gitignore`) |
| State IaC | không có; `*.tfstate`, `.terraform/`, `*.tfvars` đã chặn sẵn |
| Mật khẩu Grafana | lấy từ `GRAFANA_ADMIN_PASSWORD`, thiếu biến thì Compose báo lỗi và không khởi động |

Kết quả kiểm tra ngày 05/11/2026:

- `git ls-files | findstr /i "\.env tfstate"` chỉ trả về `.env.example`.
- `git log --all --oneline -- .env` không có kết quả, tức `.env` chưa từng bị commit.

**Lưu ý khi điền `.env`:** tắt bộ gõ tiếng Việt và chỉ dùng chữ không dấu, số. Bộ gõ Telex biến `dd` thành `đ`, ký tự này làm hỏng khóa MinIO. Kiểm tra bằng lệnh sau, kết quả chỉ nên còn dòng chú thích:

```
Select-String -Path .env -Pattern '[^\x00-\x7F]' | ForEach-Object { "$($_.LineNumber): " + ($_.Line -split '=')[0] }
```

## 4. Triển khai

Chạy trong PowerShell tại thư mục gốc của repo:

```
copy .env.example .env
notepad .env
docker compose -f docker-compose.improved.yml config -q
docker compose -f docker-compose.improved.yml up -d --build
docker compose -f docker-compose.improved.yml ps
curl.exe http://localhost:8080/health
```

Bước `copy` chỉ chạy khi chưa có `.env` (lệnh sẽ ghi đè file cũ). Kết quả mong đợi: `app01`, `app02`, `db01`, `lb01` ở trạng thái `(healthy)`, và `/health` trả `{"status":"ok","instance":"app01"}` hoặc `app02`.

| Giao diện | Địa chỉ |
|---|---|
| Ứng dụng qua load balancer | http://localhost:8080 |
| Prometheus | http://127.0.0.1:9090 |
| Grafana | http://127.0.0.1:3001 |

## 5. Dọn tài nguyên

Có 3 mức. Chạy bằng script (xác nhận trước khi xóa dữ liệu) hoặc gõ lệnh trực tiếp.

| Mức | Việc làm | Dữ liệu |
|---|---|---|
| 1 | Dừng, xóa container và mạng | **giữ** DB và ảnh sản phẩm |
| 2 | Mức 1 + xóa volume `improved_dbdata`, `improved_objdata` | **mất** DB và ảnh sản phẩm |
| 3 | Mức 2 + xóa image build `improved-app01`, `improved-app02` | **mất** toàn bộ |

Dùng script (tại thư mục gốc của repo):

```
powershell -ExecutionPolicy Bypass -File infra\cleanup.ps1 -Level 1
powershell -ExecutionPolicy Bypass -File infra\cleanup.ps1 -Level 2
powershell -ExecutionPolicy Bypass -File infra\cleanup.ps1 -Level 3
```

Mức 2 và 3 yêu cầu gõ `YES` để xác nhận. Script chạy xong sẽ tự in danh sách tài nguyên còn sót.

Hoặc gõ lệnh trực tiếp:

```
docker compose -f docker-compose.improved.yml down
docker compose -f docker-compose.improved.yml down -v
docker compose -f docker-compose.improved.yml down -v --rmi local
```

Kiểm tra không còn sót tài nguyên:

```
docker ps -a --filter "name=improved-"
docker volume ls --filter "name=improved_"
docker network ls --filter "name=improved_"
docker images "improved-*"
```

Kết quả mong đợi của bốn lệnh trên sau từng mức:

| Sau mức | Container | Mạng | Volume | Image |
|---|---|---|---|---|
| 1 | trống | trống | còn `improved_dbdata`, `improved_objdata` | còn `improved-app01`, `improved-app02` |
| 2 | trống | trống | trống | còn |
| 3 | trống | trống | trống | trống |

Nếu lệnh `docker network ls` vẫn hiện mạng `improved_default` thì đó là mạng sót từ lần chạy thử bằng `docker compose run` (mạng này không còn nằm trong file compose nên `down` không xóa). Xóa bằng `docker network rm improved_default`.

Không dùng `docker system prune -a` vì lệnh này xóa cả tài nguyên của các project Docker khác trên máy.

## 6. Lỗi thường gặp đã gặp khi thực hiện

| Triệu chứng trong log | Nguyên nhân | Cách xử lý |
|---|---|---|
| `initStorage retry: Invalid character in header content ["authorization"]` | `MINIO_ACCESS_KEY` hoặc `MINIO_SECRET_KEY` có ký tự không phải ASCII (ví dụ `Đ`) | Gõ lại khóa với bộ gõ tắt, rồi `up -d --force-recreate obj01 app01 app02` |
| `initStorage retry: password authentication failed for user "shop"` | `DB_PASSWORD` trong `.env` khác mật khẩu đã lưu trong volume `dbdata` (Postgres chỉ nhận mật khẩu lúc tạo volume) | Đặt lại mật khẩu bằng `ALTER USER shop PASSWORD '…'`, hoặc dọn mức 2 rồi triển khai lại |
| `host not found in upstream "app02:3000"` khi nạp cấu hình `lb01` | Một bản sao đang dừng đúng lúc `lb01` khởi động hoặc reload | Bật đủ `app01`, `app02` trước, rồi reload `lb01` |
| `lb01` không khởi động, báo thiếu `GRAFANA_ADMIN_PASSWORD` | `.env` chưa có biến này | Thêm biến vào `.env` |
