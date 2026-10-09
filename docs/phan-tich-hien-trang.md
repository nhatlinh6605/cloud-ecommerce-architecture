# Phân tích kiến trúc hiện trạng (kiến trúc cơ sở)

Đề tài 1: Đánh giá và thiết kế lại kiến trúc website thương mại điện tử theo khung Well-Architected.
Người phụ trách: Lê Văn Nhựt. Phối hợp: Võ Nhật Linh, Phan Quang Thoại.

Nguồn: `docker-compose.base.yml`, `README.md`, các script trong `scripts/`.

## 1\. Mô tả hiện trạng

Website ba tầng chạy trên **một nút duy nhất** (một máy, Docker Compose, project `baseline`).

|Tầng|Thành phần|Ghi chú|
|-|-|-|
|Ứng dụng|`app01`|Một bản duy nhất, lắng nghe cổng 3000 trong container, mở ra máy qua cổng 8080|
|Dữ liệu|`db01` (PostgreSQL 16)|Một bản, dữ liệu lưu ở volume cục bộ `dbdata`|
|Lưu trữ đối tượng|`obj01` (MinIO)|Một bản, ảnh sản phẩm lưu ở volume `objdata`|
|Giám sát|`prometheus`|Thu metric từ `/metrics` của ứng dụng|

Không có load balancer, không có bản sao, không có cơ chế sao lưu trong cấu hình.
Các thành phần dùng chung một mạng Compose mặc định, không phân đoạn.

> Quyết định (Nhựt, 09/10/2026; nhóm được thông báo, ai phản đối thì xem lại): giữ `obj01` trong kiến trúc cơ sở (phương án A). Lý do: cùng một mã nguồn ứng dụng chạy ở cả hai kiến trúc nên phép so sánh trước và sau công bằng, và không phát sinh việc sửa mã. Sai khác so với PDF (kiến trúc cơ sở chỉ gồm ứng dụng web và cơ sở dữ liệu) được ghi vào phần giới hạn của báo cáo.

## 2\. Luồng dữ liệu chính

Người dùng → `app01` → `db01` (sản phẩm, giỏ hàng, đơn hàng) và `obj01` (ảnh sản phẩm).

|Thao tác|Endpoint|Thành phần được gọi|
|-|-|-|
|Xem sản phẩm|`GET /products`, `GET /products/:id`|`app01`, `db01`|
|Xem ảnh|`GET /products/:id/image`|`app01`, `obj01`|
|Giỏ hàng|`POST /cart/:sid/items`, `GET /cart/:sid`|`app01`, `db01`|
|Đặt hàng|`POST /orders`|`app01`, `db01`|
|Kiểm tra sức khỏe|`GET /health`|`app01`, `db01`|
|Metric|`GET /metrics`|`app01`|

## 3\. Ranh giới tin cậy và trách nhiệm quản trị

* Vùng không tin cậy: người dùng/Internet. Điểm vào duy nhất là `app01` ở cổng 8080.
* Vùng nội bộ: `app01`, `db01`, `obj01` cùng một mạng, không có ranh giới giữa tầng ứng dụng và tầng dữ liệu.
* Prometheus mở cổng 9090 ra máy chủ.
* Trách nhiệm quản trị: nhóm tự quản trị toàn bộ (hệ điều hành, Docker, ứng dụng, cơ sở dữ liệu, sao lưu). Không có dịch vụ được quản lý.

## 4\. Điểm lỗi đơn (SPOF)

|Thành phần|Hậu quả khi lỗi|Mức ảnh hưởng|
|-|-|-|
|Nút/máy chủ|Toàn bộ dịch vụ ngừng|Cao|
|`app01`|Không xử lý được bất kỳ yêu cầu nào|Cao|
|`db01`|Mất sản phẩm, giỏ hàng, đơn hàng; nếu volume hỏng thì mất dữ liệu|Cao|
|`obj01`|Không hiển thị ảnh sản phẩm|Trung bình|
|Thiếu load balancer|Không chia tải, không tự loại thành phần lỗi|Cao|
|Thiếu sao lưu|Không phục hồi được khi mất dữ liệu|Cao|

## 5\. Đánh giá sơ bộ theo trụ cột

|Trụ cột|Nhận xét hiện trạng|
|-|-|
|Độ tin cậy|Thấp: mọi thành phần là SPOF, phục hồi phải thao tác thủ công|
|Bảo mật|Mạng phẳng; mật khẩu truyền qua biến môi trường (`.env`, không commit); chưa thấy TLS|
|Hiệu quả hiệu năng|Một bản ứng dụng xử lý toàn bộ tải, không co giãn|
|Tối ưu chi phí|Ít tài nguyên nhất, chi phí thấp nhất|
|Vận hành|Đơn giản, có metric; ứng dụng chưa có healthcheck và giới hạn tài nguyên|

## 6\. Giả thuyết dự kiến (Thoại chính thức hóa trong kế hoạch kiểm thử)

* H1: Khi dừng `app01`, dịch vụ gián đoạn hoàn toàn cho đến khi bật lại thủ công.
* H2: Ở mức tải cao điểm và tăng đột biến, p95 và tỷ lệ lỗi của kiến trúc cơ sở tăng nhanh hơn kiến trúc cải tiến.

Đây là giả thuyết, chưa phải kết luận. Số liệu đo sẽ nằm ở `data/` do Thoại tổng hợp.

## 7\. Việc còn thiếu để phân tích đầy đủ

* Script `scripts/fail-base-01.sh` (dừng `app01` khi có tải) để lấy số liệu H1. Việc này thuộc Linh.

