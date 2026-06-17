# naver-blog-converter-skill

네이버 블로그 글 또는 복사한 본문을 티스토리/워드프레스용 초안으로 변환하는 Vercel Agent Skill 패키지다.

## 설치

Codex 권장:

```bash
npx --yes skills add <owner>/naver-blog-converter-skill --skill naver-blog-converter --agent codex -g -y
```

로컬 테스트:

```bash
npx --yes skills add /Users/wbjung/naver-blog-converter-skill --list
```

## 사용 예시

```text
naver-blog-converter 스킬을 사용해서 이 네이버 블로그 글을 티스토리와 워드프레스용 초안으로 변환해줘.
원문은 내 블로그 글이고 이전/재가공하는 용도야.
URL: https://blog.naver.com/...
출력은 Markdown, Tistory HTML, WordPress HTML 모두 만들어줘.
이미지는 원본 URL 목록만 뽑고 자동 업로드는 하지 마.
```

## 안전 원칙

- 본인 소유 또는 허가받은 글만 이전/재게시한다.
- 타인의 글은 요약/인용/리서치 용도로만 사용하고 출처를 유지한다.
- Tistory/WordPress 로그인, 게시, 이미지 업로드는 자동으로 하지 않는다.
- 비밀번호, OTP, 쿠키, API 토큰은 저장하지 않는다.
