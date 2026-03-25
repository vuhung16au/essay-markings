"""Compare live grading results with expected outputs using tolerance bands."""

from __future__ import annotations

import json
from pathlib import Path
from urllib import request


ROOT = Path(__file__).resolve().parents[1]
API_URL = "http://127.0.0.1:8000/api/grade-essay"
PER_SCORE_TOLERANCE = 1
TOTAL_TOLERANCE = 3


def load_json(path: str) -> object:
    return json.loads((ROOT / path).read_text())


def post_grade(question: str, essay: str) -> dict:
    payload = json.dumps({"question": question, "essay": essay}).encode("utf-8")
    http_request = request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(http_request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    questions = {item["id"]: item["question"] for item in load_json("data/sample_questions.json")}
    essays = load_json("data/sample_essays.json")
    expected = {item["essay_id"]: item["response"] for item in load_json("data/expected_outputs.json")}

    overall_pass = True

    for essay in essays:
        actual = post_grade(questions[essay["question_id"]], essay["text"])
        target = expected[essay["id"]]

        actual_total = sum(item["score"] for item in actual["scores"].values())
        expected_total = sum(item["score"] for item in target["scores"].values())
        total_ok = abs(actual_total - expected_total) <= TOTAL_TOLERANCE

        mismatches: list[str] = []
        for key, expected_score in target["scores"].items():
            actual_score = actual["scores"][key]["score"]
            if abs(actual_score - expected_score["score"]) > PER_SCORE_TOLERANCE:
                mismatches.append(
                    f"{key}: actual={actual_score} expected={expected_score['score']}"
                )

        passed = total_ok
        overall_pass = overall_pass and passed

        status = "PASS" if passed else "FAIL"
        print(
            f"essay {essay['id']} [{essay['quality_level']}] -> {status} | "
            f"actual_total={actual_total} expected_total={expected_total}"
        )
        if not total_ok:
            print("  total difference exceeded tolerance")
        for mismatch in mismatches:
            print(f"  {mismatch}")

    print(f"\noverall={'PASS' if overall_pass else 'FAIL'}")


if __name__ == "__main__":
    main()
