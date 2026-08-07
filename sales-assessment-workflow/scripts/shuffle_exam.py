#!/usr/bin/env python3
"""Create a deterministic shuffled exam version and answer key from JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "assessment"


def letter(index: int) -> str:
    if index < 0 or index >= 26:
        raise ValueError("A question may have at most 26 answer choices")
    return chr(ord("A") + index)


def validate(source: dict[str, Any]) -> None:
    if not isinstance(source.get("assessment_name"), str) or not source["assessment_name"].strip():
        raise ValueError("assessment_name must be a non-empty string")
    questions = source.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ValueError("questions must be a non-empty list")

    for number, question in enumerate(questions, 1):
        if not isinstance(question.get("prompt"), str) or not question["prompt"].strip():
            raise ValueError(f"Question {number}: prompt must be a non-empty string")
        options = question.get("options")
        correct = question.get("correct")
        if not isinstance(options, list) or len(options) < 2:
            raise ValueError(f"Question {number}: options must contain at least two choices")
        if len(options) > 26 or not all(isinstance(item, str) and item.strip() for item in options):
            raise ValueError(f"Question {number}: options must be 2-26 non-empty strings")
        if not isinstance(correct, list) or not correct:
            raise ValueError(f"Question {number}: correct must be a non-empty list of zero-based indexes")
        if not all(isinstance(item, int) and 0 <= item < len(options) for item in correct):
            raise ValueError(f"Question {number}: correct contains an invalid option index")
        if len(set(correct)) != len(correct):
            raise ValueError(f"Question {number}: correct contains duplicate indexes")
        points = question.get("points", 1)
        if not isinstance(points, (int, float)) or points <= 0:
            raise ValueError(f"Question {number}: points must be positive")


def shuffle_question(question: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    options = question["options"]
    order = list(range(len(options)))
    rng.shuffle(order)
    if len(order) > 1 and order == list(range(len(options))):
        order = order[1:] + order[:1]

    correct_source = set(question["correct"])
    correct_letters = [letter(new_index) for new_index, source_index in enumerate(order) if source_index in correct_source]

    return {
        "prompt": question["prompt"],
        "points": question.get("points", 1),
        "shuffled_options": [options[source_index] for source_index in order],
        "correct_letters": correct_letters,
        "source_index_order": order,
    }


def render_markdown(version: dict[str, Any]) -> str:
    lines = [f"*{version['assessment_name']}*", ""]
    for number, question in enumerate(version["questions"], 1):
        lines.append(f"{number}. {question['prompt']}")
        for option_index, option in enumerate(question["shuffled_options"]):
            lines.append(f"   {letter(option_index)}. {option}")
        lines.append("")
    lines.append("*Please reply with your answers in the thread under this message. Answers submitted outside this assessment thread will not be graded.*")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Source assessment JSON")
    parser.add_argument("--candidate", required=True, help="Candidate name")
    parser.add_argument("--attempt", required=True, type=int, help="Attempt number, starting at 1")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for version JSON and Markdown")
    parser.add_argument("--seed", default="", help="Optional extra seed material")
    args = parser.parse_args()

    if args.attempt < 1:
        raise ValueError("attempt must be at least 1")

    source = json.loads(args.input.read_text(encoding="utf-8"))
    validate(source)

    seed_material = f"{source['assessment_name']}|{args.candidate}|{args.attempt}|{args.seed}"
    digest = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()
    rng = random.Random(int(digest, 16))
    version_id = f"{slugify(source['assessment_name'])}-{slugify(args.candidate)}-a{args.attempt}-{digest[:10]}"

    questions = [shuffle_question(question, rng) for question in source["questions"]]
    total_points = sum(question["points"] for question in questions)
    version = {
        "version_id": version_id,
        "assessment_name": source["assessment_name"],
        "candidate_name": args.candidate,
        "attempt_number": args.attempt,
        "question_count": len(questions),
        "total_points": total_points,
        "questions": questions,
        "answer_key": {str(number): question["correct_letters"] for number, question in enumerate(questions, 1)},
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = slugify(version_id)
    json_path = args.output_dir / f"{stem}.json"
    md_path = args.output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(version, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(version) + "\n", encoding="utf-8")

    print(json.dumps({"version_id": version_id, "json": str(json_path), "markdown": str(md_path), "answer_key": version["answer_key"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
