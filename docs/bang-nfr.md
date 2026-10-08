# BẢNG YÊU CẦU PHI CHỨC NĂNG (NFR) VÀ TIÊU CHÍ CHẤP NHẬN
**Đề tài:** Đánh giá và thiết kế lại kiến trúc website thương mại điện tử theo khung Well-Architected  
**Người phụ trách:** Phan Quang Thoại (SV3) | **Phối hợp & Đối chiếu:** Lê Văn Nhựt (SV1)

---

## 1. Thiết lập Workload và Môi trường đo kiểm
Căn cứ vào script kiểm thử `load/load.js` và `scripts/run-load.sh`, các thông số tải chuẩn được xác định như sau:
* **LOAD-NORMAL (Tải thường):** Target **20 VUs** duy trì trong **2 phút** (Ramp-up 30s, Ramp-down 10s).
* **LOAD-PEAK (Tải cao điểm):** Target **100 VUs** duy trì trong **2 phút** (Ramp-up 30s, Ramp-down 10s).
* **LOAD-SPIKE (Tải đột biến):** Nhảy vọt lên **200 VUs** trong **1 phút** rồi hạ về mức tải nền 20 VUs.
* **Số lần lặp (Repetitions):** Mỗi kịch bản chạy lặp lại **3 lần** (`REPS=3`) trên môi trường sạch sau khi chạy `scripts/reset-data.sh`.
* **Hạn chế đo lường:** Do máy sinh tải `k6` chạy cùng máy vật lý với hệ thống Docker, CPU của máy sinh tải có thể làm độ trễ tăng nhẹ; nhóm ghi nhận yếu tố này vào báo cáo.

---

## 2. Bảng Ma trận NFR và Tiêu chí chấp nhận (SLO)

| Mã NFR | Trụ cột | Hạng mục kiểm thử | Chỉ số đo lường (SLI) | Tiêu chí chấp nhận (SLO) | Công cụ & Kịch bản | Người thực hiện |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NFR-01** | **Hiệu năng** | Tải thông thường (`LOAD-NORMAL`) | • Latency p95<br>• Latency p50<br>• Throughput<br>• Error Rate | • **p95 ≤ 300 ms**<br>• p50 ≤ 100 ms<br>• Throughput ≥ 50 req/s<br>• **Error Rate = 0.00%** | k6 (`load/load.js`), profile `normal` | Linh chạy tải; Thoại trích xuất số liệu. |
| **NFR-02** | **Hiệu năng** | Tải cao điểm (`LOAD-PEAK`) | • Latency p95<br>• Throughput<br>• Error Rate | • **p95 ≤ 800 ms**<br>• Throughput ≥ 150 req/s<br>• **Error Rate ≤ 0.5%** | k6 (`load/load.js`), profile `peak` | Linh chạy tải; Thoại đo và tổng hợp. |
| **NFR-03** | **Độ bền** | Tải đột biến (`LOAD-SPIKE`) | • Tỷ lệ lỗi tức thời<br>• Khả năng tự hồi phục | • **Error Rate ≤ 2.0%**<br>• Trở về ổn định ngay sau khi hết đợt spike | k6 (`load/load.js`), profile `spike` | Linh chạy spike; Thoại ghi nhận. |
| **NFR-04** | **Độ tin cậy** | Chuyển lỗi khi tắt 1 bản sao (`FAIL-IMP-01`) | • Thời gian chuyển tải (`failover_s`)<br>• Thời gian tái nhập (`rejoin_s`)<br>• Error rate trong sự cố | • **failover_s ≤ 7 giây**<br>• **rejoin_s ≤ 10 giây**<br>• Error rate sự cố ≤ 2.0% | Chạy `scripts/fail-imp-01.sh` dừng `app02` | Linh dừng app; Nhựt check LB; Thoại đo. |
| **NFR-05** | **Độ tin cậy** | Hành vi sập nút đơn (`FAIL-BASE-01`) | • Mức độ gián đoạn<br>• Thời gian phục hồi | • Gián đoạn 100% (Downtime)<br>• Cần can thiệp khởi động lại thủ công | Chạy lệnh dừng `app01` trên `BASE-NODE` | Thoại ghi nhận làm cơ sở đối chứng SPOF. |
| **NFR-06** | **Lưu trữ** | Tách dữ liệu tĩnh (Stateless App) | • Tỷ lệ đọc/ghi ảnh thành công<br>• Toàn vẹn sau khởi động lại | • **100%** ảnh truy cập thành công qua MinIO<br>• Ảnh bảo toàn nguyên vẹn sau khi restart app | Gọi `/products/:id/image`; restart container | Linh kiểm thử; Thoại ghi nhận. |
| **NFR-07** | **Bảo mật** | Cô lập mạng & kiểm soát secret | • Số secret bị lộ trong git<br>• Cổng mở Database | • **0** thông tin mật (password/key) trong git<br>• `db01` **không mở cổng Public** ra ngoài | Quét kho mã bằng Trivy/Gitleaks; check compose | Nhựt rà soát; Thoại lập biên bản. |
| **NFR-08** | **Vận hành** | Giám sát & Quan sát (Observability) | • Tần suất lấy mẫu (Scrape interval)<br>• Mức độ bao phủ thành phần | • **Scrape interval ≤ 5 giây**<br>• Giám sát đầy đủ: Nginx, 2 App, PostgreSQL, MinIO | Kiểm tra Prometheus (`monitoring/`) | Thoại dựng Dashboard; Nhựt hỗ trợ exporter. |
| **NFR-09** | **Chi phí** | Ngân sách & Phân tích độ nhạy | • Ngân sách mô phỏng tháng<br>• Phân tích độ nhạy khi tăng tải | • Ngân sách giả định ≤ **50 USD/tháng** (kiến trúc cơ sở) và ≤ **100 USD/tháng** (kiến trúc cải tiến)<br>• Phân tích chi phí khi tải tăng 2x và 5x | AWS Pricing Calculator; lưu `cost/cost-estimate.xlsx` | Thoại tính toán; Nhựt kiểm tra. |
| **NFR-10** | **Độ tin cậy** | Mức sẵn sàng tầng ứng dụng (kiến trúc cải tiến) | • Mức sẵn sàng ước tính mỗi tháng | • **≥ 99.5%/tháng** (tối đa 3,6 giờ ngừng trong 720 giờ)<br>• Tính từ `failover_s` đo được ở NFR-04 và số sự cố giả định mỗi tháng, ghi giả định trong báo cáo | Tính toán từ số liệu NFR-04 | Nhựt đề xuất ngưỡng; Thoại tính toán. |

---

## 3. Quy ước file kết quả đầu ra
Toàn bộ số liệu thực nghiệm sau khi chạy `scripts/run-load.sh` sẽ được Thoại tổng hợp vào thư mục `data/summary/`:
* `data/summary/latency_p50.csv`
* `data/summary/latency_p95.csv`
* `data/summary/throughput.csv`
* `data/summary/error_rate.csv`
* `data/summary/recovery_time.csv`
