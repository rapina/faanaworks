#!/usr/bin/env python3
"""블로그 글의 최소 계약을 외부 의존성 없이 검사한다."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
REQUIRED = {"layout", "title", "date", "project", "summary", "cover", "source"}


def front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("YAML front matter가 없다")
    try:
        block = text.split("---\n", 2)[1]
    except IndexError as exc:
        raise ValueError("YAML front matter가 닫히지 않았다") from exc
    values: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"')
    return values


def main() -> int:
    problems: list[str] = []
    for post in sorted(POSTS.glob("*.md")):
        try:
            meta = front_matter(post)
        except ValueError as exc:
            problems.append(f"{post.relative_to(ROOT)}: {exc}")
            continue
        missing = REQUIRED - meta.keys()
        if missing:
            problems.append(f"{post.relative_to(ROOT)}: 메타데이터 누락 {sorted(missing)}")
        cover = meta.get("cover", "").lstrip("/")
        if cover and not (ROOT / cover).is_file():
            problems.append(f"{post.relative_to(ROOT)}: 대표 이미지 없음 {cover}")
        body = post.read_text(encoding="utf-8")
        if "<figure>" not in body:
            problems.append(f"{post.relative_to(ROOT)}: 본문 화면 이미지가 없다")
        for image in re.findall(r"'/([^']+\.(?:png|jpg|jpeg|webp))'", body):
            if not (ROOT / image).is_file():
                problems.append(f"{post.relative_to(ROOT)}: 이미지 없음 {image}")
    if not list(POSTS.glob("*.md")):
        problems.append("게시글이 없다")
    if problems:
        print("\n".join(f"[SITE] {problem}" for problem in problems))
        return 1
    print(f"[SITE] OK · 글 {len(list(POSTS.glob('*.md')))}편")
    return 0


if __name__ == "__main__":
    sys.exit(main())
