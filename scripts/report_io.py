"""Helpers for writing local Markdown reports."""

from __future__ import annotations

from pathlib import Path


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_markdown_report(path: Path, content: str) -> Path:
    ensure_parent_dir(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return path
