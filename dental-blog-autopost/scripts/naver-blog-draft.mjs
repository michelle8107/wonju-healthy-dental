// 네이버 블로그에 글 한 편을 임시저장한다 (Playwright).
//
// 사용법:
//   node scripts/naver-blog-draft.mjs <html-file> "<제목>" "태그1,태그2"
// 옵션:
//   --inspect      아무것도 입력하지 않고 에디터 DOM 진단만 출력 (셀렉터가 깨졌을 때)
//   --keep-open    끝나도 크롬 창을 닫지 않음
//   --timeout N    최초 로그인 대기 초 (기본 300)
//   --publish      임시저장 대신 발행까지 진행 (기본값 아님. 명시할 때만)
//
// 네이버 로그인이 필요하므로 항상 창을 띄운다(headless 미지원).

import {
  CONFIG, log, launch, openEditor, buildBodyHtml, fillPost, screenshot, inspect, readSaveCount,
} from "./naver-blog-core.mjs";

const argv = process.argv.slice(2);
const flags = {
  inspect: argv.includes("--inspect"),
  keepOpen: argv.includes("--keep-open"),
  publish: argv.includes("--publish"),
  timeout: Number(argv[argv.indexOf("--timeout") + 1]) || CONFIG.loginTimeoutSec || 300,
};
const positional = argv.filter((a, i) => !a.startsWith("--") && argv[i - 1] !== "--timeout");
const [htmlFile, title, tagsArg] = positional;

if (!flags.inspect && (!htmlFile || !title)) {
  console.error(
    '사용법: node scripts/naver-blog-draft.mjs <html-file> "<제목>" "태그1,태그2" [--inspect|--keep-open|--publish|--timeout N]'
  );
  process.exit(1);
}

const tags = tagsArg
  ? tagsArg.split(",").map((s) => s.trim().replace(/^#/, "")).filter(Boolean)
  : [];

const { context, page } = await launch();

async function finish(code) {
  if (flags.keepOpen) {
    log("--keep-open: 창을 열어둡니다. 터미널에서 Ctrl+C로 종료하세요.");
    await new Promise(() => {});
  }
  await context.close();
  process.exit(code);
}

let editor;
try {
  editor = await openEditor(page, { loginTimeoutSec: flags.timeout });
} catch (err) {
  console.error(String(err.message || err));
  await finish(2);
}

if (flags.inspect) {
  console.log(JSON.stringify(await inspect(editor), null, 2));
  log(`스크린샷: ${await screenshot(page, "inspect")}`);
  await finish(0);
}

const before = await readSaveCount(editor);
if (before !== null) log(`저장 전 임시저장 개수: ${before}`);

const result = await fillPost(page, editor, {
  title,
  bodyHtml: buildBodyHtml(htmlFile),
  tags,
  publish: flags.publish,
});

if (!result.ok) {
  console.error(`실패: ${result.reason}. --inspect 로 셀렉터를 확인하고 naver-blog-config.json에 넣으세요.`);
  log(`스크린샷: ${await screenshot(page, "fail")}`);
  await finish(3);
}

// 초안이 실제로 생겼는지 검증 — 블로그 글 목록에는 발행글만 보이므로 이 카운터가 유일한 근거.
if (!flags.publish) {
  const after = await readSaveCount(editor);
  if (before !== null && after !== null) {
    log(`저장 후 임시저장 개수: ${after} (${after > before ? "증가 확인 ✓" : "증가 안 함 — 저장 실패 의심"})`);
  }
}
log(`완료. 스크린샷: ${await screenshot(page, flags.publish ? "publish" : "draft")}`);
log(`확인: https://blog.naver.com/${CONFIG.blogId}`);
await finish(0);
