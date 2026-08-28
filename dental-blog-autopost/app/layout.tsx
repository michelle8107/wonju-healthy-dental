export const metadata = {
  title: "dental-blog-autopost",
  description: "원주 건강한치과 블로그 자동 포스팅 크론 워커",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
