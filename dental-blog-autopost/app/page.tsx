export default function Home() {
  return (
    <main style={{ fontFamily: "sans-serif", padding: 40 }}>
      <h1>dental-blog-autopost</h1>
      <p>원주 건강한치과 블로그(healthydentalwonju.blogspot.com) 자동 포스팅 크론 워커.</p>
      <p>
        사람이 보는 화면은 없고, Vercel Cron이 <code>/api/cron/generate-post</code>를
        주기적으로 호출해서 Claude가 쓴 글을 Blogger에 바로 게시합니다.
      </p>
    </main>
  );
}
