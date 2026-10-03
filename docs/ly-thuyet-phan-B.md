# Lý thuyết phần B: Điện toán đám mây
*(Nội dung dựa trên NIST SP 800-145 [1]; mỗi thành viên tự viết phần của mình — đây là bản nháp để Linh chỉnh sửa/diễn đạt lại.)*

## 1. Năm đặc trưng thiết yếu
1. **On-demand self-service** – Người dùng tự cấp phát tài nguyên (máy chủ, lưu trữ) khi cần, không cần nhân viên nhà cung cấp can thiệp. *Trong đồ án:* `docker compose up` tự dựng toàn bộ môi trường.
2. **Broad network access** – Dịch vụ truy cập qua mạng bằng cơ chế chuẩn (HTTP/HTTPS) từ nhiều loại thiết bị. *Đồ án:* ứng dụng truy cập qua cổng 8080.
3. **Resource pooling** – Tài nguyên dùng chung phục vụ nhiều người dùng theo mô hình đa người thuê, cấp phát động. *Đồ án:* nhiều dịch vụ chia sẻ cùng tài nguyên máy chủ.
4. **Rapid elasticity** – Tài nguyên co giãn nhanh theo tải, người dùng thấy gần như vô hạn. *Đồ án:* kiến trúc cải tiến thêm bản sao APP02 sau LB01.
5. **Measured service** – Mức sử dụng được đo, giám sát, báo cáo minh bạch. *Đồ án:* Prometheus/Grafana đo độ trễ, lỗi, thông lượng.

## 2. Ba mô hình dịch vụ
- **IaaS** – cung cấp hạ tầng (máy ảo, mạng, lưu trữ); người dùng quản lý OS và ứng dụng. Ví dụ: EC2, Azure VM, Compute Engine.
- **PaaS** – cung cấp nền tảng chạy ứng dụng; người dùng chỉ quản lý mã và dữ liệu. Ví dụ: Elastic Beanstalk, App Engine.
- **SaaS** – cung cấp phần mềm hoàn chỉnh qua mạng. Ví dụ: Gmail, Microsoft 365.

## 3. Bốn mô hình triển khai
- **Private cloud** – dành riêng cho một tổ chức. **Community cloud** – dùng chung cho cộng đồng có mục tiêu tương đồng.
- **Public cloud** – cung cấp cho công chúng, do nhà cung cấp sở hữu. **Hybrid cloud** – kết hợp từ hai mô hình trở lên, liên thông bằng công nghệ chuẩn.

*Liên hệ đồ án:* môi trường thí nghiệm chạy trên máy cục bộ mô phỏng các thành phần của public cloud (LB, compute, DB, object storage).

## Tài liệu tham khảo
[1] P. Mell, T. Grance, *The NIST Definition of Cloud Computing*, NIST SP 800-145, 2011.
