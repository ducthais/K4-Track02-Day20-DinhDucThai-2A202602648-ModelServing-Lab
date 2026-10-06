# 01 - Measure: latency baseline

Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=8` `ngl=99` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 12859 | 489 / 1260 | 25.1 / 25.5 | 2075 / 2840 / 2840 | 39.8 |
| UD-Q2_K_XL | 2.24 | 8041 | 585 / 1754 | 24.8 / 25.3 | 2145 / 3328 / 3328 | 40.3 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` and `UD-Q4_K_XL` decode within 2% of each other here, for 0.73 GB difference on disk.

## Quan sát và đánh giá chất lượng

Trên hệ thống AMD Ryzen 7 8845H với Radeon 780M (Vulkan GPU offload, ngl=99):
- **Tốc độ decode:** Cả hai bản đạt tốc độ decode gần như tương đương nhau (UD-Q2_K_XL đạt 40.3 tok/s so với UD-Q4_K_XL đạt 39.8 tok/s, chênh lệch chỉ ~1.2%), do decode bị giới hạn bởi memory bandwidth của LPDDR5/Vulkan runtime.
- **Latency & Dung lượng:** UD-Q2_K_XL giảm 0.73 GB dung lượng (2.24 GB vs 2.97 GB) và load nhanh hơn (8.0s vs 12.8s), nhưng TTFT P50 của UD-Q4_K_XL lại tốt hơn (489 ms vs 585 ms) do việc giải lượng tử 2-bit phức tạp hơn ở prefill.
- **Chất lượng thực tế:** Khi thử nghiệm cùng prompt kỹ thuật về Continuous vs Static Batching, UD-Q4_K_XL đưa ra câu trả lời mạch lạc, cấu trúc rõ ràng và giải thích chính xác trade-off về latency/throughput. Bản UD-Q2_K_XL bị cụt câu và cấu trúc lỏng lẻo hơn.
- **Kết luận:** Với máy có 28 GB RAM và iGPU Vulkan, việc đánh đổi chất lượng lấy 0.73 GB là không đáng; UD-Q4_K_XL là lựa chọn tối ưu cho phục vụ sản xuất.
