// Blogger API v3 클라이언트 — 공식 googleapis 패키지 없이, OAuth2 refresh_token으로
// access_token을 교환한 뒤 REST 엔드포인트를 직접 호출한다 (의존성을 가볍게 유지).

interface TokenResponse {
  access_token: string;
  expires_in: number;
  token_type: string;
}

async function getAccessToken(): Promise<string> {
  const clientId = process.env.BLOGGER_CLIENT_ID;
  const clientSecret = process.env.BLOGGER_CLIENT_SECRET;
  const refreshToken = process.env.BLOGGER_REFRESH_TOKEN;

  if (!clientId || !clientSecret || !refreshToken) {
    throw new Error(
      "Blogger 환경변수(BLOGGER_CLIENT_ID/BLOGGER_CLIENT_SECRET/BLOGGER_REFRESH_TOKEN)가 설정되지 않았습니다."
    );
  }

  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: "refresh_token",
    }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Google OAuth 토큰 갱신 실패 (${res.status}): ${body}`);
  }

  const data = (await res.json()) as TokenResponse;
  return data.access_token;
}

export interface BloggerPostInput {
  title: string;
  contentHtml: string;
  labels: string[];
}

export interface BloggerPostResult {
  id: string;
  url: string;
}

export async function publishPost(post: BloggerPostInput): Promise<BloggerPostResult> {
  const blogId = process.env.BLOGGER_BLOG_ID;
  if (!blogId) {
    throw new Error("BLOGGER_BLOG_ID 환경변수가 설정되지 않았습니다.");
  }

  const accessToken = await getAccessToken();

  const res = await fetch(
    `https://www.googleapis.com/blogger/v3/blogs/${blogId}/posts/?isDraft=false`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: post.title,
        content: post.contentHtml,
        labels: post.labels,
      }),
    }
  );

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Blogger 게시 실패 (${res.status}): ${body}`);
  }

  const data = (await res.json()) as { id: string; url: string };
  return { id: data.id, url: data.url };
}
