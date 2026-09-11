import { getRedis } from "./redis";

const TOKEN_KEY = "instagram:access_token";
const TOKEN_REFRESHED_AT_KEY = "instagram:token_refreshed_at";
const REFRESH_AFTER_SECONDS = 24 * 60 * 60; // 24h — 이보다 어리면 ig_refresh_token이 거절함

async function getStoredToken(): Promise<{ token: string; refreshedAt: number }> {
  const redis = getRedis();
  const [token, refreshedAtRaw] = await Promise.all([
    redis.get<string>(TOKEN_KEY),
    redis.get<string>(TOKEN_REFRESHED_AT_KEY),
  ]);
  if (!token) {
    throw new Error(
      "Redis에 instagram:access_token이 없습니다. scripts/get-instagram-token.mjs로 처음 발급 후 시딩하세요."
    );
  }
  return { token, refreshedAt: Number(refreshedAtRaw ?? 0) };
}

// 60일짜리 long-lived 토큰을 24시간 이상 지났으면 새로 갱신해서 Redis에 저장.
// (Blogger의 refresh_token과 달리 Instagram은 토큰 자체를 주기적으로 교체해줘야 한다.)
export async function getValidAccessToken(): Promise<string> {
  const { token, refreshedAt } = await getStoredToken();
  const ageSeconds = Date.now() / 1000 - refreshedAt;

  if (ageSeconds < REFRESH_AFTER_SECONDS) {
    return token;
  }

  const res = await fetch(
    `https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=${encodeURIComponent(token)}`
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Instagram 토큰 갱신 실패 (${res.status}): ${body}`);
  }
  const data = (await res.json()) as { access_token: string; expires_in: number };

  const redis = getRedis();
  await Promise.all([
    redis.set(TOKEN_KEY, data.access_token),
    redis.set(TOKEN_REFRESHED_AT_KEY, String(Math.floor(Date.now() / 1000))),
  ]);

  return data.access_token;
}

async function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export interface PublishReelInput {
  videoUrl: string; // 공개적으로 접근 가능한 URL (Vercel Blob 등)
  caption: string;
}

export interface PublishReelResult {
  mediaId: string;
}

// 릴스 발행: 컨테이너 생성 -> 처리 완료까지 폴링 -> 발행. 최대 ~2분 정도 걸릴 수 있다.
export async function publishReel({ videoUrl, caption }: PublishReelInput): Promise<PublishReelResult> {
  const igUserId = process.env.IG_USER_ID;
  if (!igUserId) {
    throw new Error("IG_USER_ID 환경변수가 설정되지 않았습니다.");
  }
  const accessToken = await getValidAccessToken();

  const createRes = await fetch(`https://graph.instagram.com/v23.0/${igUserId}/media`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      media_type: "REELS",
      video_url: videoUrl,
      caption,
      access_token: accessToken,
    }),
  });
  if (!createRes.ok) {
    const body = await createRes.text();
    throw new Error(`Instagram 미디어 컨테이너 생성 실패 (${createRes.status}): ${body}`);
  }
  const { id: containerId } = (await createRes.json()) as { id: string };

  // 비디오 처리 완료까지 폴링 (최대 ~2분, 5초 간격)
  let status = "IN_PROGRESS";
  for (let i = 0; i < 24 && status === "IN_PROGRESS"; i++) {
    await sleep(5000);
    const statusRes = await fetch(
      `https://graph.instagram.com/v23.0/${containerId}?fields=status_code&access_token=${accessToken}`
    );
    const statusData = (await statusRes.json()) as { status_code: string };
    status = statusData.status_code;
  }
  if (status !== "FINISHED") {
    throw new Error(`Instagram 미디어 처리 실패 또는 타임아웃 (status: ${status})`);
  }

  const publishRes = await fetch(`https://graph.instagram.com/v23.0/${igUserId}/media_publish`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      creation_id: containerId,
      access_token: accessToken,
    }),
  });
  if (!publishRes.ok) {
    const body = await publishRes.text();
    throw new Error(`Instagram 발행 실패 (${publishRes.status}): ${body}`);
  }
  const { id: mediaId } = (await publishRes.json()) as { id: string };

  return { mediaId };
}
