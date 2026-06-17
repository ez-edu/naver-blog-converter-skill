# 네이버 블로그 변환 스킬 직원용 Codex 가이드

이 문서는 비개발자 직원이 Codex에서 `naver-blog-converter` 스킬을 설치하고 네이버 블로그 글을 티스토리/워드프레스용 초안으로 변환하는 방법을 안내한다.

## 1. 설치

PowerShell 또는 Terminal에서 실행한다.

```bash
npx --yes skills add <owner>/naver-blog-converter-skill --skill naver-blog-converter --agent codex -g -y
```

GitHub에 올린 뒤 `<owner>`를 실제 GitHub 계정/조직명으로 바꾼다.

로컬 테스트용:

```bash
npx --yes skills add /Users/wbjung/naver-blog-converter-skill --skill naver-blog-converter --agent codex -g -y
```

설치 확인:

```bash
npx --yes skills list --agent codex -g
```

`naver-blog-converter`가 보이면 정상이다.

## 2. Codex에 요청하는 문구

```text
naver-blog-converter 스킬을 사용해서 이 네이버 블로그 글을 티스토리와 워드프레스용 초안으로 변환해줘.
원문은 내 블로그 글이고 이전/재가공하는 용도야.
URL: https://blog.naver.com/...
출력은 Markdown, Tistory HTML, WordPress HTML 모두 만들어줘.
이미지는 원본 URL 목록만 뽑고 자동 업로드는 하지 마.
```

## 3. URL 접근이 안 될 때

비공개 글, 이웃공개 글, 로그인 필요 글, 네이버 차단 등으로 URL 읽기가 실패할 수 있다. 이때는 직원이 직접 네이버 블로그 글 본문을 복사해서 Codex에 붙여넣거나 HTML 파일로 저장해 제공한다.

요청 문구:

```text
URL 읽기가 안 되면 내가 복사한 본문을 기준으로 변환해줘.
아래 본문은 내 블로그 글이고 이전/재가공 권한이 있어.
대상은 티스토리와 워드프레스 초안이야.
```

## 4. 기대 결과

```text
변환 완료

생성 파일:
- Markdown
- Tistory HTML
- WordPress HTML
- 이미지 목록

검토 필요:
- 이미지 재업로드/저작권 확인
- 내부 링크 수정
- 카테고리/태그/SEO 제목
- 게시 전 미리보기
```

## 5. 주의사항

- 본인 글 또는 허가받은 글만 재게시한다.
- 타인의 글은 그대로 복사해 게시하지 않는다.
- 티스토리/워드프레스 로그인, 게시, 이미지 업로드는 별도 확인 없이 하지 않는다.
- 비밀번호, OTP, 쿠키, API 토큰은 Codex에 알려주지 않는다.
