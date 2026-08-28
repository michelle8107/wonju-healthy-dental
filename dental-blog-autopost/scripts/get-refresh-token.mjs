// 1회성 로컬 스크립트: Google OAuth "설치된 앱(Desktop app)" 흐름으로 Blogger API에 쓸
// refresh_token을 발급받는다. 배포되는 앱에는 포함되지 않음 — 로컬에서 `npm run get-refresh-token`
// 으로 한 번만 실행하면 된다.
//
// 사전 준비: Google Cloud Console에서 OAuth 클라이언트(애플리케이션 유형: 데스크톱 앱)를
// 만들어 클라이언트 ID/보안 비밀을 받아둔다.

import http from "node:http";
import readline from "node:readline/promises";
import { stdin, stdout } from "node:process";

const PORT = 53682; // 로컬 리디렉션 수신용 임시 포트
const REDIRECT_URI = `http://127.0.0.1:${PORT}/oauth2callback`;
const SCOPE = "https://www.googleapis.com/auth/blogger";

async function prompt(question) {
  const rl = readline.createInterface({ input: stdin, output: stdout });
  const answer = await rl.question(question);
  rl.close();
  return answer.trim();
}

async function main() {
  const clientId = process.env.BLOGGER_CLIENT_ID || (await prompt("BLOGGER_CLIENT_ID: "));
  const clientSecret =
    process.env.BLOGGER_CLIENT_SECRET || (await prompt("BLOGGER_CLIENT_SECRET: "));

  const authUrl = new URL("https://accounts.google.com/o/oauth2/v2/auth");
  authUrl.searchParams.set("client_id", clientId);
  authUrl.searchParams.set("redirect_uri", REDIRECT_URI);
  authUrl.searchParams.set("response_type", "code");
  authUrl.searchParams.set("scope", SCOPE);
  authUrl.searchParams.set("access_type", "offline");
  authUrl.searchParams.set("prompt", "consent");

  console.log("\n아래 URL을 브라우저에서 열고, 블로그를 관리하는 구글 계정으로 로그인/승인하세요:\n");
  console.log(authUrl.toString());
  console.log("\n승인하면 이 터미널이 자동으로 코드를 받아 refresh_token을 발급합니다...\n");

  const code = await new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      const url = new URL(req.url, `http://127.0.0.1:${PORT}`);
      if (url.pathname !== "/oauth2callback") {
        res.writeHead(404);
        res.end();
        return;
      }
      const code = url.searchParams.get("code");
      const error = url.searchParams.get("error");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(
        error
          ? `<h1>승인 실패: ${error}</h1><p>이 창을 닫고 터미널을 확인하세요.</p>`
          : `<h1>승인 완료!</h1><p>이 창을 닫고 터미널로 돌아가세요.</p>`
      );
      server.close();
      if (error) reject(new Error(error));
      else resolve(code);
    });
    server.listen(PORT);
  });

  const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      code,
      grant_type: "authorization_code",
      redirect_uri: REDIRECT_URI,
    }),
  });

  const tokenData = await tokenRes.json();
  if (!tokenRes.ok) {
    console.error("토큰 교환 실패:", tokenData);
    process.exit(1);
  }

  if (!tokenData.refresh_token) {
    console.error(
      "\n응답에 refresh_token이 없습니다. 이미 이 계정으로 한 번 승인한 적이 있으면 Google이" +
        " refresh_token을 다시 안 줄 수 있습니다.\n" +
        "https://myaccount.google.com/permissions 에서 이 앱의 접근 권한을 제거하고 다시 시도하세요."
    );
    process.exit(1);
  }

  console.log("\n발급된 BLOGGER_REFRESH_TOKEN (Vercel 환경변수에 등록하세요):\n");
  console.log(tokenData.refresh_token);
  console.log("");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
