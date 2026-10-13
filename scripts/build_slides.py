#!/usr/bin/env python3
"""Build docs/presentation.pdf (10 slides) with no external tooling.

    python scripts/build_slides.py

Writes a small vector PDF by hand (Helvetica base fonts, WinAnsi),
so the deck can be regenerated on any machine that has Python.
Slide content lives in SLIDES below and mirrors
docs/presentation_outline.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "presentation.pdf"

PAGE_W, PAGE_H = 960, 540

# Colors (0..1 RGB)
TEAL = (0.055, 0.463, 0.431)
TEAL_DARK = (0.035, 0.302, 0.282)
AMBER = (0.914, 0.635, 0.157)
INK = (0.106, 0.122, 0.137)
GRAY = (0.42, 0.45, 0.48)
LIGHT = (0.949, 0.957, 0.965)
WHITE = (1.0, 1.0, 1.0)

SLIDES: list[dict] = [
    {
        "title": "1. Problem and user",
        "rows": [
            ("h", "Who"),
            ("b", "Clinical officers and nurses at small clinics making triage calls under time pressure"),
            ("b", "Ops leads who must audit decisions and control AI cost"),
            ("sp", ""),
            ("h", "Problem"),
            ("b", "Paper protocols differ per site - inconsistent acuity calls, no audit trail"),
            ("b", "Free-text notes carry phone numbers and IDs into logs"),
            ("b", "Unclear which model/rules produced a decision, and what it cost"),
            ("sp", ""),
            ("c", "AfyaPlus: one authenticated triage service with deterministic, inspectable decisions."),
        ],
    },
    {
        "title": "2. Path chosen and why",
        "rows": [
            ("h", "Path: AfyaPlus Module 4 Capstone (recommended)"),
            ("b", "Weeks 1-5: LLM/RAG fundamentals  ->  router + RAG layer"),
            ("b", "Week 6: Triage API  ->  /health /token /triage with auth"),
            ("b", "Week 7: Cost / MCP logistics  ->  tool stubs + cost ledger"),
            ("b", "Week 8: Pins / versioning  ->  manifest + pin-field tests"),
            ("b", "Week 9: Security  ->  redaction + security smoke + repo secret scan"),
            ("b", "Week 10: Catalog  ->  marketplace fixture line (poster path not taken)"),
            ("sp", ""),
            ("c", "Why: one coherent product demonstrates the whole skill checklist."),
            ("c", "Mapping: skill_matrix.md + integration_map.json (week_reuse)."),
        ],
    },
    {
        "title": "3. Architecture - module boundaries",
        "code": [
            "                 +--------------------------------------+",
            "                 |   triage/policy.py  (single ruleset)  |",
            "                 | acuity: symptoms+vitals+age | routing  |",
            "                 +----+----------------+-----------------+",
            "                      |                |",
            "        +---------------v----+   +-----v--------------+",
            "        | domain_twin.py     |   | router/deterministic|",
            "        | assess/recommend   |   | endpoint + priority |",
            "        +---------+----------+   +---------+-----------+",
            "                  +------v-----------------v---+",
            "   POST /triage ->| triage/api.py + auth.py    |<- GET /health",
            "                  | 401/403/422, redact note   |",
            "                  +--+----------+----------+---+",
            "                     |          |          |",
            "        rag/ (ingest+retriever)  mcp/ (tools+cost)   pins/ (manifest)",
            "        security/ (redaction)    catalog/ (marketplace search)",
            "                     |",
            "        fixtures/ 300 triage + 200 catalog rows (seeded, no scrape)",
        ],
        "rows": [
            ("sp", ""),
            ("c", "One ruleset feeds assessment, routing and gold labels - stub mode end to end"),
        ],
    },
    {
        "title": "4. Skill coverage - which skills, where in repo",
        "rows": [
            ("kv", "Weeks 1-5 | src/afyaplus/rag/, router/deterministic.py, evaluation.py"),
            ("kv", "Week 6    | triage/api.py, triage/auth.py, tests/test_api.py"),
            ("kv", "Week 7    | mcp/tools.py, mcp/cost_tracker.py, docs/cost_analysis.md"),
            ("kv", "Week 8    | pins/manifest.py + manager.py, tests/test_pin_fields.py"),
            ("kv", "Week 9    | security/redaction.py, tests/test_security_smoke.py"),
            ("kv", "Week 10   | catalog/service.py, fixtures/catalog_listings_sample.jsonl"),
            ("kv", "Cross     | pytest.ini tiers, perf_stub.json, docs pack, git flow"),
            ("sp", ""),
            ("c", "Full mapping: skill_matrix.md (required/optional per row)"),
            ("c", "Machine readable: integration_map.json -> week_reuse"),
        ],
    },
    {
        "title": "5. Live demo",
        "rows": [
            ("h", "Three commands"),
            ("c", "$ ./start_service.sh"),
            ("c", "$ curl -i http://127.0.0.1:8000/health"),
            ("c", "$ TOKEN=$(curl -s -X POST .../token ...) && curl -i .../triage -H \"Bearer $TOKEN\" ..."),
            ("sp", ""),
            ("b", "On screen: 200 health -> token -> triage with a PII note"),
            ("b", "Response shows redacted_note: 'Call [PHONE] or [EMAIL] about the fever'"),
            ("b", "Server log prints the redacted note only"),
            ("sp", ""),
            ("h", "Backup if the network misbehaves"),
            ("b", "docs/demo_transcript.md - 60-second step-by-step with real output"),
            ("b", "docs/evidence/api_transcript.txt - full headers for 200/401/403/422"),
        ],
    },
    {
        "title": "6. Testing evidence",
        "rows": [
            ("c", "$ pytest -q                     -> 55 passed, 12 deselected"),
            ("c", "$ pytest -m integration         -> 12 passed, 55 deselected"),
            ("c", "$ python scripts/eval_score.py  -> EVAL SCORE: 1.0000 (300/300 rows)"),
            ("sp", ""),
            ("b", "Security smoke: real redaction test, repo secret scan, token tamper checks"),
            ("b", "Pin test: source digest + requirements must match the manifest"),
            ("b", "Perf (p95): route 0.05ms | twin 0.15ms | retriever 0.87ms | HTTP 18.3ms"),
            ("sp", ""),
            ("h", "The test that earned its keep"),
            ("b", "Golden set caught label drift: pre-fix eval 0.6833, 95/300 rows wrong"),
            ("b", "Fix: shared policy module - incident note in docs/incidents/"),
        ],
    },
    {
        "title": "7. Security and compliance choices",
        "rows": [
            ("b", "Auth: HMAC-SHA256 bearer tokens - 401 without/invalid, 403 for wrong role"),
            ("b", "Redaction at the edge: raw PII never echoed, never logged (shown live)"),
            ("b", "Repo hygiene: CI scans every text file for key patterns; no .env committed"),
            ("b", "Fixtures: synthetic only, identifier fields rejected by tests"),
            ("b", "Data lines separated: clinical fixture vs catalog fixture, asserted both ways"),
            ("b", "Secrets from env (AFYA_TOKEN_SECRET), dev placeholder clearly labelled"),
            ("sp", ""),
            ("c", "No production data, no scraping, no live provider calls in this build."),
        ],
    },
    {
        "title": "8. Cost table with assumptions",
        "table": [
            ["Step", "API calls", "Cost"],
            ["Unit + security + golden tests", "0", "$0.00"],
            ["Integration tests (in-process)", "0", "$0.00"],
            ["Golden-set eval, 300 rows", "0", "$0.00"],
            ["Perf measurement (~1,400 iterations)", "0", "$0.00"],
            ["Local demo (loopback HTTP)", "0", "$0.00"],
            ["Live demo allowance (declared)", "~10", "~$1.00 - not spent"],
            ["TOTAL SPENT", "0", "$0.00"],
        ],
        "rows": [
            ("sp", ""),
            ("b", "Assumptions: stub mode, no keys used, pay-per-token pricing if wired"),
            ("b", "Teaching figures if a model were wired: small chat ~$0.001 per demo run"),
        ],
    },
    {
        "title": "9. What works vs deferred",
        "two_col": {
            "left_title": "Works (evidence linked)",
            "left": [
                "One-command pipeline + eval 1.0000",
                "API: auth, validation, redaction",
                "55 + 12 tests green (captured)",
                "Pins verified, perf measured",
                "Fixtures 300 + 200, no PII",
                "Incident note: drift 0.6833 fixed",
            ],
            "right_title": "Deferred (declared)",
            "right": [
                "Live LLM backend - stub path taken",
                "Real MCP server - fallback reason shown",
                "Docker build - not installed here",
                "Cloud deploy - no creds, docs only",
                "Embeddings - deterministic overlap",
                "Streaming / persistence - out of scope",
            ],
        },
        "rows": [
            ("sp", ""),
            ("b", "Eval caveat: labels share the runtime policy - regression guard, not clinical validation"),
        ],
    },
    {
        "title": "10. Process",
        "rows": [
            ("b", "Git: main = scaffold, feature/module4-capstone = work, merged --no-ff"),
            ("b", "History includes the red -> green fix (06ec11a), not a squashed snapshot"),
            ("b", "Peer review: Alvin Swalah, 12-item checklist, 5 findings - all re-verified"),
            ("b", "CI: .github/workflows/ci.yml runs tests + eval (EVAL SCORE in logs)"),
            ("sp", ""),
            ("h", "Next steps"),
            ("b", "Push the repo, open the PR, present Week 12 Monday"),
            ("b", "Optionally wire a live model behind the same interface (budget ~$1)"),
            ("sp", ""),
            ("c", "Questions?  -  deck, transcript and evidence all live in this repo."),
        ],
    },
]


def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def text_ops(x: float, y: float, text: str, font: str, size: float, color) -> str:
    r, g, b = color
    return (
        f"BT /{font} {size} Tf {r:.3f} {g:.3f} {b:.3f} rg "
        f"1 0 0 1 {x:.1f} {y:.1f} Tm ({esc(text)}) Tj ET"
    )


def rect_ops(x: float, y: float, w: float, h: float, color) -> str:
    r, g, b = color
    return f"{r:.3f} {g:.3f} {b:.3f} rg {x:.1f} {y:.1f} {w:.1f} {h:.1f} re f"


def line_ops(x1: float, y1: float, x2: float, y2: float, color, width: float = 1.0) -> str:
    r, g, b = color
    return (
        f"{r:.3f} {g:.3f} {b:.3f} RG {width:.1f} w "
        f"{x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S"
    )


def wrap(text: str, font: str, size: float, width: float) -> list[str]:
    per_char = 0.60 if font == "F3" else 0.52
    max_chars = max(int(width / (per_char * size)), 8)
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def build_page(slide: dict, index: int, total: int) -> str:
    ops: list[str] = [rect_ops(0, 0, PAGE_W, PAGE_H, WHITE)]

    # Title band
    ops.append(rect_ops(0, PAGE_H - 74, PAGE_W, 74, TEAL))
    ops.append(rect_ops(0, PAGE_H - 80, PAGE_W, 6, AMBER))
    ops.append(text_ops(40, PAGE_H - 50, slide["title"], "F2", 26, WHITE))
    ops.append(text_ops(760, PAGE_H - 46, "AfyaPlus Capstone", "F1", 14, WHITE))

    y = PAGE_H - 116

    if slide.get("code"):
        lines = slide["code"]
        block_h = len(lines) * 17 + 16
        ops.append(rect_ops(40, y - block_h + 20, PAGE_W - 80, block_h, LIGHT))
        yy = y
        for line in lines:
            ops.append(text_ops(56, yy, line, "F3", 12.5, INK))
            yy -= 17
        y = yy - 6

    if slide.get("table"):
        table = slide["table"]
        col_x = [56, 560, 720]
        row_h = 26
        table_top = y
        for r_i, row in enumerate(table):
            row_y = table_top - (r_i + 1) * row_h
            if r_i == 0:
                ops.append(rect_ops(48, row_y - 6, PAGE_W - 96, row_h, TEAL_DARK))
            elif r_i == len(table) - 1:
                ops.append(rect_ops(48, row_y - 6, PAGE_W - 96, row_h, LIGHT))
            color = WHITE if r_i == 0 else INK
            font = "F2" if r_i in (0, len(table) - 1) else "F1"
            for c_i, cell in enumerate(row):
                ops.append(text_ops(col_x[c_i], row_y, cell, font, 15, color))
        y = table_top - len(table) * row_h - 10

    if slide.get("two_col"):
        cols = slide["two_col"]
        col_w = (PAGE_W - 120) / 2
        for side, (title_key, list_key, x0) in enumerate(
            [
                ("left_title", "left", 50),
                ("right_title", "right", 70 + col_w),
            ]
        ):
            ops.append(rect_ops(x0, y - 240, col_w, 264, LIGHT))
            ops.append(rect_ops(x0, y - 240, col_w, 5, TEAL if side == 0 else AMBER))
            ops.append(text_ops(x0 + 14, y - 20, cols[title_key], "F2", 16, INK))
            yy = y - 52
            for item in cols[list_key]:
                for line in wrap(f"- {item}", "F1", 13, col_w - 30):
                    ops.append(text_ops(x0 + 14, yy, line, "F1", 13, INK))
                    yy -= 20
                yy -= 4
        y -= 268

    for kind, text in slide.get("rows", []):
        if kind == "sp":
            y -= 12
        elif kind == "h":
            y -= 10
            ops.append(text_ops(50, y, text, "F2", 16.5, TEAL_DARK))
            y -= 24
        elif kind == "b":
            for line in wrap(f"- {text}", "F1", 14.5, PAGE_W - 120):
                ops.append(text_ops(56, y, line, "F1", 14.5, INK))
                y -= 21
        elif kind == "c":
            for line in wrap(text, "F3", 13, PAGE_W - 140):
                ops.append(rect_ops(48, y - 5, PAGE_W - 96, 22, LIGHT))
                ops.append(text_ops(58, y, line, "F3", 13, TEAL_DARK))
                y -= 22
        elif kind == "kv":
            head, _, tail = text.partition("|")
            ops.append(text_ops(56, y, head, "F2", 13.5, TEAL_DARK))
            ops.append(text_ops(180, y, tail.strip(), "F1", 13.5, INK))
            y -= 23

    # Footer
    if y < 56:
        print(f"warning: slide '{slide['title']}' content ends at y={y:.0f} (footer zone)", file=sys.stderr)
    ops.append(line_ops(40, 46, PAGE_W - 40, 46, (0.85, 0.87, 0.89), 1.0))
    ops.append(
        text_ops(40, 26, "Module 4 Capstone - presented Week 12 Monday", "F1", 11, GRAY)
    )
    ops.append(text_ops(880, 26, f"{index} / {total}", "F1", 11, GRAY))
    return "\n".join(ops)


def build_pdf(slides: list[dict], path: Path) -> None:
    """Assemble a minimal but valid PDF: catalog(1), pages(2), fonts(3-5),
    then per slide a content stream (6,8,...) and a page (7,9,...)."""
    total = len(slides)
    objects: dict[int, bytes] = {}

    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[3] = (
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
        b"/Encoding /WinAnsiEncoding >>"
    )
    objects[4] = (
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
        b"/Encoding /WinAnsiEncoding >>"
    )
    objects[5] = (
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier "
        b"/Encoding /WinAnsiEncoding >>"
    )

    page_ids: list[int] = []
    for index, slide in enumerate(slides):
        content_id = 6 + 2 * index
        page_id = 7 + 2 * index
        page_ids.append(page_id)

        content = build_page(slide, index + 1, total).encode("latin-1", "replace")
        objects[content_id] = (
            f"<< /Length {len(content)} >>\nstream\n".encode("ascii")
            + content
            + b"\nendstream"
        )
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        ).encode("ascii")

    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects[2] = f"<< /Type /Pages /Kids [{kids}] /Count {total} >>".encode("ascii")

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets: dict[int, int] = {}
    for num in sorted(objects):
        offsets[num] = len(out)
        out += f"{num} 0 obj\n".encode("ascii")
        out += objects[num]
        out += b"\nendobj\n"

    xref_pos = len(out)
    size = len(objects) + 1
    out += f"xref\n0 {size}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for num in range(1, size):
        out += f"{offsets[num]:010d} 00000 n \n".encode("ascii")
    out += (
        f"trailer\n<< /Size {size} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode("ascii")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(out))


def main() -> int:
    build_pdf(SLIDES, OUTPUT)
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)} ({len(SLIDES)} slides)")

    # Self-check with pypdf when available.
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(OUTPUT))
        assert len(reader.pages) == len(SLIDES), "page count mismatch"
        first = reader.pages[0].extract_text() or ""
        assert "Problem and user" in first, "slide 1 text missing"
        last = reader.pages[-1].extract_text() or ""
        assert "Process" in last, "slide 10 text missing"
        print(f"verified: {len(reader.pages)} pages, text extractable")
    except ImportError:
        print("pypdf not available - skipped text verification")
    return 0


if __name__ == "__main__":
    sys.exit(main())
