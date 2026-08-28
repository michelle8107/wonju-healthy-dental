import { NextRequest, NextResponse } from "next/server";
import { generateBlogPost } from "@/lib/anthropic";
import { publishPost } from "@/lib/blogger";
import { getRecentTopics, addRecentTopic } from "@/lib/redis";

export const maxDuration = 60;

function isAuthorized(req: NextRequest): boolean {
  const secret = process.env.CRON_SECRET;
  if (!secret) return false;
  const auth = req.headers.get("authorization");
  return auth === `Bearer ${secret}`;
}

export async function GET(req: NextRequest) {
  if (!isAuthorized(req)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  try {
    const recentTopics = await getRecentTopics();
    const post = await generateBlogPost(recentTopics);
    const published = await publishPost({
      title: post.title,
      contentHtml: post.contentHtml,
      labels: post.labels,
    });
    await addRecentTopic(post.topic);

    return NextResponse.json({
      ok: true,
      topic: post.topic,
      title: post.title,
      postId: published.id,
      url: published.url,
    });
  } catch (err) {
    console.error("generate-post failed:", err);
    return NextResponse.json(
      { ok: false, error: err instanceof Error ? err.message : String(err) },
      { status: 500 }
    );
  }
}
