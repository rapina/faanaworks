#!/usr/bin/env python3
"""블로그 글의 최소 계약을 외부 의존성 없이 검사한다."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
SUBJECTS = ROOT / "_data" / "subjects.yml"
REQUIRED = {"layout", "title", "date", "project", "summary", "cover"}


def known_subjects() -> set[str]:
    text = SUBJECTS.read_text(encoding="utf-8")
    return set(re.findall(r'^- id:\s*"([^"]+)"', text, re.MULTILINE))


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
    subjects = known_subjects()
    used: set[str] = set()
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
        subject = meta.get("subject", "")
        if subject:
            used.add(subject)
            if subject not in subjects:
                problems.append(f"{post.relative_to(ROOT)}: _data/subjects.yml에 없는 subject {subject}")
        body = post.read_text(encoding="utf-8")
        if "<figure>" not in body:
            problems.append(f"{post.relative_to(ROOT)}: 본문 화면 이미지가 없다")
        for image in re.findall(r"'/([^']+\.(?:png|jpg|jpeg|webp))'", body):
            if not (ROOT / image).is_file():
                problems.append(f"{post.relative_to(ROOT)}: 이미지 없음 {image}")
        clips = re.findall(r"'/([^']+\.mp4)'", body)
        for clip in clips:
            path = ROOT / clip
            if not path.is_file():
                problems.append(f"{post.relative_to(ROOT)}: 영상 없음 {clip}")
            elif path.stat().st_size > 2 * 1024 * 1024:
                size = path.stat().st_size / 1024 / 1024
                problems.append(f"{post.relative_to(ROOT)}: 영상 2MB 초과 {clip} ({size:.1f}MB)")
        # 키 영상은 한 개다. 둘이 되면 글이 아니라 재생 목록이 된다 (AGENTS.md).
        if len(set(clips)) > 1:
            problems.append(f"{post.relative_to(ROOT)}: 영상이 둘 이상 {sorted(set(clips))}")
    if not list(POSTS.glob("*.md")):
        problems.append("게시글이 없다")
    for stale in sorted(subjects - used):
        problems.append(f"_data/subjects.yml: 쓰는 글이 없는 subject {stale}")
    if problems:
        print("\n".join(f"[SITE] {problem}" for problem in problems))
        return 1
    print(f"[SITE] OK · 글 {len(list(POSTS.glob('*.md')))}편 · 괴이 {len(used)}종")
    return 0


if __name__ == "__main__":
    sys.exit(main())
