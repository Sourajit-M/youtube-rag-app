import os
import sys
import json
import csv
from datetime import datetime
from pathlib import Path
import groq

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.generate import generate_answer

client = groq.Groq(api_key=GROQ_API_KEY)

RAGAS_JUDGE_PROMPT = """You are an expert RAG evaluation judge. Rate the Generated Answer against the 4 RAGAS metrics on a scale from 0.0 to 1.0.

Metrics:
1. faithfulness:
   - Are the factual claims in the Generated Answer supported by the retrieved Context Excerpts?
   - If the User Question is out-of-domain and the answer properly states "not covered", give 1.0.
   - 1.0 = fully grounded, 0.0 = hallucinated.

2. answer_relevancy:
   - Does the Generated Answer directly address the User Question?
   - 1.0 = completely relevant, 0.0 = off-topic or evasive.

3. context_precision:
   - Are the retrieved Context Excerpts relevant to the User Question?
   - 1.0 = retrieved chunks are on-topic, 0.0 = completely irrelevant chunks.

4. context_recall:
   - Does the retrieved context contain the key information specified in the Ground Truth?
   - 1.0 = all key concepts present, 0.0 = missing necessary information.

You must respond in valid JSON with this exact schema:
{
  "faithfulness": 1.0,
  "answer_relevancy": 1.0,
  "context_precision": 0.9,
  "context_recall": 0.9,
  "reasoning": "brief explanation"
}
"""

def evaluate_ragas_metrics(question: str, ground_truth: str, answer: str, context_snippets: list[str]) -> dict:
    """Uses Groq in native JSON mode to calculate the 4 RAGAS metrics."""
    context_str = "\n".join(f"[{i+1}] {s}" for i, s in enumerate(context_snippets))
    user_prompt = f"""
User Question: {question}
Ground Truth: {ground_truth}

Retrieved Context Excerpts:
{context_str}

Generated Answer:
{answer}
"""
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": RAGAS_JUDGE_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},  # Native JSON mode prevents parse errors
            temperature=0.0,
            max_tokens=1000,  # Prevents token truncation
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        print(f"  [Judge Error]: {e}")
        return {
            "faithfulness": 0.0,
            "answer_relevancy": 0.0,
            "context_precision": 0.0,
            "context_recall": 0.0,
            "reasoning": str(e),
        }


def run_ragas_benchmark(golden_set_path: str = "backend/golden_dataset.json"):
    """Runs the 15-question evaluation benchmark and logs results to CSV."""
    if not Path(golden_set_path).exists():
        golden_set_path = "backend/golden_set.json"

    with open(golden_set_path, "r", encoding="utf-8") as f:
        golden_set = json.load(f)

    print(f"\n=======================================================")
    print(f"  RAGAS Evaluation Harness ({len(golden_set)} Test Cases)")
    print(f"  Judge LLM: Groq ({GROQ_MODEL}) [JSON Mode Enabled]")
    print(f"=======================================================\n")

    f_scores, r_scores, cp_scores, cr_scores = [], [], [], []

    for item in golden_set:
        qid = item["id"]
        q = item["question"]
        gt = item["ground_truth"]
        src = item.get("video_source", "Mixed")

        print(f"[{qid}] [{src}] '{q}'")
        rag_res = generate_answer(query=q)
        answer = rag_res["answer"]
        context_excerpts = rag_res.get("context_excerpts") or [c.get("context", c.get("snippet", "")) for c in rag_res.get("citations", [])]
        scores = evaluate_ragas_metrics(q, gt, answer, context_excerpts)
        f = float(scores.get("faithfulness", 0.0))
        r = float(scores.get("answer_relevancy", 0.0))
        cp = float(scores.get("context_precision", 0.0))
        cr = float(scores.get("context_recall", 0.0))

        f_scores.append(f)
        r_scores.append(r)
        cp_scores.append(cp)
        cr_scores.append(cr)

        print(f"  |-> Faithfulness:       {f:.2f}")
        print(f"  |-> Answer Relevancy:   {r:.2f}")
        print(f"  |-> Context Precision:  {cp:.2f}")
        print(f"  |-> Context Recall:     {cr:.2f}")
        print(f"  Reasoning: {scores.get('reasoning', '')}\n")

    avg_f = sum(f_scores) / len(f_scores)
    avg_r = sum(r_scores) / len(r_scores)
    avg_cp = sum(cp_scores) / len(cp_scores)
    avg_cr = sum(cr_scores) / len(cr_scores)
    overall_ragas = (avg_f + avg_r + avg_cp + avg_cr) / 4

    print("=======================================================")
    print("                 RAGAS BENCHMARK SUMMARY")
    print("=======================================================")
    print(f"  Faithfulness:        {avg_f:.3f} / 1.000")
    print(f"  Answer Relevancy:    {avg_r:.3f} / 1.000")
    print(f"  Context Precision:   {avg_cp:.3f} / 1.000")
    print(f"  Context Recall:      {avg_cr:.3f} / 1.000")
    print(f"  ---------------------------------------------")
    print(f"  Overall RAGAS Score: {overall_ragas:.3f} / 1.000")
    print("=======================================================\n")

    # Append to CSV log
    csv_file = "eval_results.csv"
    file_exists = Path(csv_file).exists()
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "judge_model", "test_cases",
                "faithfulness", "answer_relevancy",
                "context_precision", "context_recall", "overall_ragas_score"
            ])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            GROQ_MODEL,
            len(golden_set),
            round(avg_f, 3),
            round(avg_r, 3),
            round(avg_cp, 3),
            round(avg_cr, 3),
            round(overall_ragas, 3),
        ])
    print(f"✓ Results logged to {csv_file}")


if __name__ == "__main__":
    run_ragas_benchmark()