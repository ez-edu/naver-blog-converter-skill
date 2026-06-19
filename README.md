# naver-blog-converter-skill

네이버 블로그 글 또는 복사한 본문을 티스토리/워드프레스용 초안으로 변환하고, GEO/AEO에 맞게 핵심 요약·FAQ·SEO 메타·JSON-LD 초안까지 만들어주는 Vercel Agent Skill 패키지다.

## 설치

Codex 권장:

```bash
npx --yes skills add ez-edu/naver-blog-converter-skill --skill naver-blog-converter --agent codex -g -y
```

로컬 테스트:

```bash
npx --yes skills add . --list
```

## 현재 지원 범위

v1 변환 + 최적화:

- Markdown 생성
- Tistory HTML 생성
- WordPress HTML 생성
- 이미지 URL 목록 생성
- GEO/AEO 핵심 요약과 FAQ 섹션 추가
- SEO 제목/메타 설명/키워드 제안
- WordPress SEO 플러그인에 참고할 Article/FAQPage JSON-LD 초안 생성

v2 브라우저 입력 보조:

- Tistory/WordPress 글쓰기 화면에 제목/본문 입력 보조
- 로그인은 사용자가 직접 수행
- 발행/저장/예약/수정 버튼은 누르지 않음

Tistory는 공개 게시 API가 중단되었으므로 브라우저 입력 보조만 지원한다. WordPress REST API draft 생성은 회사 계정/보안 정책이 정해진 뒤 다음 버전에서 추가한다.

## 사용 예시

```text
naver-blog-converter 스킬을 사용해서 이 네이버 블로그 글을 티스토리와 워드프레스용 초안으로 변환해줘.
원문은 내 블로그 글이고 이전/재가공하는 용도야.
URL: https://blog.naver.com/...
출력은 Markdown, Tistory HTML, WordPress HTML 모두 만들어줘.
GEO/AEO에 맞게 핵심 요약, FAQ, SEO 제목/메타 설명, JSON-LD 초안도 같이 만들어줘.
이미지는 원본 URL 목록만 뽑고 자동 업로드는 하지 마.
```

## 안전 원칙

- 본인 소유 또는 허가받은 글만 이전/재게시한다.
- 타인의 글은 요약/인용/리서치 용도로만 사용하고 출처를 유지한다.
- Tistory/WordPress 로그인은 사용자가 직접 한다.
- 발행/저장/예약/수정 버튼은 자동으로 누르지 않는다.
- 이미지 업로드는 자동으로 하지 않는다.
- 비밀번호, OTP, 쿠키, API 토큰은 저장하지 않는다.
