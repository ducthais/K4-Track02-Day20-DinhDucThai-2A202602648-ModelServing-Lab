# 02 - Serve: load test + saturation reading

Host `Windows-AMD64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=8` ·
`ngl=99`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 57 | 1.03 | 6800 | 18000 | 20000 | 8.4 | 0.0% |
| 50 | 73 | 1.26 | 30000 | 39000 | 43000 | 33.1 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **1.22x** (24% of linear) |
| P95 latency | **2.17x** |
| Effective concurrency at 50 users | 33.1 vs `--parallel 4` slots (occupancy/slot ratio 8.29) |

**Saturated.** Throughput delivered only 1.22x for 5x the offered load, and effective concurrency (33.1) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 1.22x while P95 moved 2.17x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

## Đánh giá bão hòa và Goodput@SLO (Saturation Reading)

- **Bằng chứng bão hòa (Evidence of Saturation):**
  Server bão hòa hoàn toàn ở mức 50 users. Các con số chứng minh:
  1. **Tỷ lệ tăng Throughput:** Khi tải gửi vào tăng 5× (10 → 50 users), throughput thực tế chỉ tăng vỏn vẹn **1.22×** (từ 1.03 lên 1.26 RPS, đạt 24% mức kỳ vọng tuyến tính).
  2. **Bùng nổ độ trễ (Latency explosion):** P50 tăng từ 6.8s lên 30.0s (4.4×), P95 tăng từ 18.0s lên 39.0s (2.17×).
  3. **Effective Concurrency vs Slots:** Concurrency theo Little's Law ở 50 users là **33.1**, gấp **8.29×** năng lực 4 slots (`--parallel 4`).
  4. **Prometheus Gauge:** Peak `n_busy_slots_per_decode` đạt **3.96 / 4** slots và số request bị trì hoãn (`deferred`) lên tới **46 requests**. Điều này chứng minh độ trễ tăng vọt chủ yếu là **Queue Time** (thời gian nằm chờ slot rảnh trong hàng đợi) chứ không phải do bản thân model decode chậm đi.

- **Đánh giá Goodput@SLO:**
  Nếu chọn ngưỡng SLO thực tế là **Latency P95 ≤ 20 giây**:
  - Tại 10 users: P95 là 18.0s (< 20s), hệ thống đáp ứng tốt SLO, Goodput xấp xỉ ~1.0 RPS.
  - Tại 50 users: P95 vọt lên 39.0s và ngay cả Median P50 cũng lên tới 30.0s, hầu hết request đều vi phạm SLO. Do đó, dù raw throughput tăng nhẹ lên 1.26 RPS nhưng **Goodput@SLO giảm nghiêm trọng**.

- **Knob can thiệp đầu tiên để tăng Goodput@SLO:**
  Knob cần thay đổi đầu tiên là **tăng `--parallel` (ví dụ từ 4 lên 6 hoặc 8 slots)** kết hợp cấp đủ context memory cho KV-cache, hoặc thiết lập cơ chế **Admission Control / Max Queue Size**. Việc tăng slots sẽ cho phép continuous batching phục vụ đồng thời nhiều request hơn, giải tỏa hàng đợi tích tụ, giúp đưa P95 quay trở lại dưới ngưỡng SLO 20s.
