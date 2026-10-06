# 02 - Continuous batching under load (u50)

Host `Windows-AMD64` · `--parallel 4` · 14 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.96 of 4 slots (99%) |
| `requests_processing` | 4 |
| `requests_deferred` | 46 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 7804 |

Highest sampled value was **3.96 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Quan sát và phân tích Continuous Batching

- **Độ rộng Batch thực tế (Peak Batch Width):** Peak đạt **3.96 / 4 slots (99% dung lượng slot)**. Điều này cung cấp bằng chứng thực nghiệm rõ ràng rằng bộ lập lịch của `llama-server` đã liên tục ghép (pack) các request đến cùng lúc vào chung các bước forward pass decode, chứng minh continuous batching hoạt động hiệu quả.
- **Đối chiếu với Effective Concurrency (33.1):** Con số 33.1 trong `02-server-results.md` và 3.96 ở đây phản ánh hai khía cạnh bổ trợ cho nhau:
  - `3.96 slots`: Là năng lực xử lý decode đồng thời thực tế bên trong engine tại một thời điểm (bị giới hạn trên bởi `--parallel 4`).
  - `33.1`: Là tổng lượng request đang nằm trong toàn bộ hệ thống (in-flight) theo Little's Law.
  - Số `requests_deferred` chạm mốc **46** chứng minh phần chênh lệch lớn giữa 33.1 và 3.96 chính là lượng request đang phải chờ trong hàng đợi (Queue Time). Gauge đo từ server là chỉ số tin cậy nhất về độ bận của hardware slot, trong khi Little's Law phản ánh áp lực tải và độ dài hàng đợi.
