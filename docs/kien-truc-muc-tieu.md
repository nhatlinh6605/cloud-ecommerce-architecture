# Thiết kế kiến trúc mục tiêu và các đánh đổi (bản nháp)

Đề tài 1: Đánh giá và thiết kế lại kiến trúc website thương mại điện tử theo khung Well-Architected.
Người phụ trách: Lê Văn Nhựt. Phối hợp: Phan Quang Thoại (phản biện chỉ số đo được), Võ Nhật Linh (cấu hình và mã hiện có).

Tài liệu liên quan: `docs/phan-tich-hien-trang.md`, `docs/truy-vet-yeu-cau.md`, `docs/bang-nfr.md`, sơ đồ trong `docs/so-do/`.
Đánh giá đầy đủ theo từng trụ cột nằm ở `docs/ma-tran-tru-cot.md` (làm riêng).

## 1. Mục tiêu thiết kế

Trả lời câu hỏi nghiên cứu: một website ba tầng đang chạy trên một nút cần thay đổi thế nào để đáp ứng đồng thời sẵn sàng, bảo mật, hiệu năng và chi phí. Nguyên tắc: thay đổi tối thiểu cần thiết, mỗi thay đổi truy vết được về một yêu cầu trong `docs/truy-vet-yeu-cau.md` và có chỉ số kiểm chứng trong `docs/bang-nfr.md`.

## 2. Thành phần của kiến trúc mục tiêu

| Thành phần | Công nghệ | Số bản | Mạng | Cổng mở ra máy chủ |
|---|---|---|---|---|
| LB01 (`lb01`) | Nginx 1.27-alpine | 1 | frontend | 8080 |
| APP01, APP02 (`app01`, `app02`) | Node.js 20-alpine | 2 | frontend, backend, monitoring | không |
| DB01 (`db01`) | PostgreSQL 16-alpine | 1 | backend | không |
| OBJ01 (`obj01`) | MinIO (`pgsty/minio`) | 1 | backend | không |
| MON01 (`prometheus`, `grafana`) | Prometheus v2.52.0, Grafana 11.0.0 | 1 mỗi loại | monitoring | 127.0.0.1:9090 và 127.0.0.1:3001 |

Giới hạn tài nguyên: các dịch vụ dùng chung giá trị với kiến trúc cơ sở (xem `docker-compose.base.yml`). `lb01` và `grafana` là thành phần mới, giá trị đề xuất: `lb01` 0,5 CPU và 128 MB; `grafana` 0,5 CPU và 256 MB.

## 3. Quyết định thiết kế và đánh đổi

| Mã | Quyết định | Lợi ích | Đánh đổi và rủi ro còn lại | Yêu cầu liên quan |
|---|---|---|---|---|
| D1 | LB01 là điểm vào duy nhất, chia tải vòng tròn | Ẩn ứng dụng khỏi người dùng, chia tải, tách bản lỗi | Thêm một bước trên đường đi nên độ trễ nền tăng nhẹ; LB01 chỉ một bản nên trở thành điểm lỗi đơn mới | BR-01, BR-02, NFR-01, NFR-02 |
| D2 | Hai bản ứng dụng không giữ trạng thái | Chịu lỗi một bản, mở rộng ngang | Tốn gấp đôi tài nguyên tầng ứng dụng. Không giữ trạng thái vì giỏ hàng và đơn hàng đã nằm trong DB01, nên không cần dính phiên | BR-01, BR-03, NFR-04 |
| D3 | Loại bản lỗi bằng kiểm tra bị động của Nginx (`max_fails=2`, `fail_timeout=5s`, `proxy_next_upstream`) | Không cần phần mềm trả phí | Lỗi chỉ lộ ra khi có request thật; request POST đã gửi tới bản đã dừng không được tự gửi lại nên có thể mất hoặc trùng đơn (ứng dụng chưa có khóa chống trùng) | BR-01, NFR-04 |
| D4 | Tách DB01 khỏi ứng dụng, dùng volume bền vững | Dữ liệu độc lập với vòng đời ứng dụng | DB01 vẫn một bản, là điểm lỗi đơn; chưa có replica và sao lưu | BR-04 |
| D5 | Tách ảnh sản phẩm sang OBJ01 | Ứng dụng không giữ tệp; thay thế hoặc mở rộng lưu trữ độc lập | Phụ thuộc bản fork cộng đồng `pgsty/minio` (`minio/minio` không còn tải được); chưa ghim phiên bản; một bản duy nhất | BR-06, NFR-06 |
| D6 | Chia ba mạng: frontend, backend, monitoring | LB01 không có đường tới DB01 và OBJ01; giảm bề mặt tấn công | Cấu hình phức tạp hơn; app01 và app02 nằm trong cả ba mạng | BR-05, NFR-07 |
| D7 | Chỉ LB01 mở cổng ra mạng; Prometheus và Grafana chỉ mở trên 127.0.0.1 | Không lộ giao diện giám sát ra mạng LAN | Chỉ xem dashboard được từ chính máy chủ | BR-05, NFR-07 |
| D8 | Giới hạn CPU và RAM cho từng dịch vụ, dùng giá trị chung với kiến trúc cơ sở | Phép so sánh công bằng, tái lập được | Có thể bị giới hạn hoặc OOM khi tải đột biến; cần theo dõi bằng `docker stats` khi đo | BR-09, NFR-11 |
| D9 | Healthcheck cho ứng dụng; ứng dụng chỉ khởi động sau khi DB01 healthy | Khởi động đúng thứ tự, phát hiện container hỏng | Thời gian khởi động dài thêm vài giây. `/health` chỉ kiểm tra DB01, không kiểm tra OBJ01 | BR-01, BR-09 |
| D10 | Prometheus thu `/metrics` của hai ứng dụng mỗi 5 giây, Grafana hiển thị | Có số liệu để đo p50, p95, error rate và dựng timeline sự cố | Chưa có exporter cho Nginx, PostgreSQL, MinIO nên chưa đạt phần bao phủ của NFR-08 | BR-08, NFR-08 |

## 4. Ranh giới tin cậy và trách nhiệm quản trị

- Ranh giới 1: giữa Internet/LAN và máy chủ. Điểm đi qua duy nhất là LB01 cổng 8080.
- Ranh giới 2: giữa tầng truy cập (frontend) và tầng dữ liệu (backend). LB01 không có đường tới DB01 và OBJ01; chỉ APP01, APP02 nối cả hai tầng.
- Trách nhiệm quản trị: nhóm tự quản trị toàn bộ (hệ điều hành, Docker, ứng dụng, cơ sở dữ liệu, sao lưu), không dùng dịch vụ được quản lý.

## 5. Điểm lỗi đơn còn lại

| Thành phần | Hậu quả khi lỗi | Ghi chú |
|---|---|---|
| Máy chủ đơn | Toàn bộ dịch vụ ngừng | Chạy trên một máy nên không có vùng sẵn sàng thật |
| LB01 | Không ai vào được website | Có thể giảm bằng cách chạy hai bản LB; ngoài phạm vi đồ án |
| DB01 | Mất sản phẩm, giỏ hàng, đơn hàng | Replica và sao lưu thuộc nhóm "không triển khai" |
| OBJ01 | Không hiển thị ảnh | Một bản duy nhất |

## 6. Việc cần làm trong cấu hình (việc thiết kế hạ tầng triển khai cải tiến)

- Thêm ba mạng vào `docker-compose.improved.yml` và gán mạng cho từng dịch vụ.
- Thêm giới hạn tài nguyên, healthcheck, `depends_on` có điều kiện cho `app01`, `app02`.
- Đổi cổng Prometheus và Grafana thành `127.0.0.1`.
- Ghim phiên bản MinIO bằng digest.
- Xem lại `nginx.conf` (định dạng log có `$upstream_addr`, `proxy_read_timeout`).
