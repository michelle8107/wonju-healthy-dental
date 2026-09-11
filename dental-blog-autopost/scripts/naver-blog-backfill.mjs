// 네이버 블로그에 여러 편을 브라우저 1세션으로 몰아서 임시저장한다.
//
// 로그인은 첫 편에서 한 번만 하고 같은 창을 계속 재사용한다. 편마다 새로 띄우면
// 매번 로그인/캡차를 만나게 되므로 배치는 반드시 이 스크립트로 돌린다.
//
// 사용법:
//   node scripts/naver-blog-backfill.mjs <manifest.json> [--delay 5] [--timeout 300] [--keep-open]
//
// manifest.json 형식:
//   [
//     { "file": "scripts/implant-guide-post.html", "title": "임플란트 가이드", "tags": ["원주치과","임플란트"] },
//     { "file": "scripts/tartar-guide-post.html",  "title": "스케일링 가이드", "tags": ["스케일링"] }
//   ]
// file 경로는 dental-blog-autopost/ 기준 상대경로 또는 절대경로.

import fs from "node:fs";
import path from "node:path";
import {
  ROOT, CONFIG, sleep, log, launch, openEditor, dismissPopups,
  buildBodyHtml, fillPost, screenshot, WRITE_URL,
} from "./naver-blog-core.mjs";

const argv = process.argv.slice(2);
const numArg = (name, fallback) => {
  const i = argv.indexOf(name);
  return i >= 0 ? Number(argv[i + 1]) || fallback : fallback;
};
const flags = {
  keepOpen: argv.includes("--keep-open"),
  publish: argv.includes("--publish"),
  delay: numArg("--delay", 5),
  timeout: numArg("--timeout", CONFIG.loginTimeoutSec || 300),
};
const manifestPath = argv.find((a, i) => !a.startsWith("--") && !["--delay", "--timeout"].includes(argv[i - 1]));

if (!manifestPath) {
  console.error("사용법: node scripts/naver-blog-backfill.mjs <manifest.json> [--delay 5] [--timeout 300] [--keep-open]");
  process.exit(1);
}

const items = JSON.parse(fs.readFileSync(path.resolve(manifestPath), "utf8"));
if (!Array.isArray(items) || !items.length) {
  console.error("manifest가 비어 있거나 배열이 아닙니다.");
  process.exit(1);
}
log(`${items.length}편 처리 예정 (delay ${flags.delay}초, ${flags.publish ? "발행" : "임시저장"})`);

const { context, page } = await launch();
const report = [];

let editor;
try {
  editor = await openEditor(page, { loginTimeoutSec: flags.timeout });
} catch (err) {
  console.error(String(err.message || err));
  await context.close();
  process.exit(2);
}

for (const [i, item] of items.entries()) {
  const label = `${i + 1}/${items.length} ${item.title}`;
  const filePath = path.isAbsolute(item.file) ? item.file : path.join(ROOT, item.file);

  if (!fs.existsSync(filePath)) {
    log(`SKIP ${label} — 파일 없음: ${filePath}`);
    report.push({ ...item, status: "skip", reason: "파일 없음" });
    continue;
  }

  log(`--- ${label}`);
  try {
    // 2편째부터는 글쓰기 화면을 새로 연다 (이전 본문이 남아있지 않도록).
    if (i > 0) {
      await page.goto(WRITE_URL, { waitUntil: "domcontentloaded" });
      const frameEl = await page.$("#mainFrame");
      editor = frameEl ? await frameEl.contentFrame() : page;
      await editor.waitForSelector(".se-main-container, .se-content", { timeout: 30000 }).catch(() => {});
      await dismissPopups(editor);
    }

    const result = await fillPost(page, editor, {
      title: item.title,
      bodyHtml: buildBodyHtml(filePath),
      tags: item.tags || [],
      publish: flags.publish,
    });

    if (result.ok) {
      report.push({ ...item, status: "ok" });
      log(`OK ${label}`);
    } else {
      report.push({ ...item, status: "fail", reason: result.reason });
      log(`FAIL ${label} — ${result.reason}`);
      await screenshot(page, `fail-${i + 1}`);
    }
  } catch (err) {
    report.push({ ...item, status: "fail", reason: String(err.message || err) });
    log(`FAIL ${label} — ${err.message || err}`);
    await screenshot(page, `fail-${i + 1}`);
  }

  if (i < items.length - 1) await sleep(flags.delay * 1000);
}

console.log("\n===== 리포트 =====");
for (const r of report) {
  console.log(`${r.status.toUpperCase().padEnd(4)} | ${r.title}${r.reason ? ` (${r.reason})` : ""}`);
}
const ok = report.filter((r) => r.status === "ok").length;
console.log(`\n성공 ${ok} / 전체 ${report.length}`);
log(`확인: 에디터 상단 "저장 N" 카운터로 임시저장 개수를 본다. https://blog.naver.com/${CONFIG.blogId}`);

if (flags.keepOpen) {
  log("--keep-open: 창을 열어둡니다. 터미널에서 Ctrl+C로 종료하세요.");
  await new Promise(() => {});
}
await context.close();
process.exit(ok === report.length ? 0 : 1);
