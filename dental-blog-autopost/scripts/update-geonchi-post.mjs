// 이미 발행된 블로그 글을 수정한다 (내용 교체 + 라벨 재설정).
// 사용법: node --env-file=.env.local scripts/update-geonchi-post.mjs <postId> <html-file> "<제목>" "라벨1,라벨2"

import fs from "node:fs";

const [, , postId, htmlFile, title, labelsArg] = process.argv;
if (!postId || !htmlFile || !title) {
  console.error('사용법: node --env-file=.env.local scripts/update-geonchi-post.mjs <postId> <html-file> "<제목>" "라벨1,라벨2"');
  process.exit(1);
}

const { BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN, BLOGGER_BLOG_ID } = process.env;

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

const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({
    client_id: BLOGGER_CLIENT_ID,
    client_secret: BLOGGER_CLIENT_SECRET,
    refresh_token: BLOGGER_REFRESH_TOKEN,
    grant_type: "refresh_token",
  }),
});
const { access_token } = await tokenRes.json();

const content = fs.readFileSync(htmlFile, "utf8") + "\n" + CLINIC_FOOTER;
const labels = labelsArg ? labelsArg.split(",").map((s) => s.trim()) : [];

const res = await fetch(`https://www.googleapis.com/blogger/v3/blogs/${BLOGGER_BLOG_ID}/posts/${postId}`, {
  method: "PUT",
  headers: { Authorization: `Bearer ${access_token}`, "Content-Type": "application/json" },
  body: JSON.stringify({ title, content, labels }),
});
const data = await res.json();
console.log(res.status, JSON.stringify(data, null, 2).slice(0, 2000));
