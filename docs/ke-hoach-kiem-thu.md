# KẾ HOẠCH KIỂM THỬ VÀ MA TRẬN TEST MATRIX
**Đề tài:** Đánh giá và thiết kế lại kiến trúc website thương mại điện tử theo khung Well-Architected  
**Người phụ trách chính:** Phan Quang Thoại (SV3) | **Phối hợp:** Võ Nhật Linh (Tải, Ứng dụng), Lê Văn Nhựt (Hạ tầng, LB)

---

## 1. Mục tiêu và Nguyên tắc kiểm thử
* **Mục tiêu:** Kiểm chứng định lượng các giả thuyết kiến trúc; so sánh hiệu năng, độ tin cậy giữa Kiến trúc Cơ sở (`BASE-NODE`) và Kiến trúc Cải tiến (`improved`: LB01 + APP01/APP02) đối chiếu với bảng NFR.
* **Nguyên tắc kiểm soát sai số:**
  1. **Số lần lặp (Repetitions):** Mọi kịch bản đo tải hiệu năng bắt buộc chạy lặp lại **3 lần** (`REPS=3`).
  2. **Trạng thái môi trường sạch (Clean State):** Trước mỗi lần đo, bắt buộc chạy `bash scripts/reset-data.sh [base|improved]` để đưa dữ liệu về đúng 50 sản phẩm mẫu ban đầu trong `seed.sql`.
  3. **Workload nhất quán:** Cùng một kịch bản sinh tải `load/load.js` bằng công cụ `k6` cho cả hai kiến trúc.
  4. **Ghi nhận giới hạn:** Máy phát tải (LOADGEN) chạy cùng máy vật lý với Docker; CPU cạnh tranh có thể làm tăng nhẹ độ trễ nền, kết quả dùng để so sánh tương quan A/B.

---

## 2. Thiết lập Môi trường và Công cụ
* **Công cụ sinh tải:** `k6` (phiên bản ≥ 0.50).
* **Workload API:** Luồng người dùng gồm 5 bước: `GET /products` -> `GET /products/:id` -> `GET /products/:id/image` -> `POST /cart/:sid/items` -> `POST /orders`.
* **Cấu hình 3 mức tải:**
  * **LOAD-NORMAL:** 20 VUs (Ramp-up 30s, Giữ tải 2 phút, Ramp-down 10s).
  * **LOAD-PEAK:** 100 VUs (Ramp-up 30s, Giữ tải 2 phút, Ramp-down 10s).
  * **LOAD-SPIKE:** 20 VUs (20s) -> Nhảy vọt 200 VUs (10s) -> Giữ 200 VUs (1 phút) -> Hạ về 20 VUs (10s) -> Giữ 20 VUs (30s).

---

## 3. Ma trận Kiểm thử chi tiết (Test Matrix)

| Mã Test Case | Hạng mục kiểm thử | Kiến trúc áp dụng | Điều kiện tiên quyết & Lệnh thực thi | Kỳ vọng kết quả (Tiêu chí Pass) | Đối chiếu NFR | Người thực hiện |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-FUNC-01** | Kiểm tra chức năng toàn trình (E2E API) | Cả 2 | Dựng hệ thống (`base-up.sh` hoặc `improved-up.sh`); gọi tuần tự 5 API nghiệp vụ | HTTP 200 cho xem sản phẩm/ảnh; HTTP 201 cho giỏ hàng và tạo đơn hàng thành công | NFR-06 | Linh test; Thoại ghi nhận |
| **TC-FUNC-02** | Phân phối lưu lượng qua Load Balancer | Cải tiến | `improved-up.sh` đang chạy; gửi 10 request liên tiếp tới `/health` | Header `X-Instance` trả về xen kẽ giữa `app01` và `app02` | NFR-01 | Nhựt & Thoại |
| **TC-PERF-01** | Hiệu năng tải thường (`LOAD-NORMAL`) | Cả 2 | Reset data; chạy `PROFILE=normal bash scripts/run-load.sh <arch> 3` | • **p95 ≤ 300 ms**<br>• Error rate = 0.00%<br>• Throughput ≥ 50 req/s | NFR-01 | Linh chạy tải; Thoại trích xuất CSV |
| **TC-PERF-02** | Hiệu năng tải cao điểm (`LOAD-PEAK`) | Cả 2 | Reset data; chạy `PROFILE=peak bash scripts/run-load.sh <arch> 3` | • **p95 ≤ 800 ms**<br>• Error rate ≤ 0.5%<br>• Kiến trúc cải tiến có throughput cao hơn cơ sở | NFR-02 | Linh chạy tải; Thoại trích xuất CSV |
| **TC-PERF-03** | Khả năng chịu tải đột biến (`LOAD-SPIKE`) | Cả 2 | Reset data; chạy `PROFILE=spike bash scripts/run-load.sh <arch> 3` | • Error rate ≤ 2.0%<br>• Hệ thống không bị treo cứng, phục hồi ngay khi hết đợt spike | NFR-03 | Linh chạy tải; Thoại trích xuất CSV |
| **TC-FAIL-01** | Dừng dịch vụ nút đơn (`FAIL-BASE-01`) | Cơ sở | Hệ thống cơ sở đang có tải nền; chạy lệnh dừng container `app01` | • Dịch vụ gián đoạn 100% (HTTP Connection Refused/Timeout)<br>• Minh chứng cho rủi ro SPOF | NFR-05 | Thoại ghi log đối chứng |
| **TC-FAIL-02** | Dừng 1 bản sao ứng dụng (`FAIL-IMP-01`) | Cải tiến | Hệ thống cải tiến có tải nền; chạy `bash scripts/fail-imp-01.sh` (tắt `app02` 30s rồi bật lại) | • **failover_s ≤ 7 giây** (LB01 chuyển hết tải sang `app01`)<br>• **rejoin_s ≤ 10 giây** (`app02` nhận lại request)<br>• Error rate sự cố ≤ 2.0% | NFR-04 | Linh thao tác; Nhựt check LB; Thoại bấm giờ |
| **TC-DATA-01** | Tính bền vững dữ liệu & Stateless | Cả 2 | Tạo đơn hàng mới; upload ảnh; chạy `down.sh` rồi `up.sh` lại (không purge) | Toàn bộ đơn hàng trong `dbdata` và ảnh trong `objdata` vẫn còn nguyên vẹn | NFR-06 | Linh test; Thoại kiểm chứng |
| **TC-SEC-01** | Kiểm tra an toàn bảo mật hạ tầng | Cả 2 | Quét repository git; kiểm tra port mở bằng `nmap`/`docker ps` | • 0 secret bị lộ trong git<br>• `db01` và `obj01` không public port bừa bãi | NFR-07 | Nhựt rà soát; Thoại lập biên bản |

---

## 4. Cấu trúc lưu trữ dữ liệu kiểm thử
Toàn bộ kết quả đầu ra sau các đợt chạy test sẽ được lưu trữ phân cấp:
* Dữ liệu thô k6: `results/{arch}-{profile}-run{r}.json` và `.log` (Linh bàn giao).
* Bảng số liệu tổng hợp (Thoại trích xuất):
  * `data/summary/latency_p50.csv`
  * `data/summary/latency_p95.csv`