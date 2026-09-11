import fs from "node:fs";

const {
  BLOGGER_CLIENT_ID,
  BLOGGER_CLIENT_SECRET,
  BLOGGER_REFRESH_TOKEN,
  BLOGGER_BLOG_ID,
} = process.env;

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

const content = fs.readFileSync(new URL("./about-page.html", import.meta.url), "utf8");

const res = await fetch(
  `https://www.googleapis.com/blogger/v3/blogs/${BLOGGER_BLOG_ID}/pages/`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${access_token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ title: "병원 소개", content, isDraft: false }),
  }
);

const data = await res.json();
console.log(res.status, JSON.stringify(data, null, 2));
