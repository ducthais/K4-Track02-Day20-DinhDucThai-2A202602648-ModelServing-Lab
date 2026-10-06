# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.
>
> `make verify` sẽ fail nếu còn placeholder chưa điền. Đó là cố ý.

**Họ Tên:** Đinh Đức Thái
**MSSV:** 2A202602648
**Cohort:** K4-Track02
**Ngày submit:** 2026-10-06

---

## 1. Hardware & runtime  *(rubric 1, 2 — 10 điểm)*

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** Windows 10 (AMD64)
- **CPU:** AMD Ryzen 7 8845H w/ Radeon 780M Graphics
- **Cores:** 8 physical / 16 logical
- **CPU extensions:** AVX2, AVX-512
- **RAM:** 27.8 GB
- **Accelerator:** Vulkan (Radeon 780M Graphics)
- **llama.cpp asset đã tải:** llama-b10488-bin-win-vulkan-x64.zip
- **Model đã dùng:** Gemma 4 E2B (`LAB_MODEL=gemma4-e2b`)
- **Quantization:** UD-Q4_K_XL + UD-Q2_K_XL (từ `models/active.json`)

**Chạy ở đâu:** Laptop cá nhân

**Setup story** (≤ 80 chữ): Khắc phục lỗi thoát chuỗi và ký tự em-dash không tương thích mã hóa trong `lab.ps1` trên PowerShell 5.1; cấu hình `PYTHONUTF8=1` để tránh crash cp1252 charmap trên Windows. Tải đầy đủ bộ đôi weights Gemma 4 GGUF qua Hugging Face Hub và giải nén runtime prebuilt b10488 kích hoạt GPU Vulkan offload thành công.

---

## 2. Đo lường  *(rubric 3, 4, 5 — 20 điểm)*

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 12859 | 489 / 1260 | 25.1 / 25.5 | 2075 / 2840 / 2840 | 39.8 |
| UD-Q2_K_XL | 2.24 | 8041 | 585 / 1754 | 24.8 / 25.3 | 2145 / 3328 / 3328 | 40.3 |

**Quan sát** (≤ 60 chữ): Bản 2-bit decode chỉ nhanh hơn ~1.2% (40.3 vs 39.8 tok/s) và tiết kiệm 0.73 GB nhưng TTFT lại chậm hơn (585 vs 489 ms). Thử cùng câu hỏi, bản 4-bit trả lời đầy đủ, mạch lạc và chuẩn xác; bản 2-bit suy giảm cấu trúc và cụt ý. Không đáng hy sinh chất lượng lấy 0.73 GB trên máy 28 GB RAM.

---

## 3. Serving under load  *(rubric 8, 9, 10 — 20 điểm)*

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 1.03 | 6800 | 18000 | 20000 | 8.4 | 0.0% |
| 50 | 1.26 | 30000 | 39000 | 43000 | 33.1 | 0.0% |

- **Offered load tăng 5×, throughput thực tăng:** 1.22×
- **P95 tăng:** 2.17×
- **Effective concurrency ở 50 users:** 33.1 so với `--parallel` = 4 slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang chạy): 3.96 / 4 slots

**Saturation reading** (≤ 80 chữ): Server bão hòa ở 50 users: throughput chỉ tăng 1.22× khi tải tăng 5×, concurrency đạt 33.1 (>4 slots). Peak busy slots 3.96/4 và 46 deferred requests chứng minh latency tăng vọt do Queue Time chứ không phải compute time. Để nâng Goodput tại SLO 20s, sẽ tăng `--parallel` lên 8 slots trước tiên để tăng năng lực continuous batching giải tỏa hàng đợi.

---

## 4. Integration  *(rubric 12, 13 — 15 điểm)*

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | Infrastructure as Code | stub |
| N17 Data pipeline | Data Cleaning & Ingestion | stub |
| N18 Lakehouse | Storage & Table Management | stub |
| N19 Vector + features | Vector Embeddings & Index | stub |
| N20 Serving | `llama-server` | real |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: 0.0 ms
- retrieve: 0.0 ms
- llm: 3621.2 ms
- **stage chiếm nhiều nhất:** llm (100.0% của total)

**Reflection** (≤ 60 chữ): Bottleneck nằm 100% ở LLM generation, khớp kỳ vọng vì keyword retrieval chạy in-memory tức thì. Để giảm latency 2×, cần tối ưu LLM: áp dụng prefix caching để loại bỏ prefill lặp lại, rút ngắn context chunk và dùng speculative decoding để đẩy decode rate.

---

## 5. The single change that mattered most  *(rubric 11 — 10 điểm)*

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn
> một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization,
> `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** Tối ưu hóa số luồng tính toán CPU (`-t`) từ mức tối thiểu 1 thread lên 8 threads (khớp với 8 physical cores của CPU AMD Ryzen 7 8845H) trong bài đo sweep của `make tune`.

```
before:  40.7 tok/s (-t 1)
after:   41.6 tok/s (-t 8)
speedup: 1.02×
```

**Tại sao nó work** (1–2 đoạn — đây là phần grader đọc kỹ nhất):

Do mô hình Gemma 4 E2B được offload sang GPU qua Vulkan backend (`ngl=99` trên AMD Radeon 780M Graphics), quá trình decode token bị giới hạn chủ yếu bởi băng thông bộ nhớ (memory-bandwidth bound) của LPDDR5 và tốc độ thực thi kernel của iGPU, thay vì sức mạnh tính toán số học thuần túy của CPU.

Khi điều chỉnh từ 1 lên 8 threads (khớp chính xác số physical cores), throughput decode đạt đỉnh 41.6 tok/s nhờ phân phối tối ưu các tác vụ nạp bộ đệm và điều phối pipeline mà không làm quá tải CPU. Ngược lại, khi đẩy lên 16 threads (logical cores/SMT) hoặc 32 threads (oversubscription), tốc độ giảm nhẹ xuống 41.1 và 40.9 tok/s do phát sinh chi phí chuyển đổi ngữ cảnh (context switching), tranh chấp L3 cache và xung đột bộ điều phối luồng mà không đem lại thêm kênh băng thông vật lý nào.

---

## 6. Bonus  *(optional — tối đa 10 điểm)*

> Bám sát nguyên tắc kế hoạch: chỉ làm bonus khi hoàn tất base track.

*(để trống)*

---

## 7. Điều làm bạn ngạc nhiên nhất  *(optional)*

Cơ chế Continuous Batching trong `llama-server` hoạt động cực kỳ mượt mà: gauge `n_busy_slots_per_decode` đạt tới 3.96/4 slot đồng thời dưới tải nặng 50 users mà không phát sinh bất kỳ lỗi HTTP nào (0.0% failure rate).

---

## 8. Self-check trước khi push

- [x] `hardware.json` committed
- [x] `models/active.json` committed
- [x] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [x] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [x] `benchmarks/02-server-results.md` committed (`make load-report`)
- [x] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [x] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed (`make load-10` / `load-50`)
- [x] `benchmarks/03-integration-results.md` committed (`make pipeline`)
- [x] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md`
      đã được thay bằng nhận xét của bạn
- [x] 5 screenshots trong `submission/screenshots/`
- [x] `make verify` → **exit 0**
- [ ] Repo tên đúng mẫu `K4-L3-DAY20-HoVaTen-MSSV-ModelServing` (xem `docs/SUBMISSION.md`)
- [ ] Repo GitHub ở chế độ **public**
- [ ] Đã push và paste public URL vào VinUni LMS **trước 23:59 (UTC+7) ngày làm lab**
- [x] **Không** commit `models/*.gguf`, `runtime/` hay `.env` (đã có trong `.gitignore`)

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không
xem được → 0 điểm.

---

## 9. Khai báo sử dụng AI  *(xem `docs/RULES.md` §3)*

Sử dụng AI assistant (Gemini 3.8 Flash) hỗ trợ gỡ lỗi PowerShell parsing (`lab.ps1`), hỗ trợ xử lý mã hóa UTF-8 cho Windows console, tự động hóa chuỗi lệnh chạy benchmark/load-test và định dạng văn bản báo cáo theo đúng rubric. Toàn bộ số liệu benchmark, load test và quan sát kỹ thuật được đo và xác thực trực tiếp trên môi trường máy trạm cá nhân.
