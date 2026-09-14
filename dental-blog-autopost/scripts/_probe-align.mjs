// 일회성 진단: 정렬 드롭다운을 열어 옵션 버튼 클래스명을 확인한다. 확인 후 삭제.
import { launch, openEditor, sleep, log } from "./naver-blog-core.mjs";

const { context, page } = await launch();
const editor = await openEditor(page, { loginTimeoutSec: 120 });

// 본문에 포커스를 준 뒤 정렬 드롭다운 열기
await editor.locator(".se-section-text .se-text-paragraph").first().click();
await sleep(500);

const alignBtn = editor.locator("[class*='toolbar-button'][class*='se-align-']").first();
log(`정렬 버튼 클래스: ${await alignBtn.getAttribute("class")}`);
await alignBtn.click();
await sleep(800);

const opts = await editor.evaluate(() =>
  Array.from(document.querySelectorAll("button, li, a"))
    .filter((b) => b.offsetParent !== null && /align/i.test(String(b.className || "")))
    .map((b) => `${(b.innerText || b.getAttribute("aria-label") || "").trim().slice(0, 20)} :: ${String(b.className || "").slice(0, 100)}`)
);
console.log(JSON.stringify(opts, null, 2));
await page.screenshot({ path: "./.naver-shots/probe-align.png" });
await context.close();
