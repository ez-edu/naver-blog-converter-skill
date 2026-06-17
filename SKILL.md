---
name: naver-blog-converter
description: Convert Naver Blog posts or drafts into Tistory- and WordPress-ready Markdown/HTML while preserving source attribution, headings, links, and image placeholders.
---

# naver-blog-converter

## What this skill does

Use this skill when the user wants to convert Naver Blog posts into reusable drafts for Tistory or WordPress.

The skill can:

- read a Naver Blog post URL when it is publicly accessible;
- convert Naver Blog text/HTML copied by the user;
- produce platform-ready outputs:
  - clean Markdown;
  - Tistory HTML draft;
  - WordPress classic/block-compatible HTML;
  - image inventory and migration checklist;
- rewrite formatting while keeping the original meaning;
- preserve source URL and attribution metadata;
- warn when source rights are unclear;
- assist browser-based draft entry for Tistory/WordPress up to the review screen without publishing.

## Important boundary

Only convert content that the user owns or has permission to reuse.

Do not help copy third-party Naver Blog posts into another blog as if they were the user's original work. If the source appears to be someone else's post, convert only for review, summary, quotation, or authorized migration, and keep attribution.

This skill has two modes:

- v1 convert-only mode: generate Markdown/HTML draft files and stop.
- v2 browser-entry-assist mode: after conversion, open or guide the user to the Tistory/WordPress editor, help paste the title/body/tags as a draft, then stop before Save/Publish.

Do not publish, schedule, save drafts, upload images, change SEO settings, or modify live content unless the user separately asks and explicitly confirms that side effect. For this version, the safe default is to stop at the preview/review stage before any Save/Publish button.

## Inputs

Ask for or infer:

- source: Naver Blog URL, copied HTML, copied text, or local file path;
- target platform: `tistory`, `wordpress`, or `both`;
- desired output: Markdown, HTML, or both;
- tone: faithful migration, SEO rewrite, casual rewrite, corporate blog rewrite;
- image policy:
  - keep source image URLs as placeholders;
  - download images locally;
  - omit images;
  - produce an image checklist only;
- whether the content is user-owned or permissioned;
- optional v2 posting-assist target URL/admin screen, e.g. Tistory write page or WordPress `/wp-admin/post-new.php`.

If the user provides only a Naver Blog URL, first try the helper script below. If it fails due to login, private post, age gate, bot block, or changed HTML, ask the user to paste the post body or exported HTML.

## Helper script

This skill includes a stdlib-only helper:

```bash
python3 scripts/naver_blog_convert.py --url "https://blog.naver.com/blogId/logNo" --target both --out ./converted
```

Alternative input from a local file:

```bash
python3 scripts/naver_blog_convert.py --input-file ./naver-post.html --title "원문 제목" --source-url "https://blog.naver.com/..." --target wordpress --out ./converted
```

Useful options:

```text
--url URL                     Naver Blog PC/mobile post URL
--input-file PATH             Local HTML/text copied from Naver Blog
--title TITLE                 Override title
--source-url URL              Source URL when using --input-file
--target both|tistory|wordpress|markdown
--out DIR                     Output directory
--slug SLUG                   Optional filename slug
--download-images             Download images referenced in the post
--max-images N                Limit image downloads, default 20
--no-source-note              Do not add source note to generated post body
--json                        Print machine-readable output summary
```

## Workflow

1. Confirm rights and intent.
   - If the user is migrating their own Naver Blog, proceed.
   - If the user is converting another person's post, keep it as summary/quotation or require permission/attribution.

2. Read source content.
   - Prefer the provided URL.
   - Convert `blog.naver.com/{blogId}/{logNo}` to `m.blog.naver.com/{blogId}/{logNo}` for easier reading.
   - If URL extraction fails, ask the user to paste content or save the page HTML and provide a file path.

3. Normalize content.
   - Extract title, text paragraphs, headings, links, and image URLs.
   - Remove scripts, tracking widgets, share buttons, duplicate UI text, and hidden metadata.
   - Keep source URL and extraction timestamp.

4. Convert to platform formats.
   - Markdown: clean headings, paragraphs, lists, links, and image placeholders.
   - Tistory HTML: simple semantic HTML using `h2/h3`, `p`, `figure`, `img`, `figcaption` where possible.
   - WordPress HTML: classic/block-compatible HTML comments around paragraphs/headings/images.

5. Quality pass.
   - Ensure the title is not empty.
   - Ensure the body is readable and not navigation junk.
   - Flag suspicious extraction problems: too little text, repeated menu labels, missing images, or only comments.

6. Deliver outputs.
   - Tell the user exact output paths.
   - Include a migration checklist: review text, replace images if needed, set categories/tags, check links, preview before publishing.

## v2 browser-entry-assist workflow

Use this workflow only when the user asks to put the converted draft into Tistory or WordPress. This is not automatic publishing.

### Shared rules

- Login is user-controlled. Open the site/editor if browser tools are available, then ask the user to log in manually in the opened browser.
- Never ask for passwords, OTP, cookies, application passwords, or API tokens.
- Paste or type only the title, body draft, tags/categories requested by the user, and optional excerpt/SEO draft when clearly requested.
- Stop before clicking any button that saves, publishes, schedules, updates, uploads, deletes, or changes public content.
- If the editor shows a publish/save/update/confirm modal, stop and ask the user to review and click it manually.
- If the agent lacks browser/computer-use capability, provide exact copy/paste instructions instead of pretending the entry was done.

### Tistory notes

Tistory's public posting API has been discontinued, so this skill should treat Tistory as browser-only.

Safe Tistory v2 path:

1. Convert the source post and choose the `.tistory.html` output.
2. Open the user's Tistory admin/write page if the user provided it, or ask the user to open the Tistory 글쓰기 page.
3. Ask the user to complete login manually.
4. Switch the editor to HTML mode only if the UI makes that safe and visible; otherwise instruct the user where to paste.
5. Enter title and body HTML.
6. Optionally enter tags/categories if the user supplied them.
7. Stop before 임시저장/발행/예약/수정 buttons. Tell the user to preview and click manually.

### WordPress notes

For now, WordPress should also use browser-entry-assist only. Future versions may add WordPress REST API draft creation after the company provides site accounts and a credential policy.

Safe WordPress v2 path:

1. Convert the source post and choose the `.wordpress.html` output.
2. Open the WordPress admin new-post page if provided, usually `https://example.com/wp-admin/post-new.php`.
3. Ask the user to log in manually.
4. Use the editor's Code Editor, Custom HTML block, or Classic Editor HTML mode when available.
5. Enter title and body HTML.
6. Optionally enter category/tags/excerpt if supplied by the user.
7. Stop before Save draft/Publish/Update/Schedule. Tell the user to preview and click manually.

### v2 completion response

When browser entry is prepared, respond with:

```text
입력 보조 완료 또는 입력 준비 완료

대상:
- 플랫폼: Tistory/WordPress
- 편집 화면: ...
- 제목 입력: 완료/사용자 직접 필요
- 본문 입력: 완료/사용자 직접 필요

멈춘 지점:
- 발행/저장/예약 전

사용자가 직접 확인할 것:
- 본문 깨짐 여부
- 이미지 표시/재업로드
- 카테고리/태그
- 미리보기
- 최종 저장/발행 클릭
```

## Output format to user

When done, respond with:

```text
변환 완료

입력:
- 원문 URL: ...
- 제목: ...
- 대상: Tistory/WordPress

생성 파일:
- Markdown: ...
- Tistory HTML: ...
- WordPress HTML: ...
- 이미지 목록: ...

검토 필요:
- 이미지 저작권/업로드 여부
- 내부 링크 수정
- 카테고리/태그/SEO 제목
- 게시 전 미리보기
```

## Safety and privacy

- Do not request or store Naver/Tistory/WordPress passwords, OTP, cookies, or access tokens.
- Do not bypass paywalls, private posts, login walls, or robots/bot blocks.
- Do not bulk-convert large numbers of third-party posts.
- Default to drafts, not publication.
- If downloading images, store them locally and tell the user to verify rights before re-uploading.

## Failure modes

- Private Naver Blog post: ask user to paste text/HTML they are allowed to reuse.
- HTML structure changed: use copied text/HTML fallback.
- Images hotlink blocked: output image list and ask user to download manually or provide files.
- WordPress/Tistory login needed: open/guide the login page only when v2 browser-entry-assist is requested; user logs in manually; do not ask for credentials.
- Tistory API requested: explain that the public posting API has been discontinued and use browser-entry-assist instead.
- WordPress API requested: defer to a future version until the company provides account details and a credential policy; for now use browser-entry-assist.

## Good v2 prompt

```text
naver-blog-converter 스킬을 사용해서 이 네이버 블로그 글을 변환한 뒤 티스토리 글쓰기 화면 입력까지 도와줘.
원문은 내 블로그 글이고 이전/재가공하는 용도야.
URL: https://blog.naver.com/...
티스토리 글쓰기 화면은 내가 로그인해서 열어둘게.
제목과 본문 HTML까지만 입력하고, 임시저장/발행/예약 버튼은 누르지 마.
이미지는 자동 업로드하지 말고 원본 URL 목록만 따로 알려줘.
```

```text
naver-blog-converter 스킬을 사용해서 이 네이버 블로그 글을 변환한 뒤 워드프레스 새 글 화면 입력까지 도와줘.
원문은 내 블로그 글이고 이전/재가공하는 용도야.
URL: https://blog.naver.com/...
워드프레스 관리자 새 글 URL: https://example.com/wp-admin/post-new.php
제목과 본문 HTML까지만 입력하고, Save draft/Publish/Update/Schedule은 누르지 마.
```

## Good first prompt

```text
naver-blog-converter 스킬을 사용해서 이 네이버 블로그 글을 티스토리와 워드프레스용 초안으로 변환해줘.
원문은 내 블로그 글이고 이전 게시글을 이전/재가공하는 용도야.
URL: https://blog.naver.com/...
출력은 Markdown, Tistory HTML, WordPress HTML 모두 만들어줘.
이미지는 원본 URL 목록만 뽑고 자동 업로드는 하지 마.
```
