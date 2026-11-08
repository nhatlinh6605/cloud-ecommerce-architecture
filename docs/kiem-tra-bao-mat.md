# Biên bản kiểm tra bảo mật (NFR-07, TC-SEC-01)

Ngày kiểm tra: 08/11/2026. Người thực hiện: Võ Nhật Linh. Phạm vi: kiến trúc cơ sở và kiến trúc cải tiến.

## 1. Cổng mở

Kiểm tra bằng `docker ps` (kiến trúc cơ sở đang chạy) và đọc `ports:` trong hai file compose.

| Kiến trúc | Thành phần | Cổng | Đánh giá |
|---|---|---|---|
| Cơ sở | app01 | 0.0.0.0:8080 | Cổng vào duy nhất, đúng thiết kế |
| Cơ sở | db01, obj01 | chỉ cổng nội bộ (5432, 9000) | Không mở ra máy chủ, đạt |
| Cơ sở | prometheus | 127.0.0.1:9090 | Chỉ máy cục bộ |
| Cải tiến | lb01 | 8080:80 | Cổng vào duy nhất, đúng thiết kế |
| Cải tiến | prometheus, grafana | 127.0.0.1:9090, 127.0.0.1:3001 | Chỉ máy cục bộ |
| Cải tiến | app01, app02, db01, obj01 | không khai báo `ports:` | Không mở cổng, đạt |

Kết luận: db01 và obj01 không mở cổng ra ngoài ở cả hai kiến trúc.

## 2. Secret trong mã nguồn hiện tại

Lệnh: `git grep -n -iE "password|secret|token|api[_-]?key"` (loại trừ docs và file .example).
Kết quả: mọi dòng khớp chỉ là tên biến hoặc tham chiếu biến môi trường (`process.env.*`, `${...}`). Không có giá trị bí mật nào được ghi cứng. `.env.example` chỉ chứa giá trị giữ chỗ (`__DAT_MAT_KHAU__`...). Grafana bắt buộc có biến `GRAFANA_ADMIN_PASSWORD`, thiếu thì Compose không khởi động.

## 3. Secret trong lịch sử Git

- `git log --all -- .env`: không có commit nào, `.env` chưa từng được đưa lên Git (đã nằm trong `.gitignore`).
- `git log --all -S` với hai mật khẩu đang dùng trên máy: không có commit nào.
- Gitleaks 8.30.1 (`gitleaks detect --source .`): quét 27 commit, kết quả `no leaks found`.

## 4. Rủi ro còn lại

1. Cổng vào 8080 bind trên 0.0.0.0, thiết bị cùng mạng có thể truy cập. Chấp nhận với thực nghiệm cục bộ.
2. Chưa có TLS giữa người dùng và hệ thống (đã ghi nhận trong `docs/truy-vet-yeu-cau.md`).
3. Mật khẩu mẫu dùng trên máy thực nghiệm là dạng dễ đoán. Cần đặt mật khẩu mạnh và quản lý bằng kho bí mật khi triển khai thật.
4. Tài khoản DB `shop` có quyền Superuser (kiểm tra bằng `\du` trên db01). Đây là mặc định của image Postgres khi dùng `POSTGRES_USER`. Chưa đạt quyền tối thiểu. Hướng khắc phục: tạo role riêng chỉ có quyền trên schema của ứng dụng, dành `shop` cho quản trị.
5. Tiến trình ứng dụng chạy bằng root trong container (`docker exec app01 id` trả về `uid=0`). Hướng khắc phục: thêm `USER node` vào `app/Dockerfile`.
6. Chưa quét lỗ hổng image (ví dụ Trivy).

## 5. Truy cập DB và object storage

db01 và obj01 không mở cổng ra máy chủ ở cả hai kiến trúc (mục 1), nên chỉ tầng ứng dụng truy cập được qua mạng nội bộ. Chưa kiểm tra riêng chính sách bucket của MinIO.
