# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.1 | 4030.2 | 4030.3 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 3361.1 | 3361.2 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.0 | 3472.4 | 3472.5 |

Mean per stage (ms): embed **0.0** · retrieve **0.0** ·
llm **3621.2** · total **3621.3**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.

**What problem does PagedAttention actually solve?**

> PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.


## Khai báo Real/Stub và Phân tích Bottleneck

### 1. Khai báo trạng thái tích hợp các thành phần N16–N20:
- **N16 Cloud/IaC:** Stub (Chạy local trực tiếp trên máy trạm Windows, không dùng Terraform/Cloud provider).
- **N17 Data pipeline:** Stub (Sử dụng 5 toy documents sẵn có trong bộ nhớ script).
- **N18 Lakehouse:** Stub (Không tích hợp kho dữ liệu Delta/Iceberg/Parquet bên ngoài).
- **N19 Vector + features:** Stub (Sử dụng thuật toán fallback keyword overlap trong script; embed = 0.0 ms, retrieve = 0.0 ms).
- **N20 Serving:** **REAL** (Phục vụ thực tế qua tiến trình `llama-server` cục bộ với mô hình `Gemma 4 E2B UD-Q4_K_XL`, streaming context và sinh câu trả lời thật qua OpenAI-compatible API).

### 2. Phân tích Bottleneck và hướng tối ưu 2× Latency:
- **Hiện trạng:** Giai đoạn **LLM sinh câu trả lời chiếm 3621.2 ms (100.0% tổng thời gian pipeline)**, trong khi khâu retrieve chỉ mất ~0.0–0.1 ms do tập corpus nhỏ. Kết quả này hoàn toàn khớp với bản chất của các hệ thống RAG khi chi phí lớn nhất luôn nằm ở autoregressive generation của LLM.
- **Chiến lược giảm latency 2×:** Ta bắt buộc phải tập trung tối ưu **LLM generation stage**:
  1. **Tối ưu Prompt & KV Cache:** Giới hạn context retrieve (Top-K ngắn gọn, nén prompt) và bật Prefix Caching trong `llama-server` để tái sử dụng KV cache của system prompt và context chung, giảm TTFT về mức tối thiểu.
  2. **Tăng tốc Decode:** Sử dụng Speculative Decoding (draft model nhỏ hơn hoặc Medusa/MTP) để sinh nhiều token mỗi forward pass, đẩy decode throughput từ ~40 tok/s lên >70 tok/s.
  3. **Streaming TTFT:** Chuyển sang Server-Sent Events (SSE) streaming để người dùng nhận first token ngay lập tức (~400–500 ms) thay vì phải đợi toàn bộ 3.6s mới nhận trọn vẹn JSON payload.
