// 네이버 블로그 자동화 공용 모듈.
//
// 네이버는 블로그 글쓰기 공식 API를 제공하지 않는다(구 오픈API 글쓰기는 종료).
// 그래서 티스토리와 같은 방식으로 실제 크롬을 Playwright로 띄워 스마트에디터 ONE을
// 조작하고, 기본은 "저장"(임시저장)까지만 자동으로 처리한다. 발행은 사람이 검토 후 누른다.
//
// naver-blog-draft.mjs(한 편) / naver-blog-backfill.mjs(여러 편)가 이 모듈을 쓴다.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const ROOT = path.resolve(__dirname, "..");
export const CONFIG = JSON.parse(
  fs.readFileSync(path.join(__dirname, "naver-blog-config.json"), "utf8")
);

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
export const log = (...a) => console.log("[naver]", ...a);

// 블로거(lib/blogger.ts)와 동일한 병원 정보 푸터. 주소/전화번호를 매번 다시 쓰지 않도록 고정.
// 네이버 에디터는 붙여넣기 시 inline style 대부분을 버리므로 여기서는 태그를 최소화한다.
export const CLINIC_FOOTER = [
  "<p>&nbsp;</p>",
  "<p>원주 건강한치과</p>",
  "<p>강원특별자치도 원주시 건강로 21, 2층 (반곡동 조은빌딩, 국민건강보험공단 앞)</p>",
  "<p>TEL. 033-734-2275</p>",
  '<p>카카오톡 상담 문의: <a href="https://pf.kakao.com/_YCjxaX/chat">https://pf.kakao.com/_YCjxaX/chat</a></p>',
  "<p>이 글은 일반적인 치아 건강 정보 제공을 목적으로 하며, 정확한 진단과 처방은 내원 후 상담을 통해 받으실 수 있습니다.</p>",
].join("\n");

// ------------------------------------------------------- 셀렉터 후보 목록
//
// 스마트에디터 ONE은 클래스명에 해시가 붙어(.save_btn__xxxxx) 배포마다 바뀔 수 있다.
// 그래서 해시 없는 구조 셀렉터 → 부분일치 순으로 후보를 두고 처음 보이는 걸 쓴다.
// config.json의 selectors 값이 있으면 그게 최우선.

const CANDIDATES = {
  title: [
    ".se-section-documentTitle .se-text-paragraph",
    ".se-documentTitle .se-text-paragraph",
    ".se-section-documentTitle",
  ],
  body: [
    ".se-section-text .se-text-paragraph",
    ".se-component.se-text .se-text-paragraph",
    ".se-main-container .se-text-paragraph",
  ],
  tagInput: ["#tag-input", "[class*='tag_input'] input", "input[placeholder*='태그']"],
  saveButton: ["[class*='save_btn']", "button[class*='save_btn']", ".btn_save"],
  publishButton: ["[class*='publish_btn']", "button[class*='publish_btn']"],
  restorePopupCancel: [".se-popup-button-cancel", ".se-popup-button.se-popup-button-cancel"],
  helpClose: [".se-help-panel-close-button", ".se-utils-close-button", "[class*='help_close']"],
};

function pick(name) {
  const override = CONFIG.selectors?.[name];
  const base = CANDIDATES[name] || [];
  return override ? [override, ...base] : base;
}

export async function firstVisible(scope, name, { timeout = 8000 } = {}) {
  const list = pick(name);
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    for (const sel of list) {
      const loc = scope.locator(sel).first();
      if (await loc.isVisible().catch(() => false)) return loc;
    }
    await sleep(250);
  }
  return null;
}

export function shotDir() {
  const dir = path.join(ROOT, CONFIG.shotDir);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

// ------------------------------------------------------------- 브라우저

export async function launch() {
  const profileDir = path.join(ROOT, CONFIG.profileDir);
  log(`프로필: ${profileDir}`);
  const context = await chromium.launchPersistentContext(profileDir, {
    channel: "chrome",
    headless: false,
    viewport: { width: 1440, height: 960 },
    locale: "ko-KR",
    timezoneId: "Asia/Seoul",
    // 네이버는 자동화 브라우저를 감지해 로그인을 막는다. 실제 크롬 + 이 플래그 조합으로
    // navigator.webdriver 노출을 없앤다. (그래도 캡차가 뜨면 사용자가 창에서 직접 푼다.)
    args: ["--disable-blink-features=AutomationControlled"],
  });
  await context
    .grantPermissions(["clipboard-read", "clipboard-write"], { origin: "https://blog.naver.com" })
    .catch(() => log("클립보드 권한 부여 실패 — 붙여넣기 대신 평문 타이핑으로 넘어갈 수 있음."));

  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(20000);
  return { context, page };
}

export const WRITE_URL = `https://blog.naver.com/${CONFIG.blogId}?Redirect=Write`;

// 새 글 작성 화면을 열고, 로그인이 필요하면 사람이 창에서 로그인할 때까지 기다린다.
// 성공하면 에디터가 들어있는 frame(또는 page)을 돌려준다.
export async function openEditor(page, { loginTimeoutSec = CONFIG.loginTimeoutSec || 300 } = {}) {
  log(`글쓰기 페이지 이동: ${WRITE_URL}`);
  await page.goto(WRITE_URL, { waitUntil: "domcontentloaded" });

  if (page.url().includes("nid.naver.com")) {
    log(`로그인 필요 — 열린 크롬 창에서 직접 로그인하세요. 최대 ${loginTimeoutSec}초 대기합니다.`);
    // ID/PW 입력 후에도 "새로운 기기 등록" 같은 안내 페이지가 nid.naver.com에 그대로 머무는
    // 경우가 있어서, URL이 바뀔 때마다 찍어준다 — 어디서 멈췄는지 터미널로 보이게.
    const deadline = Date.now() + loginTimeoutSec * 1000;
    let last = "";
    while (Date.now() < deadline && page.url().includes("nid.naver.com")) {
      const now = page.url();
      if (now !== last) {
        log(`  현재 URL: ${now}`);
        last = now;
      }
      await sleep(1000);
    }
    if (page.url().includes("nid.naver.com")) {
      const shot = path.join(shotDir(), `login-timeout-${Date.now()}.png`);
      await page.screenshot({ path: shot }).catch(() => {});
      throw new Error(
        `로그인 대기 시간 초과 (마지막 URL: ${page.url()}). 화면: ${shot}\n` +
          `"새로운 기기 등록" 같은 안내 페이지에서 멈춰 있으면 그 버튼까지 눌러주세요.`
      );
    }
    log(`로그인 확인됨 → ${page.url()}`);
    await page.goto(WRITE_URL, { waitUntil: "domcontentloaded" });
  }

  // 블로그 홈이 frameset이라 에디터가 #mainFrame 안에 뜬다.
  let editor = page;
  const mainFrameEl = await page.$("#mainFrame");
  if (mainFrameEl) {
    editor = await mainFrameEl.contentFrame();
    log("에디터가 #mainFrame 안에 있음.");
  } else {
    log("에디터가 최상위 문서에 있음.");
  }

  await editor.waitForSelector(".se-main-container, .se-content", { timeout: 30000 }).catch(() => {
    log("경고: 스마트에디터 ONE 컨테이너를 못 찾았습니다. --inspect 로 확인하세요.");
  });

  await dismissPopups(editor);
  return editor;
}

// "작성 중인 글이 있습니다" 복구 팝업은 항상 취소한다 — 늘 새 글로 시작해야
// 이전 편 내용이 섞이지 않는다. 도움말 패널도 닫는다.
export async function dismissPopups(editor) {
  const cancel = await firstVisible(editor, "restorePopupCancel", { timeout: 4000 });
  if (cancel) {
    log("작성 중 글 복구 팝업 → 취소 (항상 새 글로 시작)");
    await cancel.click().catch(() => {});
    await sleep(800);
  }
  const helpClose = await firstVisible(editor, "helpClose", { timeout: 2500 });
  if (helpClose) {
    log("도움말 패널 닫기");
    await helpClose.click().catch(() => {});
    await sleep(500);
  }
}

// ------------------------------------------------------------- 본문 조립

export function buildBodyHtml(htmlFile) {
  const raw = fs.readFileSync(path.resolve(htmlFile), "utf8");
  const cleaned = raw
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .trim();
  return `${cleaned}\n${CLINIC_FOOTER}`;
}

export function htmlToPlain(html) {
  return html
    .replace(/<\/(p|div|h[1-6]|li|tr)>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

// ------------------------------------------------------- 한 편 채워넣기
//
// 반환: { ok: true } 또는 { ok: false, reason }

export async function fillPost(page, editor, { title, bodyHtml, tags = [], publish = false }) {
  // 제목
  const titleEl = await firstVisible(editor, "title", { timeout: 15000 });
  if (!titleEl) return { ok: false, reason: "제목 입력 영역을 찾지 못함" };
  log(`제목 입력: ${title}`);
  await titleEl.click();
  await page.keyboard.type(title, { delay: 20 });
  await sleep(500);

  // 본문 — 스마트에디터 ONE은 innerHTML 주입을 인식하지 않는다(내부 문서 모델이 따로 있음).
  // 대신 클립보드에 text/html을 넣고 Ctrl+V — 에디터의 붙여넣기 핸들러가 자기 컴포넌트로 변환한다.
  const bodyEl = await firstVisible(editor, "body", { timeout: 10000 });
  if (!bodyEl) return { ok: false, reason: "본문 영역을 찾지 못함" };
  log(`본문 붙여넣기 (HTML ${bodyHtml.length}자)`);
  await bodyEl.click();
  await sleep(300);

  const pasted = await editor.evaluate(async (html) => {
    try {
      const plain = html.replace(/<[^>]+>/g, "").replace(/\n{3,}/g, "\n\n");
      await navigator.clipboard.write([
        new ClipboardItem({
          "text/html": new Blob([html], { type: "text/html" }),
          "text/plain": new Blob([plain], { type: "text/plain" }),
        }),
      ]);
      return true;
    } catch (e) {
      return String(e);
    }
  }, bodyHtml);

  if (pasted === true) {
    await page.keyboard.press("Control+V");
    await sleep(2500);
    log("붙여넣기 완료.");
  } else {
    // 클립보드가 막히면 텍스트로라도 넣는다 (서식은 사용자가 에디터에서 다듬음).
    log(`클립보드 실패(${pasted}) → 평문 타이핑으로 대체`);
    await page.keyboard.type(htmlToPlain(bodyHtml), { delay: 3 });
  }

  // 저장 / 발행
  //
  // 태그는 글쓰기 화면에 없다 — 네이버는 태그 입력란을 "발행" 레이어 안에 둔다
  // (2026-09-05 --inspect로 확인: 글쓰기 화면의 input은 글감 검색창 하나뿐).
  // 그래서 임시저장 경로에서는 태그를 넣을 수 없고, 발행 경로에서만 레이어 안에서 넣는다.
  if (publish) {
    const pub = await firstVisible(editor, "publishButton", { timeout: 8000 });
    if (!pub) return { ok: false, reason: "발행 버튼을 못 찾음" };
    log("발행 레이어 열기");
    await pub.click();
    await sleep(2000);

    if (tags.length) {
      const tagEl = await firstVisible(editor, "tagInput", { timeout: 5000 });
      if (tagEl) {
        log(`태그 ${tags.length}개 입력 (발행 레이어)`);
        await tagEl.click();
        for (const t of tags) {
          await page.keyboard.type(t, { delay: 20 });
          await page.keyboard.press("Enter");
          await sleep(250);
        }
      } else {
        log(`태그 입력란을 못 찾음 — 직접 입력하세요: ${tags.map((t) => `#${t}`).join(" ")}`);
      }
    }

    const confirm = editor.locator("[class*='confirm_btn'], .btn_apply").last();
    await confirm.click().catch(() => log("최종 발행 버튼 클릭 실패 — 창에서 직접 눌러주세요."));
    await sleep(3000);
  } else {
    const save = await firstVisible(editor, "saveButton", { timeout: 8000 });
    if (!save) return { ok: false, reason: "저장(임시저장) 버튼을 못 찾음" };
    log("임시저장 클릭");
    await save.click();
    await sleep(3000);
    if (tags.length) {
      log(`태그는 임시저장에 안 들어갑니다. 발행할 때 붙여넣으세요: ${tags.map((t) => `#${t}`).join(" ")}`);
    }
  }

  return { ok: true, tags };
}

// 임시저장 개수를 읽는다. 블로그 글 목록에는 발행글만 보이므로, 초안이 실제로 생겼는지는
// 에디터 상단의 "저장 N" 카운터로만 확인할 수 있다. 저장 전후로 비교해서 검증에 쓴다.
export async function readSaveCount(editor) {
  const el = editor.locator("[class*='save_count_btn']").first();
  const txt = await el.innerText().catch(() => "");
  const n = parseInt(String(txt).replace(/[^0-9]/g, ""), 10);
  return Number.isNaN(n) ? null : n;
}

export async function screenshot(page, name) {
  const file = path.join(shotDir(), `${name}-${Date.now()}.png`);
  await page.screenshot({ path: file }).catch(() => {});
  return file;
}

// --inspect 용 DOM 진단
export async function inspect(editor) {
  return editor.evaluate(() => {
    const seen = (sel) =>
      Array.from(document.querySelectorAll(sel))
        .slice(0, 8)
        .map((el) => ({
          tag: el.tagName.toLowerCase(),
          cls: String(el.className || "").slice(0, 120),
          text: (el.innerText || "").trim().slice(0, 40),
          editable: el.getAttribute("contenteditable"),
        }));
    return {
      url: location.href,
      contenteditable: seen("[contenteditable='true']"),
      seSections: seen("[class^='se-section']"),
      buttons: Array.from(document.querySelectorAll("button, a[role='button']"))
        .filter((b) => b.offsetParent !== null)
        .slice(0, 40)
        .map((b) => `${(b.innerText || "").trim().slice(0, 20)} :: ${String(b.className || "").slice(0, 80)}`),
      inputs: Array.from(document.querySelectorAll("input"))
        .slice(0, 20)
        .map((i) => `${i.id || "(no id)"} :: ${i.placeholder || ""} :: ${String(i.className || "").slice(0, 60)}`),
    };
  });
}
