// k6: cùng một workload cho cả hai kiến trúc. Chọn mức tải bằng PROFILE=normal|peak|spike
// !! Giá trị VUs/thời lượng bên dưới là MẶC ĐỊNH TẠM — thay bằng tham số trong bảng NFR của Thoại.
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE = __ENV.BASE_URL || 'http://localhost:8080';
const P = {
  normal: { stages: [{ duration: '30s', target: 20 }, { duration: __ENV.DURATION || '2m', target: 20 }, { duration: '10s', target: 0 }] },   // LOAD-NORMAL
  peak:   { stages: [{ duration: '30s', target: 100 }, { duration: __ENV.DURATION || '2m', target: 100 }, { duration: '10s', target: 0 }] }, // LOAD-PEAK
  spike:  { stages: [{ duration: '20s', target: 20 }, { duration: '10s', target: 200 }, { duration: '1m', target: 200 }, { duration: '10s', target: 20 }, { duration: '30s', target: 20 }] }, // LOAD-SPIKE
};
export const options = {
  stages: P[__ENV.PROFILE || 'normal'].stages,
  thresholds: { http_req_failed: ['rate<0.05'], http_req_duration: ['p(95)<1000'] }, // đối chiếu NFR của Thoại
};

export default function () {
  const sid = `s-${__VU}-${__ITER}`;
  const list = http.get(`${BASE}/products`);
  check(list, { 'list 200': r => r.status === 200 });
  const id = 1 + Math.floor(Math.random() * 50);
  check(http.get(`${BASE}/products/${id}`), { 'detail 200': r => r.status === 200 });
  check(http.get(`${BASE}/products/${id}/image`), { 'image 200': r => r.status === 200 });
  http.post(`${BASE}/cart/${sid}/items`, JSON.stringify({ product_id: id, qty: 1 }), { headers: { 'Content-Type': 'application/json' } });
  const o = http.post(`${BASE}/orders`, JSON.stringify({ session_id: sid }), { headers: { 'Content-Type': 'application/json' } });
  check(o, { 'order 201': r => r.status === 201 });
  sleep(1);
}
