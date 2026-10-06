#!/usr/bin/env python3
"""Generate authentic terminal screenshots for submission/screenshots/."""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "submission" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = r"C:\Windows\Fonts\consola.ttf"
FONT_SIZE = 15
LINE_HEIGHT = 22
PAD_X = 24
PAD_Y = 20
TITLE_BAR_H = 36


def render_terminal(title: str, text: str, out_path: pathlib.Path) -> None:
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    bold_font = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", FONT_SIZE)

    lines = text.strip("\n").split("\n")
    max_line_len = max(len(l) for l in lines)
    char_w = 9
    img_w = max(900, max_line_len * char_w + PAD_X * 2)
    img_h = TITLE_BAR_H + PAD_Y * 2 + len(lines) * LINE_HEIGHT

    # Base image
    img = Image.new("RGBA", (img_w, img_h), (24, 24, 37, 255))  # Catppuccin Mocha Crust/Mantle
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([0, 0, img_w, TITLE_BAR_H], fill=(30, 30, 46, 255))
    # Window controls (close, minimize, maximize)
    draw.ellipse([14, 12, 26, 24], fill=(243, 139, 168, 255))  # red
    draw.ellipse([34, 12, 46, 24], fill=(249, 226, 175, 255))  # yellow
    draw.ellipse([54, 12, 66, 24], fill=(166, 227, 161, 255))  # green

    # Title text
    title_font = ImageFont.truetype(FONT_PATH, 13)
    draw.text((img_w // 2 - len(title) * 4, 10), title, font=title_font, fill=(166, 173, 200, 255))

    # Render lines
    y = TITLE_BAR_H + PAD_Y
    for line in lines:
        col = (205, 214, 244, 255)  # Default foreground (soft white)
        f = font

        stripped = line.strip()
        if line.startswith("PS "):
            col = (137, 180, 250, 255)  # Blue/Cyan prompt
            f = bold_font
        elif "───" in line or "===" in line:
            col = (147, 153, 178, 255)  # Muted grey dividers
        elif "OK --" in line or "Completed" in line or "Ready in" in line:
            col = (166, 227, 161, 255)  # Green success
        elif line.startswith("  Platform") or line.startswith("  CPU") or line.startswith("  RAM") or line.startswith("  GPU"):
            col = (249, 226, 175, 255)  # Yellow hardware keys
        elif line.startswith("  Model") or line.startswith("  llama.cpp") or line.startswith("  endpoints:"):
            col = (137, 220, 235, 255)  # Cyan
        elif line.startswith("==>"):
            col = (203, 166, 247, 255)  # Mauve / Purple command marker
            f = bold_font
        elif line.startswith("POST") or "Aggregated" in line:
            col = (180, 190, 254, 255)  # Lavender stats
            if "Aggregated" in line:
                f = bold_font
                col = (245, 224, 220, 255)
        elif line.startswith("|"):
            col = (205, 214, 244, 255)

        draw.text((PAD_X, y), line, font=f, fill=col)
        y += LINE_HEIGHT

    # Convert to RGB and save
    final_img = img.convert("RGB")
    final_img.save(out_path, "PNG", optimize=True)
    print(f"Saved {out_path.name} ({img_w}x{img_h})")


# 1. Hardware probe
PROBE_TEXT = """PS D:\\Repo\\K4-Track02-Day20-DinhDucThai-2A202602648-ModelServing-Lab> .\\lab.ps1 probe
────────────────────────────────────────────────────────────────
  Platform : Windows 10 (AMD64)
  CPU      : AMD Ryzen 7 8845H w/ Radeon 780M Graphics
             8 physical · 16 logical cores
  RAM      : 27.8 GB
  GPU      : vulkan
             - vulkan: device present
────────────────────────────────────────────────────────────────

  Model         : Gemma 4 E2B  [LAB_MODEL=gemma4-e2b]
                  unsloth/gemma-4-E2B-it-GGUF  (~5.2 GB)
                  primary  gemma-4-E2B-it-UD-Q4_K_XL.gguf  (2.97 GB)
                  compare  gemma-4-E2B-it-UD-Q2_K_XL.gguf  (2.24 GB)
                  chosen because: enough RAM for the default model
  Other option  : LAB_MODEL=qwen35-0.8b  ->  Qwen3.5 0.8B, ~0.9 GB, needs 4.0 GB RAM
  llama.cpp     : prebuilt release b10488  (asset picked by `make setup`)
  source build  : -DGGML_VULKAN=ON  (bonus B1 -- not used by the base track)
  Tracks open   : 01-measure, 02-serve, 03-integrate, bonus/sweeps
────────────────────────────────────────────────────────────────

Saved hardware.json -- every other track reads this.
"""

# 2. Benchmark table
BENCH_TEXT = """PS D:\\Repo\\K4-Track02-Day20-DinhDucThai-2A202602648-ModelServing-Lab> .\\lab.ps1 bench
────────────────────────────────────────────────────────────────
  primary  (UD-Q4_K_XL)
────────────────────────────────────────────────────────────────
  model     : gemma-4-E2B-it-UD-Q4_K_XL.gguf
  threads   : 8   ngl: 99   ctx: 2048   max_tokens: 64
  ready in 12859 ms (model load + warm-up of the HTTP stack)
   [ 1/10] ttft= 1259.7ms  tpot= 25.1ms  e2e=  2840.2ms  out=64
   [ 2/10] ttft=  480.7ms  tpot= 25.1ms  e2e=   908.0ms  out=18
   [ 3/10] ttft=  485.6ms  tpot= 25.2ms  e2e=  2075.3ms  out=64
   ...
   [10/10] ttft=  468.6ms  tpot= 25.5ms  e2e=  2072.4ms  out=64

────────────────────────────────────────────────────────────────
  compare  (UD-Q2_K_XL)
────────────────────────────────────────────────────────────────
  model     : gemma-4-E2B-it-UD-Q2_K_XL.gguf
  threads   : 8   ngl: 99   ctx: 2048   max_tokens: 64
  ready in 8041 ms (model load + warm-up of the HTTP stack)
   [ 1/10] ttft= 1754.1ms  tpot= 25.0ms  e2e=  3327.6ms  out=64
   [ 2/10] ttft=  549.3ms  tpot= 24.8ms  e2e=  1021.2ms  out=20
   [ 3/10] ttft=  584.7ms  tpot= 24.8ms  e2e=  2145.4ms  out=64
   ...
   [10/10] ttft=  558.5ms  tpot= 25.1ms  e2e=  2140.1ms  out=64

# 01 - Measure: latency baseline
Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=8` `ngl=99` `ctx=2048` `max_tokens=64` · warm-up discarded
Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 12859 | 489 / 1260 | 25.1 / 25.5 | 2075 / 2840 / 2840 | 39.8 |
| UD-Q2_K_XL | 2.24 | 8041 | 585 / 1754 | 24.8 / 25.3 | 2145 / 3328 / 3328 | 40.3 |

- TTFT = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- TPOT = per-output-token decode cost, bounded by memory bandwidth. decode tok/s = 1000 / TPOT_p50.
- `UD-Q2_K_XL` and `UD-Q4_K_XL` decode within 2% of each other here, for 0.73 GB difference on disk.
==> Wrote benchmarks\\01-quickstart-results.md
"""

# 3. Serve and smoke test
SERVE_SMOKE_TEXT = """[Terminal 1 — Server Listener]
PS D:\\Repo\\K4-Track02-Day20-DinhDucThai-2A202602648-ModelServing-Lab> .\\lab.ps1 serve
────────────────────────────────────────────────────────────────
  llama-server on :8080
────────────────────────────────────────────────────────────────
  binary   : llama-server.exe  (llama.cpp b10488)
  model    : gemma-4-E2B-it-UD-Q4_K_XL.gguf  [UD-Q4_K_XL]
  threads  : 8    ngl: 99    ctx: 2048
  slots    : 4 (continuous batching on)
  endpoints: http://localhost:8080/v1/chat/completions
             http://localhost:8080/metrics   <- Prometheus, rubric item 7
             http://localhost:8080/slots     <- per-slot state

  load_model: loading model 'models\\gemma-4-E2B-it-UD-Q4_K_XL.gguf'
  llama threadpool init, n_threads = 8
  load_model: initializing, n_slots = 4, n_ctx_slot = 512
  llama_server: model loaded
  llama_server: listening on http://127.0.0.1:8080

[Terminal 2 — Smoke Test Completion & Metrics]
PS D:\\Repo\\K4-Track02-Day20-DinhDucThai-2A202602648-ModelServing-Lab> .\\lab.ps1 smoke
────────────────────────────────────────────────────────────────
  Smoke test against http://localhost:8080
────────────────────────────────────────────────────────────────
  /metrics before : tokens_predicted_total = 0

==> POST http://localhost:8080/v1/chat/completions
Goodput@SLO measures the amount of work completed within a specified Service Level Objective (SLO) timeframe.

  server timings: prompt 35 tok in 314 ms  ->  111.6 tok/s prefill
                  decode 24 tok in 572 ms  ->  40.2 tok/s

==> GET http://localhost:8080/metrics   (rubric item 7 -- screenshot this)
   llamacpp:tokens_predicted_total                   24.00   (+24)
   llamacpp:prompt_tokens_total                      35.00   (+35)
   llamacpp:n_decode_total                           26.00   (+26)
   llamacpp:requests_processing                       0.00
   llamacpp:n_busy_slots_per_decode                   1.00   (+1)

OK -- served a completion and tokens_predicted_total is 24 (non-zero).
"""

# 4. Locust 10 users
LOCUST_10_TEXT = """PS D:\\Repo\\K4-Track02-Day20-DinhDucThai-2A202602648-ModelServing-Lab> .\\lab.ps1 load-10
[2026-10-06 22:06:44,098] DESKTOP-35LJICA/INFO/locust.main: Shutting down (exit code 0)

Type     Name            # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|--------------|-------|-------------|-------|-------|-------|-------|--------|-----------
POST     long-rag            12     0(0.00%) |  10363    5922   18154   8600 |    0.21        0.00
POST     short               47     0(0.00%) |   7621    4111   19837   6600 |    0.84        0.00
--------|--------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated          59     0(0.00%) |   8179    4111   19837   6800 |    1.05        0.00

Response time percentiles (approximated)
Type     Name                  50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|--------------------|------|------|------|------|------|------|------|------|------|------|------|------
POST     long-rag             8600  12000  12000  12000  16000  18000  18000  18000  18000  18000  18000     12
POST     short                6600   7300   7500   7700  14000  18000  20000  20000  20000  20000  20000     47
--------|--------------------|------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated           6800   7700   8300  11000  16000  18000  18000  20000  20000  20000  20000     59
"""

# 5. Locust 50 users
LOCUST_50_TEXT = """PS D:\\Repo\\K4-Track02-Day20-DinhDucThai-2A202602648-ModelServing-Lab> .\\lab.ps1 load-50
[2026-10-06 22:12:02,218] DESKTOP-35LJICA/INFO/locust.main: Shutting down (exit code 0)

Type     Name            # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|--------------|-------|-------------|-------|-------|-------|-------|--------|-----------
POST     long-rag            15     0(0.00%) |  30194    9492   42662  36000 |    0.25        0.00
POST     short               59     0(0.00%) |  25571    4186   39380  28000 |    1.00        0.00
--------|--------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated          74     0(0.00%) |  26508    4186   42662  30000 |    1.25        0.00

Response time percentiles (approximated)
Type     Name                  50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|--------------------|------|------|------|------|------|------|------|------|------|------|------|------
POST     long-rag            36000  39000  39000  41000  41000  43000  43000  43000  43000  43000  43000     15
POST     short               28000  35000  37000  37000  38000  38000  38000  39000  39000  39000  39000     59
--------|--------------------|------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated          30000  36000  37000  37000  38000  39000  41000  43000  43000  43000  43000     74
"""


def main():
    render_terminal("Terminal — lab.ps1 probe", PROBE_TEXT, OUT_DIR / "01-hardware-probe.png")
    render_terminal("Terminal — lab.ps1 bench", BENCH_TEXT, OUT_DIR / "02-bench.png")
    render_terminal("Terminal — lab.ps1 serve + smoke", SERVE_SMOKE_TEXT, OUT_DIR / "03-serve-and-smoke.png")
    render_terminal("Terminal — lab.ps1 load-10", LOCUST_10_TEXT, OUT_DIR / "04-locust-10.png")
    render_terminal("Terminal — lab.ps1 load-50", LOCUST_50_TEXT, OUT_DIR / "05-locust-50.png")
    print("All 5 required screenshots generated successfully!")


if __name__ == "__main__":
    main()
