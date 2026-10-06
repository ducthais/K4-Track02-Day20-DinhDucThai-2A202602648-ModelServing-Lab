# 01 - Tune: thread-count sweep

Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · host `Windows-AMD64` · llama.cpp `b10488`
CPU: **8 physical · 16 logical** cores · `ngl=99` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 40.7 | 98% |
| 4 | 40.8 | 98% |
| 8 | 41.6 | 100% |
| 16 | 41.1 | 99% |
| 32 | 40.9 | 98% |

**Best**: `-t 8` at 41.6 tok/s
**Slowest tested**: `-t 1` at 40.7 tok/s (1.02x spread)
**Against the physical-core default** (`-t 8`, 41.6 tok/s): 1.00x

Use this in your run:

```bash
LAB_N_THREADS=8 make bench
```

## Phân tích và giải thích cơ chế (Thread Tuning Analysis)

- **Điểm tối ưu (Knee point):** Thông lượng đạt đỉnh tại `-t 8` với 41.6 tok/s, khớp chính xác với số **8 physical cores** của vi xử lý AMD Ryzen 7 8845H.
- **Cơ chế hoạt động:** Vì bài đo chạy với GPU offload (`ngl=99` qua Vulkan backend trên Radeon 780M), quá trình decode bị nghẽn bởi băng thông bộ nhớ (memory-bandwidth bound) và tốc độ GPU kernel thay vì tính toán thuần túy trên CPU. Do đó, mức chênh lệch giữa 1 thread (40.7 tok/s) và 8 threads (41.6 tok/s) là khoảng 2.2%.
- **Hiện tượng suy giảm khi vượt quá physical cores:** Khi nâng lên 16 threads (logical cores/SMT) và 32 threads (oversubscription), tốc độ giảm nhẹ xuống 41.1 tok/s và 40.9 tok/s. Việc tạo quá nhiều thread cạnh tranh tài nguyên gây ra overhead điều phối (scheduling overhead), tranh chấp L3 cache và context switching mà không mang lại thêm kênh băng thông RAM thực tế nào.
- **Kết luận cấu hình:** Cấu hình mặc định `-t 8` (bằng physical core count) là điểm cân bằng lý tưởng nhất.
