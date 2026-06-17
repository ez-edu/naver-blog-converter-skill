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
- warn when source rights are unclear.

## Important boundary

Only convert content that the user owns or has permission to reuse.

Do not help copy third-party Naver Blog posts into another blog as if they were the user's original work. If the source appears to be someone else's post, convert only for review, summary, quotation, or authorized migration, and keep attribution.

This skill prepares drafts. It does not log in to Tistory/WordPress, publish posts, upload images, change SEO settings, or delete/edit live content unless the user separately asks and confirms the target account action.

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
- whether the content is user-owned or permissioned.

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
- WordPress/Tistory login needed: stop and ask for explicit publishing workflow; do not ask for credentials.

## Good first prompt

```text
naver-blog-converter 스킬을 사용해서 이 네이버 블로그 글을 티스토리와 워드프레스용 초안으로 변환해줘.
원문은 내 블로그 글이고 이전 게시글을 이전/재가공하는 용도야.
URL: https://blog.naver.com/...
출력은 Markdown, Tistory HTML, WordPress HTML 모두 만들어줘.
이미지는 원본 URL 목록만 뽑고 자동 업로드는 하지 마.
```
