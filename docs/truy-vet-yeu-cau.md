# Bảng truy vết: yêu cầu nghiệp vụ → yêu cầu kiến trúc → quyết định → chỉ số kiểm chứng

Đề tài 1: Đánh giá và thiết kế lại kiến trúc website thương mại điện tử theo khung Well-Architected.
Người phụ trách: Lê Văn Nhựt. Phối hợp: Phan Quang Thoại (bảng NFR), Võ Nhật Linh (ứng dụng, tải).

Nguồn số liệu ngưỡng: `docs/bang-nfr.md` (bản nháp do Nhựt soạn, Thoại bổ sung cách đo và chốt).
Tên thành phần theo sheet `Quy_uoc`: BASE-NODE, LB01, APP01, APP02, DB01, OBJ01, MON01, LOADGEN.

## 1. Bối cảnh nghiệp vụ giả định (nhóm xác nhận)

Website bán hàng cỡ nhỏ chạy trên một máy chủ duy nhất. Chủ cửa hàng cần: bán hàng không gián đoạn giờ cao điểm, không mất đơn hàng, an toàn dữ liệu khách hàng và chi phí hạ tầng nằm trong ngân sách.

| Tham số | Giá trị |
|---|---|
| Lưu lượng dự kiến (bình thường, cao điểm, tăng đột biến) | 7 req/s; 22 req/s; 67 req/s |
| Thời gian đáp ứng mục tiêu (p95) | ≤ 300 ms; ≤ 500 ms; ≤ 1.000 ms (theo ba mức tải) |
| Mức sẵn sàng mục tiêu | ≥ 99,5% mỗi tháng (tầng ứng dụng) |
| Ngân sách tháng | ≤ 100 USD (giả định, khi triển khai đám mây) |

## 2. Bảng truy vết

| Mã | Yêu cầu nghiệp vụ | Yêu cầu kiến trúc (kiểm chứng được) | Trụ cột | Quyết định kiến trúc | Đánh đổi / rủi ro còn lại | Chỉ số và minh chứng |
|---|---|---|---|---|---|---|
| BR-01 | Website vẫn bán hàng khi một bản ứng dụng gặp sự cố | AR-01: không còn điểm lỗi đơn ở tầng ứng dụng; dịch vụ tiếp tục khi một bản sao dừng | Độ tin cậy | LB01 (Nginx) + APP01, APP02; loại bản lỗi bằng `max_fails`, `fail_timeout`, `proxy_next_upstream` | Tốn thêm tài nguyên; request POST đang xử lý lúc bản sao dừng có thể mất (Linh ghi nhận khoảng 0,01% ở lần đo đầu); chỉ kiểm tra bị động | Error rate và recovery time khi FAIL-IMP-01; test case "dừng APP02" |
| BR-02 | Trang phản hồi nhanh giờ cao điểm | AR-02: p95 không vượt 500 ms ở LOAD-PEAK | Hiệu quả hiệu năng | Chia tải qua hai bản sao | LB01 thêm một bước nên độ trễ nền tăng nhẹ | p50, p95, throughput ở LOAD-PEAK, so với BASE-NODE |
| BR-03 | Chịu được lượng truy cập tăng đột ngột | AR-03: error rate không vượt 2% ở LOAD-SPIKE | Hiệu quả hiệu năng, độ tin cậy | Hai bản sao cố định | Không co giãn tự động (ngoài phạm vi đồ án) | Error rate, p95 ở LOAD-SPIKE |
| BR-04 | Không mất đơn hàng và giỏ hàng | AR-04: dữ liệu nằm ở thành phần riêng, lưu bền vững | Độ tin cậy | DB01 tách khỏi ứng dụng, dùng volume `dbdata` | DB01 vẫn là một bản, là SPOF còn lại; chưa có replica và sao lưu (quyết định không triển khai trong phạm vi đồ án) | Test kết nối DB01; dữ liệu còn sau khi khởi động lại ứng dụng |
| BR-05 | Bảo vệ dữ liệu khách hàng và thông tin đăng nhập | AR-05: chỉ LB01 nhận kết nối từ ngoài; DB01 và OBJ01 chỉ nhận kết nối từ tầng ứng dụng; không để secret trong Git | Bảo mật | Chia mạng `frontend` / `backend`; bỏ cổng công khai của DB01, OBJ01; `.env` nằm ngoài Git | Cấu hình phức tạp hơn; chưa có TLS (rủi ro còn lại) | Kết quả quét cổng; quét secret trong repo |
| BR-06 | Ảnh sản phẩm hiển thị ổn định | AR-06: ảnh lưu ở thành phần riêng, không nằm trong ứng dụng | Độ tin cậy, hiệu quả hiệu năng | OBJ01 (MinIO, bản `pgsty/minio`) | Phụ thuộc bản fork cộng đồng vì `minio/minio` không còn tải được; một bản duy nhất | Test tải lên và tải xuống ảnh |
| BR-07 | Chi phí nằm trong ngân sách | AR-07: chi phí tháng của kiến trúc cải tiến không vượt 100 USD (giả định) | Tối ưu chi phí | Dùng phần mềm mã nguồn mở, một DB, hai bản ứng dụng | Không có dự phòng DB để giữ chi phí thấp | Bảng chi phí hai kiến trúc; độ nhạy 2x và 5x |
| BR-08 | Phát hiện sự cố và theo dõi chất lượng dịch vụ | AR-08: có metric và log để dựng lại timeline sự cố | Vận hành | MON01 (Prometheus, Grafana); log LB01 ghi `$upstream_addr` | Chưa có exporter cho Nginx và PostgreSQL | Dashboard; log LB01 trong thí nghiệm lỗi |
| BR-09 | Triển khai lặp lại được, người khác chạy lại cho kết quả như nhau | AR-09: dựng lại từ kho mã bằng script, phiên bản cố định | Vận hành | Docker Compose, script `scripts/`, ghi phiên bản trong `docs/danh-muc-phien-ban.md`, không dùng `latest` | Chạy trên một máy nên không có vùng sẵn sàng thật | Kết quả kiểm tra tái lập của Thoại |

## 3. Quyết định không triển khai trong phạm vi đồ án

| Nội dung | Lý do |
|---|---|
| Replica và sao lưu cho DB01 | Ngoài yêu cầu tối thiểu của Đề tài 1; tăng chi phí và độ phức tạp |
| Co giãn tự động | Đề tài 3 mới yêu cầu; đề tài này dùng số bản sao cố định |
| TLS giữa người dùng và LB01 | Môi trường thử nghiệm trên máy cá nhân; ghi là rủi ro còn lại |
| Nhiều vùng sẵn sàng | Chạy trên một máy nên không mô phỏng được vùng sẵn sàng thật |
| Kiểm tra sức khỏe chủ động (active health check) | Nginx mã nguồn mở chỉ hỗ trợ kiểm tra bị động; chủ động cần Nginx Plus hoặc HAProxy |

## 4. Việc cần chốt

- Xác nhận phiên bản cuối của `nginx.conf` và hai file compose (mạng, giới hạn tài nguyên, thẻ phiên bản) trước khi đo chính thức.
