# Bảng yêu cầu phi chức năng và chỉ số chấp nhận (bản nháp)

Đề tài 1: Đánh giá và thiết kế lại kiến trúc website thương mại điện tử theo khung Well-Architected.

| Mục | Nội dung |
|---|---|
| Soạn nháp phần ngưỡng | Lê Văn Nhựt, 07/10/2026 |
| Bổ sung cách đo, tiêu chí Pass/Fail, chốt bản cuối | Phan Quang Thoại |
| Trạng thái | Nháp, chờ nhóm chốt. Mọi số trong file là giả định của doanh nghiệp giả định, không phải số đo thực |

Nguyên tắc: ngưỡng được **chốt trước khi có số liệu đo chính thức** và dùng chung cho cả hai kiến trúc. Kiến trúc cơ sở có thể không đạt một số ngưỡng. Đó là phát hiện của thí nghiệm, không phải lỗi của bảng này.

## 1. Giả định nghiệp vụ (nhóm chỉnh nếu cần)

| Mã | Giả định | Giá trị | Lý do |
|---|---|---|---|
| GD-01 | Số phiên truy cập mỗi ngày | 50.000 | Website bán hàng cỡ vừa |
| GD-02 | Số request mỗi phiên | 12 | Xem danh sách, chi tiết, ảnh, giỏ hàng, đặt hàng |
| GD-03 | Tỷ lệ lưu lượng ngày dồn vào giờ cao điểm | 40% trong 3 giờ | Mẫu thường gặp ở bán lẻ trực tuyến |
| GD-04 | Hệ số tăng đột biến so với cao điểm | 3 lần | Giả định cho đợt khuyến mãi |
| GD-05 | Số ngày tính chi phí và sẵn sàng | 30 ngày (720 giờ) | Chu kỳ tháng |

## 2. Lưu lượng dự kiến

| Mức tải | Cách tính | Kết quả |
|---|---|---|
| LOAD-NORMAL | 50.000 × 12 = 600.000 request/ngày; 600.000 ÷ 86.400 giây | **7 req/s** |
| LOAD-PEAK | 600.000 × 40% ÷ (3 × 3.600 giây) = 240.000 ÷ 10.800 | **22 req/s** |
| LOAD-SPIKE | 22,2 × 3 | **67 req/s** |

Nếu ở các mức trên hai kiến trúc không cho khác biệt đo được, nhóm có thể nhân một hệ số mô phỏng chung cho cả ba mức và ghi hệ số đó vào báo cáo như một giả định. Hệ số phải chốt trước khi đo chính thức.

## 3. Bảng yêu cầu và chỉ số chấp nhận

| Mã | Trụ cột | Yêu cầu | Chỉ số | Ngưỡng chấp nhận | Áp dụng cho | Cách đo (Thoại bổ sung) |
|---|---|---|---|---|---|---|
| NFR-01 | Hiệu quả hiệu năng | Phản hồi nhanh | p95 latency | ≤ 300 ms ở LOAD-NORMAL; ≤ 500 ms ở LOAD-PEAK; ≤ 1.000 ms ở LOAD-SPIKE | Cơ sở, Cải tiến | |
| NFR-02 | Hiệu quả hiệu năng | Xử lý đủ lưu lượng | Throughput | ≥ 7 req/s; ≥ 22 req/s; ≥ 67 req/s theo từng mức tải | Cơ sở, Cải tiến | |
| NFR-03 | Độ tin cậy | Ít request lỗi | Error rate | ≤ 0,5% ở LOAD-NORMAL; ≤ 1% ở LOAD-PEAK; ≤ 2% ở LOAD-SPIKE | Cơ sở, Cải tiến | |
| NFR-04 | Độ tin cậy | Chịu lỗi một bản ứng dụng | failover_s | ≤ 10 giây: từ lúc dừng APP02 đến khi LB01 phục vụ ổn định chỉ bằng APP01 | Cải tiến | |
| NFR-05 | Độ tin cậy | Bản sao quay lại sau khi bật | rejoin_s | ≤ 30 giây: từ lúc bật lại APP02 đến khi APP02 nhận request đầu tiên | Cải tiến | |
| NFR-06 | Độ tin cậy | Không mất giao dịch khi một bản sao dừng | Tỷ lệ request lỗi trong sự cố | ≤ 0,1% tổng request; request GET không được lỗi kéo dài | Cải tiến | |
| NFR-07 | Độ tin cậy | Mức sẵn sàng của tầng ứng dụng | Thời gian ngừng dịch vụ mỗi tháng | ≥ 99,5% (tối đa 3,6 giờ ngừng mỗi 720 giờ) | Cải tiến | |
| NFR-08 | Bảo mật | DB và object storage không mở ra ngoài | Kết quả quét cổng | Chỉ LB01 (và cổng giám sát) mở ra máy chủ; DB01, OBJ01 không mở | Cải tiến | |
| NFR-09 | Bảo mật | Không lộ bí mật | Kết quả quét secret | 0 secret trong kho mã, ảnh minh chứng, log | Cơ sở, Cải tiến | |
| NFR-10 | Tối ưu chi phí | Chi phí trong ngân sách | Chi phí tháng ước tính | ≤ 100 USD/tháng khi triển khai đám mây (giả định); chạy thí nghiệm cục bộ 0 đồng | Cơ sở, Cải tiến | |
| NFR-11 | Vận hành | Dựng lại được | Kết quả tái lập | Dựng lại từ kho mã theo README, không chỉnh tay ngoài hướng dẫn | Cơ sở, Cải tiến | |

Giải thích các số chính:
- NFR-04: Nginx cấu hình `proxy_connect_timeout 1s`, `max_fails=2`, `fail_timeout=5s`, nên ngưỡng 10 giây đủ dài hơn thời gian loại bản sao lỗi.
- NFR-05: gồm thời gian khởi động container, khởi tạo ứng dụng và chu kỳ `fail_timeout`.
- NFR-07: 99,5% thay vì 99,9% vì DB01 vẫn là một bản duy nhất (quyết định không triển khai replica trong phạm vi đồ án). 99,9% cho phép khoảng 43 phút ngừng mỗi tháng.

## 4. Việc Thoại bổ sung

- Cột "Cách đo": công cụ, số lần lặp, điều kiện đo, cách lấy từng chỉ số.
- Tiêu chí Pass/Fail cho từng NFR và ánh xạ sang test case trong `Pham_vi_kiem_thu`.
- Đối chiếu ngưỡng NFR-10 với bảng chi phí hai kiến trúc.
