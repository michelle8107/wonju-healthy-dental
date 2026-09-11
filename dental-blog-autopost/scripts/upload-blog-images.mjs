import { put } from "@vercel/blob";
import fs from "node:fs";
import path from "node:path";

const dir = process.argv[2];
const files = fs.readdirSync(dir).filter((f) => f.endsWith(".jpg") || f.endsWith(".png"));

for (const f of files) {
  const buf = fs.readFileSync(path.join(dir, f));
  const blob = await put(`blog/${f}`, buf, {
    access: "public",
    token: process.env.BLOB_READ_WRITE_TOKEN,
    contentType: f.endsWith(".png") ? "image/png" : "image/jpeg",
  });
  console.log(f, "->", blob.url);
}
