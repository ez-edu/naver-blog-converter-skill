#!/usr/bin/env python3
"""Convert a Naver Blog post or copied HTML/text into Markdown, Tistory HTML, and WordPress HTML.

Stdlib-only helper for the naver-blog-converter agent skill.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Tuple

USER_AGENT = "Mozilla/5.0 (compatible; naver-blog-converter-skill/1.0; +https://github.com/)"


def slugify(text: str, fallback: str = "naver-post") -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    text = re.sub(r"[^0-9A-Za-z가-힣._-]+", "-", text.strip())
    text = re.sub(r"-+", "-", text).strip("-._")
    return text[:80] or fallback


def normalize_naver_url(url: str) -> str:
    if not url:
        return url
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    qs = urllib.parse.parse_qs(parsed.query)

    blog_id = None
    log_no = None

    # https://blog.naver.com/PostView.naver?blogId=...&logNo=...
    if "blog.naver.com" in host and path.lower().endswith("postview.naver"):
        blog_id = (qs.get("blogId") or qs.get("blogid") or [None])[0]
        log_no = (qs.get("logNo") or qs.get("logno") or [None])[0]
    # https://blog.naver.com/{blogId}/{logNo}
    else:
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2:
            blog_id, log_no = parts[0], parts[1]

    if blog_id and log_no:
        return f"https://m.blog.naver.com/{urllib.parse.quote(blog_id)}/{urllib.parse.quote(log_no)}"
    return url


def fetch_url(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(normalize_naver_url(url), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


class ContentParser(HTMLParser):
    BLOCK_TAGS = {"p", "div", "section", "article", "li", "blockquote"}
    HEADING_TAGS = {"h1", "h2", "h3", "h4"}
    SKIP_TAGS = {"script", "style", "noscript", "svg", "iframe"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.stack: List[str] = []
        self.current: List[str] = []
        self.blocks: List[Dict[str, str]] = []
        self.links: List[Dict[str, str]] = []
        self.images: List[Dict[str, str]] = []
        self.in_a = False
        self.current_href = ""
        self.current_heading = ""

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs_d = {k.lower(): v or "" for k, v in attrs}
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        self.stack.append(tag)
        if tag in self.HEADING_TAGS:
            self.flush()
            self.current_heading = tag
        elif tag in self.BLOCK_TAGS:
            # avoid flushing each nested div too aggressively; flush only when current has content
            pass
        elif tag == "br":
            self.current.append("\n")
        elif tag == "a":
            self.in_a = True
            self.current_href = attrs_d.get("href", "")
        elif tag == "img":
            src = attrs_d.get("src") or attrs_d.get("data-src") or attrs_d.get("data-lazy-src")
            if src and not src.startswith("data:"):
                alt = attrs_d.get("alt", "")
                self.images.append({"src": html.unescape(src), "alt": html.unescape(alt)})
                self.flush()
                self.blocks.append({"type": "image", "src": html.unescape(src), "alt": html.unescape(alt)})

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag in self.HEADING_TAGS:
            self.flush(block_type="heading", level=tag)
            self.current_heading = ""
        elif tag in {"p", "li", "blockquote"}:
            self.flush(block_type="quote" if tag == "blockquote" else "paragraph")
        elif tag == "a":
            text = clean_text("".join(self.current).split("\uFFF9")[-1])
            if self.current_href:
                self.links.append({"href": html.unescape(self.current_href), "text": text})
            self.in_a = False
            self.current_href = ""
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if data:
            self.current.append(data)

    def flush(self, block_type: str = "paragraph", level: str = "") -> None:
        text = clean_text("".join(self.current))
        self.current = []
        if not text or is_junk_text(text):
            return
        if block_type == "heading":
            self.blocks.append({"type": "heading", "level": level or self.current_heading or "h2", "text": text})
        else:
            self.blocks.append({"type": block_type, "text": text})


def clean_text(s: str) -> str:
    s = html.unescape(s or "")
    s = s.replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def is_junk_text(text: str) -> bool:
    junk = {
        "공감", "댓글", "공유", "블로그", "카페", "keep", "memo", "보내기", "인쇄",
        "이 블로그", "카테고리 글", "전체보기", "목록열기", "닫기",
    }
    compact = re.sub(r"\s+", "", text).lower()
    if len(compact) <= 1:
        return True
    if text.strip() in junk:
        return True
    if compact in {j.lower().replace(" ", "") for j in junk}:
        return True
    return False


def extract_title(raw: str, override: str = "") -> str:
    if override:
        return clean_text(override)
    patterns = [
        r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']',
        r'<title[^>]*>(.*?)</title>',
        r'<h1[^>]*>(.*?)</h1>',
    ]
    for pat in patterns:
        m = re.search(pat, raw, re.I | re.S)
        if m:
            title = clean_text(re.sub(r"<[^>]+>", " ", m.group(1)))
            title = re.sub(r"\s*[:：]\s*네이버\s*블로그\s*$", "", title)
            if title:
                return title
    return "네이버 블로그 변환 초안"


def parse_content(raw: str, title: str) -> Dict:
    parser = ContentParser()
    parser.feed(raw)
    parser.flush()

    # De-duplicate adjacent identical text blocks and repeated images.
    blocks = []
    seen_img = set()
    last_key = None
    for b in parser.blocks:
        if b.get("type") == "image":
            key = b.get("src", "")
            if not key or key in seen_img:
                continue
            seen_img.add(key)
        else:
            key = (b.get("type"), b.get("text", ""))
            if key == last_key:
                continue
            last_key = key
        blocks.append(b)

    images = []
    seen = set()
    for img in parser.images:
        src = img.get("src", "")
        if src and src not in seen:
            seen.add(src)
            images.append(img)

    text_chars = sum(len(b.get("text", "")) for b in blocks if b.get("type") != "image")
    return {"title": title, "blocks": blocks, "images": images, "links": parser.links, "text_chars": text_chars}


def block_to_markdown(block: Dict) -> str:
    typ = block.get("type")
    if typ == "heading":
        level = block.get("level", "h2")
        n = {"h1": 1, "h2": 2, "h3": 3, "h4": 4}.get(level, 2)
        return f"{'#' * n} {block.get('text', '').strip()}"
    if typ == "image":
        alt = block.get("alt") or "image"
        return f"![{alt}]({block.get('src', '')})"
    if typ == "quote":
        return "> " + block.get("text", "").replace("\n", "\n> ")
    return block.get("text", "").strip()


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def block_to_html(block: Dict) -> str:
    typ = block.get("type")
    if typ == "heading":
        level = block.get("level", "h2")
        if level not in {"h1", "h2", "h3", "h4"}:
            level = "h2"
        return f"<{level}>{esc(block.get('text',''))}</{level}>"
    if typ == "image":
        alt = esc(block.get("alt") or "")
        src = esc(block.get("src") or "")
        return f'<figure><img src="{src}" alt="{alt}"><figcaption>{alt}</figcaption></figure>' if alt else f'<figure><img src="{src}" alt=""></figure>'
    if typ == "quote":
        return f"<blockquote>{esc(block.get('text',''))}</blockquote>"
    text = esc(block.get("text", "")).replace("\n", "<br>\n")
    return f"<p>{text}</p>"


def block_to_wp(block: Dict) -> str:
    typ = block.get("type")
    if typ == "heading":
        return "<!-- wp:heading -->\n" + block_to_html(block) + "\n<!-- /wp:heading -->"
    if typ == "image":
        return "<!-- wp:image -->\n" + block_to_html(block) + "\n<!-- /wp:image -->"
    if typ == "quote":
        return "<!-- wp:quote -->\n" + block_to_html(block) + "\n<!-- /wp:quote -->"
    return "<!-- wp:paragraph -->\n" + block_to_html(block) + "\n<!-- /wp:paragraph -->"


def render_markdown(data: Dict, source_url: str, add_source: bool = True) -> str:
    lines = [f"# {data['title']}", ""]
    if add_source and source_url:
        lines += [f"> 원문: {source_url}", ""]
    for b in data["blocks"]:
        lines += [block_to_markdown(b), ""]
    return "\n".join(lines).strip() + "\n"


def render_html(data: Dict, source_url: str, platform: str, add_source: bool = True) -> str:
    lines = [f"<h1>{esc(data['title'])}</h1>", ""]
    if add_source and source_url:
        lines += [f'<p><small>원문: <a href="{esc(source_url)}">{esc(source_url)}</a></small></p>', ""]
    conv = block_to_wp if platform == "wordpress" else block_to_html
    for b in data["blocks"]:
        lines += [conv(b), ""]
    return "\n".join(lines).strip() + "\n"


def download_images(images: List[Dict], out_dir: Path, max_images: int) -> List[Dict]:
    image_dir = out_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []
    for i, img in enumerate(images[:max_images], 1):
        src = img.get("src") or ""
        try:
            ext = Path(urllib.parse.urlparse(src).path).suffix
            if not ext or len(ext) > 8:
                ext = ".jpg"
            name = f"image-{i:02d}-{hashlib.sha1(src.encode()).hexdigest()[:8]}{ext}"
            req = urllib.request.Request(src, headers={"User-Agent": USER_AGENT, "Referer": "https://m.blog.naver.com/"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            path = image_dir / name
            path.write_bytes(data)
            downloaded.append({"src": src, "path": str(path), "bytes": len(data)})
        except Exception as e:  # noqa: BLE001 - CLI should report per-image failures
            downloaded.append({"src": src, "error": str(e)})
    return downloaded


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Convert Naver Blog content into Tistory/WordPress-ready drafts.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", help="Naver Blog URL")
    src.add_argument("--input-file", help="Local HTML/text file")
    ap.add_argument("--title", default="", help="Override title")
    ap.add_argument("--source-url", default="", help="Source URL when using --input-file")
    ap.add_argument("--target", choices=["both", "tistory", "wordpress", "markdown"], default="both")
    ap.add_argument("--out", default="./converted", help="Output directory")
    ap.add_argument("--slug", default="", help="Filename slug")
    ap.add_argument("--download-images", action="store_true")
    ap.add_argument("--max-images", type=int, default=20)
    ap.add_argument("--no-source-note", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.url:
        source_url = args.url
        raw = fetch_url(args.url)
    else:
        source_url = args.source_url
        raw = Path(args.input_file).read_text(encoding="utf-8", errors="replace")

    title = extract_title(raw, args.title)
    data = parse_content(raw, title)
    if data["text_chars"] < 80:
        warning = "extracted text is short; review source parsing or provide copied body/HTML"
    else:
        warning = ""

    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.slug or slugify(title)
    generated = {}
    add_source = not args.no_source_note

    if args.target in {"both", "markdown"}:
        path = out_dir / f"{slug}.md"
        path.write_text(render_markdown(data, source_url, add_source), encoding="utf-8")
        generated["markdown"] = str(path)
    if args.target in {"both", "tistory"}:
        path = out_dir / f"{slug}.tistory.html"
        path.write_text(render_html(data, source_url, "tistory", add_source), encoding="utf-8")
        generated["tistory_html"] = str(path)
    if args.target in {"both", "wordpress"}:
        path = out_dir / f"{slug}.wordpress.html"
        path.write_text(render_html(data, source_url, "wordpress", add_source), encoding="utf-8")
        generated["wordpress_html"] = str(path)

    image_list = out_dir / f"{slug}.images.json"
    image_list.write_text(json.dumps(data["images"], ensure_ascii=False, indent=2), encoding="utf-8")
    generated["image_list"] = str(image_list)

    downloaded = []
    if args.download_images:
        downloaded = download_images(data["images"], out_dir, args.max_images)
        dl_path = out_dir / f"{slug}.downloaded-images.json"
        dl_path.write_text(json.dumps(downloaded, ensure_ascii=False, indent=2), encoding="utf-8")
        generated["downloaded_images"] = str(dl_path)

    summary = {
        "title": title,
        "source_url": source_url,
        "target": args.target,
        "text_chars": data["text_chars"],
        "block_count": len(data["blocks"]),
        "image_count": len(data["images"]),
        "generated": generated,
        "warning": warning,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("변환 완료")
        print(f"제목: {title}")
        if source_url:
            print(f"원문 URL: {source_url}")
        print(f"본문 글자 수: {data['text_chars']}")
        print(f"이미지 수: {len(data['images'])}")
        print("생성 파일:")
        for k, v in generated.items():
            print(f"- {k}: {v}")
        if warning:
            print(f"경고: {warning}")
        print("검토 필요: 이미지 권리/재업로드, 내부 링크, 카테고리/태그, 게시 전 미리보기")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
