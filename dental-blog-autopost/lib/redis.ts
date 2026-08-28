import { Redis } from "@upstash/redis";

let client: Redis | null = null;

// Vercel Marketplace의 Upstash 연동은 KV_REST_API_URL/TOKEN 이름으로 환경변수를 주입한다
// (예전 @vercel/kv 네이밍 그대로 — UPSTASH_REDIS_REST_* 가 아님).
export function getRedis(): Redis {
  if (!client) {
    const url = process.env.KV_REST_API_URL;
    const token = process.env.KV_REST_API_TOKEN;
    if (!url || !token) {
      throw new Error("Redis 환경변수(KV_REST_API_URL/KV_REST_API_TOKEN)가 설정되지 않았습니다.");
    }
    client = new Redis({ url, token });
  }
  return client;
}

const HISTORY_KEY = "dental-blog:recent-topics";
const HISTORY_MAX = 30;

// 최근에 쓴 주제/제목 목록 (오래된 것부터). 프롬프트에 넣어 중복 소재를 피하는 데 쓴다.
export async function getRecentTopics(): Promise<string[]> {
  const redis = getRedis();
  const items = await redis.lrange<string>(HISTORY_KEY, 0, HISTORY_MAX - 1);
  return items ?? [];
}

export async function addRecentTopic(topic: string): Promise<void> {
  const redis = getRedis();
  await redis.lpush(HISTORY_KEY, topic);
  await redis.ltrim(HISTORY_KEY, 0, HISTORY_MAX - 1);
}
