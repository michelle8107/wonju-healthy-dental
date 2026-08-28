# dental-blog-autopost

원주 건강한치과 Blogger 블로그(https://healthydentalwonju.blogspot.com/)에 Claude가 쓴 글을
주 2회(월/목) 자동으로 올리는 Vercel Cron 워커. 사람 검토 없이 바로 게시된다.

## 동작 방식

1. Vercel Cron이 `GET /api/cron/generate-post`를 `CRON_SECRET`과 함께 호출
2. Upstash Redis에서 최근에 쓴 주제 이력을 읽음
3. Anthropic API(Claude Sonnet 5)로 새 글(제목/HTML 본문/라벨) 생성 — 최근 주제와 겹치지 않게,
   의료광고 가이드라인(효과 보장/전후 비교/후기 인용/할인 소구 금지) 지키도록 지시
4. Blogger API v3로 즉시 게시 (`isDraft: false`)
5. 이번 주제를 Redis 이력에 추가

## 처음 설정할 때 (사용자가 직접 해야 하는 부분)

### 1. Google Cloud Console

1. https://console.cloud.google.com 에서 새 프로젝트 생성
2. "API 및 서비스 → 라이브러리"에서 **Blogger API v3** 검색 후 사용 설정
3. "API 및 서비스 → OAuth 동의 화면" 설정 — User Type: 외부, 테스트 모드로 충분
   (게시 심사 불필요, 테스트 사용자에 본인 구글 계정 추가)
4. "API 및 서비스 → 사용자 인증 정보 → 사용자 인증 정보 만들기 → OAuth 클라이언트 ID"
   - 애플리케이션 유형: **데스크톱 앱**
   - 생성 후 클라이언트 ID/보안 비밀 저장

### 2. 블로그 ID 확인

브라우저에서 아래 URL 접속 (YOUR_API_KEY는 Cloud Console "사용자 인증 정보"에서
API 키를 하나 새로 만들어 사용, 또는 Blogger 관리 화면 설정에서 직접 확인):

```
https://www.googleapis.com/blogger/v3/blogs/byurl?url=https://healthydentalwonju.blogspot.com/&key=YOUR_API_KEY
```

응답의 `id` 필드가 `BLOGGER_BLOG_ID`.

### 3. refresh_token 발급

```bash
npm install
BLOGGER_CLIENT_ID=... BLOGGER_CLIENT_SECRET=... npm run get-refresh-token
```

출력되는 URL을 브라우저에서 열고 **블로그를 관리하는 그 구글 계정**으로 로그인/승인하면
터미널에 `refresh_token`이 출력된다.

### 4. Anthropic API 키

https://console.anthropic.com 에서 새 API 키 발급.

### 5. Vercel 환경변수 등록

`.env.example`에 나열된 값들을 Vercel 프로젝트 설정(Environment Variables)에 등록.
`KV_REST_API_URL`/`KV_REST_API_TOKEN`은 Vercel Marketplace에서 Upstash Redis 연동을 추가하면
자동으로 채워진다. `CRON_SECRET`은 아무 임의의 긴 문자열(`openssl rand -hex 32`)이면 된다.

## 로컬 테스트

```bash
npm install
npm run dev
# 다른 터미널에서:
curl -H "Authorization: Bearer $CRON_SECRET" http://localhost:3000/api/cron/generate-post
```

실제로 Blogger에 글이 올라가니, 테스트 후 Blogger 관리 화면에서 지워도 된다.

## 배포

이 저장소는 원주 건강한치과 정적 홈페이지와 같은 git 저장소의 하위 폴더다. Vercel에
새 프로젝트를 연결할 때 **Root Directory를 `dental-blog-autopost`로 지정**해야 한다.
