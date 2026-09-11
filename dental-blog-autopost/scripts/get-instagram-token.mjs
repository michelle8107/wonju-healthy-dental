// 1회성 로컬 스크립트: Instagram API with Instagram Login OAuth 흐름으로
// long-lived access token을 발급받는다. get-refresh-token.mjs(Blogger)와 같은 패턴.

import http from "node:http";

const PORT = 53683;
const REDIRECT_URI = `http://localhost:${PORT}/oauth2callback`;
const SCOPE = "instagram_business_basic,instagram_business_content_publish";

const IG_APP_ID = process.env.IG_APP_ID_INSTAGRAM || process.env.IG_APP_ID;
const IG_APP_SECRET = process.env.IG_APP_SECRET_INSTAGRAM;

if (!IG_APP_ID || !IG_APP_SECRET) {
  console.error("IG_APP_ID_INSTAGRAM(또는 IG_APP_ID)와 IG_APP_SECRET_INSTAGRAM 환경변수가 필요합니다.");
  process.exit(1);
}

const authUrl = new URL("https://www.instagram.com/oauth/authorize");
authUrl.searchParams.set("client_id", IG_APP_ID);
authUrl.searchParams.set("redirect_uri", REDIRECT_URI);
authUrl.searchParams.set("response_type", "code");
authUrl.searchParams.set("scope", SCOPE);

console.log("\n아래 URL을 브라우저에서 열고, 연결한 인스타그램 계정으로 로그인/승인하세요:\n");
console.log(authUrl.toString());
console.log("\n승인하면 자동으로 토큰을 발급합니다...\n");

const code = await new Promise((resolve, reject) => {
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    if (url.pathname !== "/oauth2callback") {
      res.writeHead(404);
      res.end();
      return;
    }
    const code = url.searchParams.get("code");
    const error = url.searchParams.get("error_description") || url.searchParams.get("error");
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    res.end(
      error
        ? `<h1>승인 실패: ${error}</h1>`
        : `<h1>승인 완료!</h1><p>이 창을 닫고 터미널로 돌아가세요.</p>`
    );
    server.close();
    if (error) reject(new Error(error));
    else resolve(code.replace(/#_$/, ""));
  });
  server.listen(PORT);
});

// Step 1: code -> short-lived token
const shortRes = await fetch("https://api.instagram.com/oauth/access_token", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({
    client_id: IG_APP_ID,
    client_secret: IG_APP_SECRET,
    grant_type: "authorization_code",
    redirect_uri: REDIRECT_URI,
    code,
  }),
});
const shortData = await shortRes.json();
if (!shortRes.ok) {
  console.error("short-lived 토큰 교환 실패:", shortData);
  process.exit(1);
}
console.log("Instagram User ID:", shortData.user_id);

// Step 2: short-lived -> long-lived (60일)
const longUrl = new URL("https://graph.instagram.com/access_token");
longUrl.searchParams.set("grant_type", "ig_exchange_token");
longUrl.searchParams.set("client_secret", IG_APP_SECRET);
longUrl.searchParams.set("access_token", shortData.access_token);

const longRes = await fetch(longUrl);
const longData = await longRes.json();
if (!longRes.ok) {
  console.error("long-lived 토큰 교환 실패:", longData);
  process.exit(1);
}

console.log("\n발급된 IG_ACCESS_TOKEN (60일 유효, 저장해두세요):\n");
console.log(longData.access_token);
console.log("\nIG_USER_ID:", shortData.user_id);
console.log("");
