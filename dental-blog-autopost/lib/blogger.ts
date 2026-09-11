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

// 매 글 하단에 붙는 고정 병원 정보 — Claude가 매번 다시 쓰게 하면 주소/전화번호가 틀릴 수 있으니
// 여기 하나로 고정해서 모든 글에 동일하게 붙인다. (홈페이지 index.html, 명함 기준)
// 맨 위 카카오톡 상담 버튼은 scripts/publish-geonchi-post.mjs · update-geonchi-post.mjs에도 똑같이 있다.
const CLINIC_FOOTER = `
<div style="text-align:center;margin:36px 0 8px;">
  <a href="https://pf.kakao.com/_YCjxaX/chat" target="_blank" rel="noopener" style="display:inline-block;background:#FEE500;color:#191919;font-size:16px;font-weight:700;line-height:1;padding:15px 30px;border-radius:12px;text-decoration:none;box-shadow:0 2px 8px rgba(0,0,0,0.12);"><svg width="20" height="20" viewBox="0 0 24 24" style="vertical-align:-4px;margin-right:8px;"><path fill="#191919" d="M12 3.5C6.75 3.5 2.5 6.86 2.5 11c0 2.66 1.75 5 4.4 6.33-.19.7-.7 2.54-.8 2.93-.12.49.18.48.38.35.16-.1 2.5-1.7 3.52-2.39.64.09 1.3.14 2 .14 5.25 0 9.5-3.36 9.5-7.5S17.25 3.5 12 3.5z"/></svg>카카오톡으로 상담 문의하기</a>
  <p style="margin:10px 0 0;font-size:13px;color:#888;">진료·예약 관련 궁금한 점은 카카오톡 채팅으로 편하게 문의해주세요</p>
</div>
<hr style="border:none;border-top:1px solid #eee;margin:32px 0 20px;">
<div style="font-size:13px;color:#888;line-height:1.7;text-align:center;">
  <p style="margin:0 0 6px;">
    <strong style="color:#0f3d3a;">원주 건강한치과</strong> ·
    강원특별자치도 원주시 건강로 21, 2층 (반곡동 조은빌딩, 국민건강보험공단 앞) ·
    TEL. <a href="tel:033-734-2275" style="color:#0f3d3a;">033-734-2275</a>
  </p>
  <p style="margin:0;">
    이 글은 일반적인 치아 건강 정보 제공을 목적으로 하며, 정확한 진단과 처방은 내원 후 상담을 통해 받으실 수 있습니다.
    병원에 대해 더 궁금하시면 <a href="https://healthydentalwonju.blogspot.com/p/blog-page.html" style="color:#0f3d3a;">병원 소개</a> 페이지를 참고해주세요.
  </p>
</div>
`.trim();

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
        content: `${post.contentHtml}\n${CLINIC_FOOTER}`,
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
