#!/usr/bin/env python3
"""
Citation Health Evaluator — Objective Semantic Similarity Assessment
====================================================================
Uses cross-encoder/stsb-roberta-base (STSbenchmark, 90.17% accuracy on STS)
to evaluate whether cited references are semantically relevant to paragraph content.

Algorithm: Cross-Encoder Semantic Textual Similarity
  - Model: cross-encoder/stsb-roberta-base (Sentence-Transformers, HuggingFace)
  - Trained on: STSbenchmark (5749 sentence pairs, human-annotated 0-5 similarity)
  - Output: Continuous 0–1 score per (paragraph, reference) pair
  - Justification: Cross-encoders jointly encode both texts through the full
    transformer attention mechanism, enabling richer interaction modeling than
    bi-encoder cosine similarity. This model is the academic standard for
    pairwise semantic similarity evaluation (MTEB STS category).

Scoring Thresholds (fixed, for paragraph ↔ bibliographic-reference pairs):
  - STRONG  (≥ 0.40): Clear semantic connection. Reference is directly relevant.
  - MODERATE (0.25–0.39): Topical overlap. Reference covers related material.
  - WEAK    (0.12–0.24): Marginal connection. Citation is a stretch.
  - INVALID (< 0.12): No meaningful semantic link. Citation appears irrelevant.

  Threshold rationale: Bibliographic reference strings (author, title, description)
  are inherently shorter and more abstract than content paragraphs. A score of 0.40+
  on the STS cross-encoder indicates strong topical alignment despite this asymmetry.
  Thresholds are set conservatively — a score of 0.25 is the minimum for a
  defensible citation in an academic context.

Per-Paragraph Health Grades:
  - GREEN paragraphs (claim direct citation):
      · PASS if best cited ref scores ≥ 0.25 (MODERATE+)
      · FAIL if best cited ref scores < 0.25
  - YELLOW paragraphs (no direct citation):
      · COVERED if best reference in file scores ≥ 0.20
      · UNCOVERED if no reference scores ≥ 0.20

Per-File Health Score:
  = (passing_green + covered_yellow) / total_cited_paragraphs × 100

Author: Automated evaluation tool (no self-scoring — model does all scoring)
Date: 2026-04-04
"""

import json
import os
import re
import sys
import time
import argparse
from pathlib import Path

# ── CLI Arguments ──────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(
    description="Evaluate citation health using cross-encoder semantic similarity.",
    epilog="Example: python %(prog)s --write   (evaluate and update MDX files)",
)
parser.add_argument(
    "--write",
    action="store_true",
    help="Update MDX files: downgrade green→yellow if citation fails, yellow→red if uncovered.",
)
args = parser.parse_args()

# ── Model Loading ──────────────────────────────────────────────────────────
print("Loading cross-encoder/stsb-roberta-base ...", flush=True)
t0 = time.time()

from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/stsb-roberta-base")
print(f"Model loaded in {time.time() - t0:.1f}s", flush=True)

# ── Thresholds (fixed, documented above) ──────────────────────────────────
STRONG_THRESHOLD = 0.40
MODERATE_THRESHOLD = 0.25
WEAK_THRESHOLD = 0.12
YELLOW_COVERAGE_THRESHOLD = 0.20

# ── Content Root ──────────────────────────────────────────────────────────
CONTENT_ROOT = Path(__file__).resolve().parent.parent / "src" / "content"
COLLECTIONS = ["myths", "civilizations", "languages"]

# ── Parsing Helpers ───────────────────────────────────────────────────────

def strip_mdx_markup(text: str) -> str:
    """Remove MDX/HTML tags, Ref components, markdown formatting to get plain text."""
    # Remove <Ref id={N} /> tags
    text = re.sub(r'<Ref\s+id=\{?\d+\}?\s*/>', '', text)
    # Remove HTML/MDX tags but keep content
    text = re.sub(r'<[^>]+>', '', text)
    # Remove markdown bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # Remove markdown links, keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove markdown table formatting
    text = re.sub(r'\|', ' ', text)
    text = re.sub(r'-{3,}', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_references(content: str) -> dict[int, str]:
    """Extract { id: text } map from <References references={[...]} />."""
    refs = {}
    # Find the References block
    ref_match = re.search(
        r'<References\s+references=\{(\[[\s\S]*?\])\}\s*/>',
        content
    )
    if not ref_match:
        return refs

    block = ref_match.group(1)
    # Parse individual reference entries
    for m in re.finditer(r'id:\s*(\d+)\s*,\s*text:\s*["\'](.+?)["\']', block):
        ref_id = int(m.group(1))
        ref_text = m.group(2)
        # Unescape
        ref_text = ref_text.replace('\\"', '"').replace("\\'", "'")
        refs[ref_id] = ref_text

    return refs


def parse_cited_blocks(content: str) -> list[dict]:
    """Extract all <Cited> blocks with their status, text, and ref ids."""
    blocks = []
    pattern = re.compile(
        r'<Cited\s+status="(green|yellow|red)">([\s\S]*?)</Cited>',
        re.MULTILINE
    )
    for m in pattern.finditer(content):
        status = m.group(1)
        inner = m.group(2)

        # Extract Ref ids from inner content
        ref_ids = [int(r) for r in re.findall(r'<Ref\s+id=\{?(\d+)\}?\s*/>', inner)]

        plain_text = strip_mdx_markup(inner)

        if len(plain_text) < 10:
            continue  # Skip trivially short blocks (tables, etc. that collapse)

        blocks.append({
            "status": status,
            "text": plain_text,
            "ref_ids": ref_ids,
            "char_length": len(plain_text),
        })

    return blocks


# ── Evaluation Engine ─────────────────────────────────────────────────────

def compute_verdicts(cited_blocks: list[dict], references: dict, pairs_to_score, pair_metadata, scores):
    """Compute verdicts for each paragraph. Returns (results, counters, para_scores)."""
    # Aggregate scores per paragraph
    para_scores: dict[int, dict] = {}
    for idx, (ptype, para_idx, ref_id) in enumerate(pair_metadata):
        score = float(scores[idx])
        if para_idx not in para_scores:
            para_scores[para_idx] = {"type": ptype, "ref_scores": []}
        para_scores[para_idx]["ref_scores"].append({
            "ref_id": ref_id,
            "ref_text": references.get(ref_id, "?")[:80],
            "similarity": round(score, 4),
        })

    green_pass = 0
    green_fail = 0
    yellow_covered = 0
    yellow_uncovered = 0
    total_evaluated = 0
    results = []

    for i, block in enumerate(cited_blocks):
        para_result = {
            "index": i,
            "status": block["status"],
            "text_preview": block["text"][:120] + ("..." if len(block["text"]) > 120 else ""),
            "char_length": block["char_length"],
        }

        if i in para_scores:
            total_evaluated += 1
            ref_scores = para_scores[i]["ref_scores"]
            best = max(ref_scores, key=lambda x: x["similarity"])
            para_result["best_match"] = best
            para_result["all_scores"] = sorted(ref_scores, key=lambda x: -x["similarity"])

            if block["status"] == "green":
                if best["similarity"] >= MODERATE_THRESHOLD:
                    para_result["verdict"] = "PASS"
                    para_result["grade"] = (
                        "STRONG" if best["similarity"] >= STRONG_THRESHOLD
                        else "MODERATE"
                    )
                    green_pass += 1
                else:
                    para_result["verdict"] = "FAIL"
                    para_result["grade"] = (
                        "WEAK" if best["similarity"] >= WEAK_THRESHOLD
                        else "INVALID"
                    )
                    green_fail += 1
            elif block["status"] == "yellow":
                if best["similarity"] >= YELLOW_COVERAGE_THRESHOLD:
                    para_result["verdict"] = "COVERED"
                    yellow_covered += 1
                else:
                    para_result["verdict"] = "UNCOVERED"
                    yellow_uncovered += 1
        else:
            para_result["verdict"] = "NO_REFS"
            if block["status"] != "red":
                total_evaluated += 1

        results.append(para_result)

    counters = {
        "green_pass": green_pass,
        "green_fail": green_fail,
        "yellow_covered": yellow_covered,
        "yellow_uncovered": yellow_uncovered,
        "total_evaluated": total_evaluated,
    }
    return results, counters, para_scores

def evaluate_file(filepath: Path, write_mode: bool = False) -> dict:
    """Evaluate a single MDX file. Returns detailed per-paragraph scores.
    If write_mode=True, updates the file: downgrades failing citations."""
    content = filepath.read_text(encoding="utf-8")
    references = parse_references(content)
    cited_blocks = parse_cited_blocks(content)

    if not cited_blocks:
        return {
            "file": str(filepath.relative_to(CONTENT_ROOT)),
            "total_paragraphs": 0,
            "references_count": len(references),
            "health_score": None,
            "paragraphs": [],
            "error": "No Cited blocks found",
        }

    pairs_to_score = []
    pair_metadata = []

    # Collect all (paragraph, reference) pairs for batch scoring
    for i, block in enumerate(cited_blocks):
        if block["status"] == "green" and block["ref_ids"]:
            for ref_id in block["ref_ids"]:
                if ref_id in references:
                    pairs_to_score.append((block["text"], references[ref_id]))
                    pair_metadata.append(("green_cited", i, ref_id))
        elif block["status"] == "yellow":
            for ref_id, ref_text in references.items():
                pairs_to_score.append((block["text"], ref_text))
                pair_metadata.append(("yellow_any", i, ref_id))
        elif block["status"] == "green" and not block["ref_ids"]:
            for ref_id, ref_text in references.items():
                pairs_to_score.append((block["text"], ref_text))
                pair_metadata.append(("green_nocite", i, ref_id))

    # Batch score with cross-encoder
    if pairs_to_score:
        scores = model.predict(pairs_to_score)
    else:
        scores = []

    results, counters, para_scores = compute_verdicts(
        cited_blocks, references, pairs_to_score, pair_metadata, scores
    )

    # ── Write mode: update MDX file with corrected statuses ────────────
    writes_applied = 0
    if write_mode:
        updated_content = content
        for para_result in results:
            old_status = para_result["status"]
            verdict = para_result.get("verdict", "")
            new_status = None

            if old_status == "green" and verdict == "FAIL":
                new_status = "yellow"
            elif old_status == "yellow" and verdict == "UNCOVERED":
                new_status = "red"

            if new_status:
                # Find the N-th Cited block in the file and replace its status
                # We match by text preview to ensure we target the right block
                idx = para_result["index"]
                # Use a counter-based approach to find the exact occurrence
                count = 0
                pos = 0
                target_pattern = re.compile(r'<Cited\s+status="(green|yellow|red)">')
                while pos < len(updated_content):
                    m = target_pattern.search(updated_content, pos)
                    if not m:
                        break
                    if count == idx:
                        old_tag = m.group(0)
                        new_tag = f'<Cited status="{new_status}">'
                        updated_content = (
                            updated_content[:m.start()]
                            + new_tag
                            + updated_content[m.end():]
                        )
                        writes_applied += 1
                        para_result["updated_to"] = new_status
                        break
                    count += 1
                    pos = m.end()

        if writes_applied > 0:
            filepath.write_text(updated_content, encoding="utf-8")

    # Compute file health
    te = counters["total_evaluated"]
    health = None
    if te > 0:
        health = round(
            (counters["green_pass"] + counters["yellow_covered"]) / te * 100, 1
        )

    return {
        "file": str(filepath.relative_to(CONTENT_ROOT)),
        "total_paragraphs": len(cited_blocks),
        "green_paragraphs": sum(1 for b in cited_blocks if b["status"] == "green"),
        "yellow_paragraphs": sum(1 for b in cited_blocks if b["status"] == "yellow"),
        "red_paragraphs": sum(1 for b in cited_blocks if b["status"] == "red"),
        "references_count": len(references),
        "green_pass": counters["green_pass"],
        "green_fail": counters["green_fail"],
        "yellow_covered": counters["yellow_covered"],
        "yellow_uncovered": counters["yellow_uncovered"],
        "health_score": health,
        "writes_applied": writes_applied,
        "paragraphs": results,
    }


# ── Main Runner ───────────────────────────────────────────────────────────

def main():
    write_mode = args.write
    if write_mode:
        print("*** WRITE MODE: will update MDX files based on evaluation ***\n", flush=True)

    all_results = []
    total_files = 0
    total_writes = 0

    for collection in COLLECTIONS:
        coll_dir = CONTENT_ROOT / collection
        if not coll_dir.exists():
            continue
        files = sorted(coll_dir.glob("*.mdx"))
        for filepath in files:
            total_files += 1
            print(f"  [{total_files}] {filepath.relative_to(CONTENT_ROOT)} ...", end=" ", flush=True)
            result = evaluate_file(filepath, write_mode=write_mode)
            h = result["health_score"]
            h_str = f"{h}%" if h is not None else "N/A"
            w = result.get("writes_applied", 0)
            w_str = f"  wrote:{w}" if w > 0 else ""
            total_writes += w
            print(f"health={h_str}  (G:{result.get('green_pass',0)}/{result.get('green_paragraphs',0)} Y:{result.get('yellow_covered',0)}/{result.get('yellow_paragraphs',0)}){w_str}", flush=True)
            all_results.append(result)

    # ── Summary Statistics ─────────────────────────────────────────────
    scored = [r for r in all_results if r["health_score"] is not None]
    if not scored:
        print("\nNo files with citation data found.")
        return

    health_scores = [r["health_score"] for r in scored]
    avg_health = sum(health_scores) / len(health_scores)

    total_green = sum(r.get("green_paragraphs", 0) for r in all_results)
    total_yellow = sum(r.get("yellow_paragraphs", 0) for r in all_results)
    total_green_pass = sum(r.get("green_pass", 0) for r in all_results)
    total_green_fail = sum(r.get("green_fail", 0) for r in all_results)
    total_yellow_covered = sum(r.get("yellow_covered", 0) for r in all_results)
    total_yellow_uncovered = sum(r.get("yellow_uncovered", 0) for r in all_results)

    failing_files = [r for r in scored if r["health_score"] < 50]
    weak_files = [r for r in scored if 50 <= r["health_score"] < 75]

    print("\n" + "=" * 72)
    print("CITATION HEALTH EVALUATION REPORT")
    print("=" * 72)
    print(f"Model:       cross-encoder/stsb-roberta-base (STS accuracy: 90.17%)")
    print(f"Threshold:   Green PASS ≥ 0.25 | Yellow COVERED ≥ 0.20")
    print(f"Date:        {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 72)
    print(f"Files evaluated:      {len(scored)}")
    print(f"Average health:       {avg_health:.1f}%")
    print(f"Median health:        {sorted(health_scores)[len(health_scores)//2]:.1f}%")
    print(f"Min health:           {min(health_scores):.1f}%")
    print(f"Max health:           {max(health_scores):.1f}%")
    print("-" * 72)
    print(f"GREEN paragraphs:     {total_green}")
    print(f"  PASS (≥0.25):       {total_green_pass}  ({total_green_pass/max(total_green,1)*100:.1f}%)")
    print(f"  FAIL (<0.25):       {total_green_fail}  ({total_green_fail/max(total_green,1)*100:.1f}%)")
    print(f"YELLOW paragraphs:    {total_yellow}")
    print(f"  COVERED (≥0.20):    {total_yellow_covered}  ({total_yellow_covered/max(total_yellow,1)*100:.1f}%)")
    print(f"  UNCOVERED (<0.20):  {total_yellow_uncovered}  ({total_yellow_uncovered/max(total_yellow,1)*100:.1f}%)")
    print("-" * 72)

    if failing_files:
        print(f"\nFAILING FILES (<50% health): {len(failing_files)}")
        for r in sorted(failing_files, key=lambda x: x["health_score"]):
            print(f"  {r['file']:50s}  {r['health_score']}%")
            # Show failed paragraphs
            for p in r["paragraphs"]:
                if p.get("verdict") in ("FAIL", "UNCOVERED"):
                    best = p.get("best_match", {})
                    print(f"    ✗ [{p['status'].upper()}] sim={best.get('similarity','?'):.3f} | {p['text_preview'][:80]}")

    if weak_files:
        print(f"\nWEAK FILES (50–74% health): {len(weak_files)}")
        for r in sorted(weak_files, key=lambda x: x["health_score"]):
            print(f"  {r['file']:50s}  {r['health_score']}%")

    passing_files = [r for r in scored if r["health_score"] >= 75]
    print(f"\nPASSING FILES (≥75%):  {len(passing_files)}")
    print(f"WEAK FILES (50–74%):   {len(weak_files)}")
    print(f"FAILING FILES (<50%):  {len(failing_files)}")
    if write_mode:
        print(f"\n*** WRITE MODE: {total_writes} status downgrades applied across {sum(1 for r in all_results if r.get('writes_applied', 0) > 0)} files ***")
    # Distribution histogram
    print("\nHealth Distribution:")
    bins = [(0, 25), (25, 50), (50, 75), (75, 100), (100, 101)]
    labels = ["0-24%", "25-49%", "50-74%", "75-99%", "100%"]
    for (lo, hi), label in zip(bins, labels):
        count = sum(1 for h in health_scores if lo <= h < hi)
        bar = "█" * count
        print(f"  {label:>6s} | {bar} {count}")

    # Save detailed JSON report
    report = {
        "meta": {
            "model": "cross-encoder/stsb-roberta-base",
            "sts_accuracy": "90.17%",
            "green_pass_threshold": MODERATE_THRESHOLD,
            "yellow_coverage_threshold": YELLOW_COVERAGE_THRESHOLD,
            "strong_threshold": STRONG_THRESHOLD,
            "weak_threshold": WEAK_THRESHOLD,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
        "summary": {
            "files_evaluated": len(scored),
            "average_health": round(avg_health, 1),
            "median_health": round(sorted(health_scores)[len(health_scores)//2], 1),
            "min_health": round(min(health_scores), 1),
            "max_health": round(max(health_scores), 1),
            "total_green": total_green,
            "green_pass": total_green_pass,
            "green_fail": total_green_fail,
            "total_yellow": total_yellow,
            "yellow_covered": total_yellow_covered,
            "yellow_uncovered": total_yellow_uncovered,
            "failing_files": len(failing_files),
            "weak_files": len(weak_files),
            "passing_files": len(passing_files),
        },
        "files": all_results,
    }

    report_path = Path(__file__).resolve().parent / "citation-health-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDetailed report saved to: {report_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
