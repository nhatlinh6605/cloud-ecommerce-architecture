# 4.5 Phân tích TCO và Độ nhạy chi phí (Cost Optimization)

## 1. Ước tính chi phí vận hành hàng tháng (Bảng 4.4)

### a. Giả định tính toán
- **Khu vực triển khai:** AWS Region Singapore (`ap-southeast-1`), mô hình On-Demand, tính cho 730 giờ/tháng.
- **Bản quyền phần mềm:** **$0** do toàn bộ hệ thống sử dụng phần mềm nguồn mở (Node.js, PostgreSQL, MinIO, Nginx, Prometheus, Grafana).
- **Lưu lượng mạng:** Trung bình 100 GB dữ liệu ra ngoài Internet (Outbound Data Transfer) mỗi tháng.

### b. Bảng so sánh chi phí cơ sở (Baseline TCO)
| Thành phần | Cấu hình & Dịch vụ | Kiến trúc cơ sở (Base) | Kiến trúc cải tiến (Improved) | Chênh lệch ($) |
| :--- | :--- | :--- | :--- | :--- |
| **Compute (App Tier)** | `t3.medium` (2 vCPU, 4GB RAM) | 1 instance: **$30.37** | 2 instances: **$60.74** | +$30.37 |
| **Load Balancer** | Nginx Reverse Proxy (`t3.micro`) | Không có ($0.00) | 1 instance: **$7.59** | +$7.59 |
| **Database** | PostgreSQL RDS (`db.t3.medium`) | **$50.40** | **$50.40** | $0.00 |
| **Object Storage** | MinIO / S3 Standard (50GB + I/O) | Không có ($0.00) | **$1.35** | +$1.35 |
| **Monitoring** | Prometheus & Grafana (`t3.small`)| Không có ($0.00) | **$15.18** | +$15.18 |
| **Data Transfer** | Outbound Internet (100GB) | **$9.00** | **$9.00** | $0.00 |
| **TỔNG CỘNG HÀNG THÁNG** | | **$89.77/tháng** | **$144.26/tháng** | **+$54.49 (+60.7%)** |

### c. Đánh giá kỹ thuật - kinh tế
Dù chi phí cơ sở tăng thêm **$54.49/tháng** (+60.7%), khoản đầu tư này giải quyết trọn vẹn các rủi ro vận hành:
1. **Loại bỏ SPOF (Single Point of Failure):** Hạ tầng sẵn sàng cao (High Availability), tự động chuyển tải khi một node sập với $RTO = 8.0\text{s}$ (đáp ứng tiêu chuẩn NFR-02), trong khi kiến trúc cơ sở yêu cầu can thiệp thủ công từ 15–30 phút.
2. **Cải thiện độ trễ tải đột biến:** Giảm $25.16\%$ độ trễ p95 ở kịch bản Spike (từ 125.61 ms xuống 94.01 ms).
3. **Khả năng quan sát (Observability):** Có sẵn cụm Prometheus/Grafana để theo dõi số liệu và xử lý sự cố chủ động.

---

## 2. Phân tích độ nhạy chi phí theo kịch bản tăng trưởng (Bảng 4.5)

Khi lưu lượng truy cập tăng trưởng gấp 2 lần (2x) và gấp 5 lần (5x), hai kiến trúc tiếp cận bài toán mở rộng theo hai chiến lược khác nhau:
- **Kiến trúc cơ sở (Scale-up / Mở rộng dọc):** Phải nâng cấp cấu hình máy chủ đơn lên các gói lớn hơn (`t3.large`, `t3.2xlarge`). Chiến lược này gây lãng phí năng lực phần cứng dư thừa và tiềm ẩn rủi ro gián đoạn dịch vụ (downtime) khi thay đổi instance type.
- **Kiến trúc cải tiến (Scale-out / Mở rộng ngang):** Giữ nguyên cấu hình chuẩn (`t3.medium`) và chỉ bổ sung bản sao container/instance đằng sau Nginx Load Balancer mà không làm gián đoạn hệ thống.

### Bảng phân tích độ nhạy chi phí:
| Kịch bản lưu lượng | Kiến trúc cơ sở (Scale-up) | Kiến trúc cải tiến (Scale-out) | Chênh lệch ($) | Phân tích & Đánh giá |
| :--- | :--- | :--- | :--- | :--- |
| **Hiện tại (1x)** | **$89.77** | **$144.26** | +$54.49 | Đầu tư chi phí ban đầu cho tính sẵn sàng cao (HA) và giám sát. |
| **Tăng trưởng 2x** | **$150.51** *(t3.xlarge)* | **$174.63** *(Thêm 1 app node)*| +$24.12 | Khoảng cách chi phí thu hẹp từ +60.7% xuống chỉ còn +16.0%. |
| **Tăng trưởng 5x** | **$332.73** *(t3.2xlarge + RDS)*| **$265.74** *(4x app nodes + RDS)*| **-$66.99 (Rẻ hơn 20.1%)** | **Điểm vượt trội kinh tế:** Scale-out rẻ hơn 20.1% nhờ tối ưu kích thước tài nguyên (Right-sizing), không trả tiền cho tài nguyên nhàn rỗi. |

### Kết luận
Kiến trúc cải tiến chứng minh hiệu quả kinh tế rõ rệt: chi phí cố định ban đầu cao hơn do hạ tầng HA, nhưng khi hệ thống tăng trưởng tải, chi phí biên trên mỗi request giảm nhanh, đạt điểm hòa vốn và tiết kiệm ngân sách so với kiến trúc cũ.
