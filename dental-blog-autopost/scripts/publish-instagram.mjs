// 로컬 mp4 파일을 Vercel Blob에 올리고 Instagram Reels로 발행한다.
// 사용법: node --env-file=.env.local scripts/publish-instagram.mjs <video-path> "<caption>"

import { put } from "@vercel/blob";
import fs from "node:fs";
import path from "node:path";

const [, , videoPath, caption] = process.argv;

if (!videoPath || !caption) {
  console.error('사용법: node --env-file=.env.local scripts/publish-instagram.mjs <video-path> "<caption>"');
  process.exit(1);
}

const {
  KV_REST_API_URL,
  KV_REST_API_TOKEN,
  IG_USER_ID,
  BLOB_READ_WRITE_TOKEN,
} = process.env;

if (!KV_REST_API_URL || !KV_REST_API_TOKEN || !IG_USER_ID || !BLOB_READ_WRITE_TOKEN) {
  console.error(
    "필요한 환경변수가 없습니다: KV_REST_API_URL, KV_REST_API_TOKEN, IG_USER_ID, BLOB_READ_WRITE_TOKEN"
  );
  process.exit(1);
}

async function redisGet(key) {
  const res = await fetch(`${KV_REST_API_URL}/get/${key}`, {
    headers: { Authorization: `Bearer ${KV_REST_API_TOKEN}` },
  });
  const data = await res.json();
  return data.result;
}

async function redisSet(key, value) {
  await fetch(`${KV_REST_API_URL}/set/${key}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${KV_REST_API_TOKEN}`, "Content-Type": "text/plain" },
    body: String(value),
  });
}

async function getValidAccessToken() {
  const token = await redisGet("instagram:access_token");
  const refreshedAt = Number((await redisGet("instagram:token_refreshed_at")) ?? 0);
  const ageSeconds = Date.now() / 1000 - refreshedAt;

  if (ageSeconds < 24 * 60 * 60) return token;

  console.log("토큰이 24시간 이상 지나 갱신합니다...");
  const res = await fetch(
    `https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=${encodeURIComponent(token)}`
  );
  const data = await res.json();
  if (!res.ok) {
    console.error("토큰 갱신 실패:", data);
    process.exit(1);
  }
  await redisSet("instagram:access_token", data.access_token);
  await redisSet("instagram:token_refreshed_at", Math.floor(Date.now() / 1000));
  return data.access_token;
}

async function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

console.log(`업로드 중: ${videoPath} -> Vercel Blob`);
const fileBuffer = fs.readFileSync(videoPath);
const blob = await put(`instagram/${Date.now()}-${path.basename(videoPath)}`, fileBuffer, {
  access: "public",
  token: BLOB_READ_WRITE_TOKEN,
  contentType: "video/mp4",
});
console.log("공개 URL:", blob.url);

const accessToken = await getValidAccessToken();

console.log("Instagram 미디어 컨테이너 생성 중...");
const createRes = await fetch(`https://graph.instagram.com/v23.0/${IG_USER_ID}/media`, {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({
    media_type: "REELS",
    video_url: blob.url,
    caption,
    access_token: accessToken,
  }),
});
const createData = await createRes.json();
if (!createRes.ok) {
  console.error("컨테이너 생성 실패:", createData);
  process.exit(1);
}
const containerId = createData.id;
console.log("컨테이너 ID:", containerId, "— 처리 대기 중...");

let status = "IN_PROGRESS";
for (let i = 0; i < 36 && status === "IN_PROGRESS"; i++) {
  await sleep(5000);
  const statusRes = await fetch(
    `https://graph.instagram.com/v23.0/${containerId}?fields=status_code&access_token=${accessToken}`
  );
  const statusData = await statusRes.json();
  status = statusData.status_code;
  console.log(`  상태: ${status} (${(i + 1) * 5}초 경과)`);
}

if (status !== "FINISHED") {
  console.error(`미디어 처리 실패 또는 타임아웃 (status: ${status})`);
  process.exit(1);
}

console.log("발행 중...");
const publishRes = await fetch(`https://graph.instagram.com/v23.0/${IG_USER_ID}/media_publish`, {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({ creation_id: containerId, access_token: accessToken }),
});
const publishData = await publishRes.json();
if (!publishRes.ok) {
  console.error("발행 실패:", publishData);
  process.exit(1);
}

console.log("\n✅ 발행 완료! Media ID:", publishData.id);
