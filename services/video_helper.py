"""動画表示ヘルパー"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import streamlit as st
from streamlit.components.v1 import html as components_html


VIDEO_ROOT = Path("assets/videos")
DEFAULT_EXTENSIONS: Iterable[str] = (".mp4", ".webm", ".mov", ".m4v")


def _get_candidate_paths(category: str, base_name: str) -> Iterable[Path]:
    category_path = VIDEO_ROOT / category if category else VIDEO_ROOT
    if base_name.lower().endswith(tuple(DEFAULT_EXTENSIONS)):
        yield category_path / base_name
    else:
        for ext in DEFAULT_EXTENSIONS:
            yield category_path / f"{base_name}{ext}"


def display_video(
    category: str,
    base_name: str,
    caption: str | None = None,
    *,
    autoplay: bool = False,
    loop: bool = True,
    muted: bool = True,
    controls: bool = True,
    height: int | None = None,
) -> bool:
    """カテゴリとベース名から動画を探して表示する。autoplay 対応。"""

    for candidate in _get_candidate_paths(category, base_name):
        if not candidate.exists():
            continue

        st.video(str(candidate))

        if autoplay or loop or not controls or muted:
            controls_js = "target.setAttribute('controls','');" if controls else "target.removeAttribute('controls');"
            script = (
                "<script>"
                "const vids = window.parent.document.querySelectorAll('video');"
                "const target = vids[vids.length - 1];"
                "if (target && !target.dataset.autoplayHandled) {"
                "target.dataset.autoplayHandled = 'true';"
                f"target.muted = {str(muted).lower()};"
                f"target.loop = {str(loop).lower()};"
                f"target.autoplay = {str(autoplay).lower()};"
                "target.playsInline = true;"
                f"{controls_js}"
                f"if ({str(autoplay).lower()}) {{"
                "const playPromise = target.play();"
                "if (playPromise !== undefined) {"
                "playPromise.catch(() => { console.warn('Autoplay prevented by browser policy'); });"
                "}"
                "}"
                "}"
                "</script>"
            )
            components_html(script, height=0, width=0)

        if caption:
            st.caption(caption)
        return True

    return False


def ensure_video_directories() -> None:
    """既定の動画保存ディレクトリを作成（存在しない場合のみ）。"""
    (VIDEO_ROOT / "reception").mkdir(parents=True, exist_ok=True)
