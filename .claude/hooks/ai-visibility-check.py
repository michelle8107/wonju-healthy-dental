#!/usr/bin/env python3
"""세션 시작 시 AI/검색 노출 상태 점검 (SessionStart hook).

자동 확인: 홈페이지·치과지식·sitemap·robots·og 이미지 응답, 라이브 페이지의 구조화 데이터(Dentist)·viewport·description,
로컬 커밋 미푸시 여부, 블로그 최근 발행일·Blogger 토큰, 인스타 최근 게시일과 치과지식 페이지 누락 캐러셀,
홈페이지 인스타 링크 불일치.
수동 체크리스트: .claude/ai-visibility-state.json 의 미완료 항목.

출력은 hook JSON(additionalContext + systemMessage). 네트워크 오류는 점검 실패로 표시만 하고 절대 세션을 막지 않는다.
"""
import datetime as dt
import json
import pathlib
import re
import subprocess
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = "https://healthydental.co.kr"
UA = {"User-Agent": "Mozilla/5.0 (healthydental visibility check)"}
TODAY = dt.date.today()


def fetch(url, data=None, headers=None, timeout=8):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # timeout, DNS, etc.
        return None, str(e).encode()


def env_local():
    env = {}
    f = ROOT / "dental-blog-autopost" / ".env.local"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$", line)
            if m:
                env[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return env


def check_site():
    ok, bad = [], []
    code, body = fetch(SITE + "/")
    if code != 200:
        return ok, [f"홈페이지 응답 이상 ({code})"]
    s = body.decode("utf-8", "replace")
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    try:
        ld = json.loads(m.group(1)) if m else None
    except ValueError:
        ld = None
    (ok if ld and ld.get("@type") == "Dentist" else bad).append("구조화 데이터(Dentist)" + ("" if ld else " 없음/깨짐"))
    for label, needle in (("viewport", 'name="viewport"'), ("meta description", 'name="description"'),
                          ("canonical", 'rel="canonical"'), ("치과지식 메뉴 링크", 'href="knowledge.html"')):
        (ok if needle in s else bad).append(label + ("" if needle in s else " 누락"))
    for path in ("knowledge.html", "sitemap.xml", "robots.txt", "og-image.jpg"):
        c, _ = fetch(f"{SITE}/{path}")
        (ok if c == 200 else bad).append(f"/{path}" + ("" if c == 200 else f" 응답 {c}"))
    ig_links = set(re.findall(r'instagram\.com/([A-Za-z0-9_.]+)/', s))
    if len(ig_links) > 1:
        bad.append("홈페이지 안 인스타 계정 링크가 서로 다름: " + ", ".join(sorted(ig_links)))
    return ok, bad


def check_git():
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "status", "-sb"], capture_output=True, text=True,
                             encoding="utf-8", timeout=8).stdout.splitlines()
    except Exception as e:
        return [f"git 상태 확인 실패: {e}"]
    head = out[0] if out else ""
    notes = []
    m = re.search(r"ahead (\d+)", head)
    if m:
        notes.append(f"푸시 안 된 커밋 {m.group(1)}개 — 홈페이지에 아직 반영 안 됨")
    changed = [l for l in out[1:] if l[:2].strip() and not l.startswith("??") and
               re.search(r"(index\.html|knowledge|sitemap|robots)", l)]
    if changed:
        notes.append("홈페이지 관련 파일에 커밋 안 된 변경 있음: " + ", ".join(l[3:] for l in changed[:5]))
    return notes


def check_blog(env):
    notes, info = [], []
    code, body = fetch("https://healthydentalwonju.blogspot.com/feeds/posts/summary?alt=json&max-results=1")
    if code == 200:
        e = json.loads(body)["feed"]["entry"][0]
        d = dt.date.fromisoformat(e["published"]["$t"][:10])
        age = (TODAY - d).days
        info.append(f"블로그 최근 글 {d} ({age}일 전): {e['title']['$t']}")
        if age > 4:
            notes.append(f"블로그 새 글이 {age}일째 없음 — 월·목 자동 발행(크론)·토큰 확인 필요")
    else:
        notes.append(f"블로그 피드 확인 실패 ({code})")
    if env.get("BLOGGER_REFRESH_TOKEN"):
        data = urllib.parse.urlencode({"client_id": env.get("BLOGGER_CLIENT_ID", ""),
                                       "client_secret": env.get("BLOGGER_CLIENT_SECRET", ""),
                                       "refresh_token": env["BLOGGER_REFRESH_TOKEN"],
                                       "grant_type": "refresh_token"}).encode()
        c, b = fetch("https://oauth2.googleapis.com/token", data=data,
                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        if c != 200:
            notes.append(f"Blogger 토큰 갱신 실패 ({c}) — 자동 발행이 멈췄을 수 있음. 스킬 문서의 토큰 재발급 절차 참고")
    return notes, info


def check_instagram(env):
    notes, info = [], []
    url, tok = env.get("KV_REST_API_URL"), env.get("KV_REST_API_TOKEN")
    if not (url and tok):
        return notes, ["인스타 점검 생략(.env.local 없음)"]
    c, b = fetch(f"{url}/get/instagram:access_token", headers={"Authorization": f"Bearer {tok}"})
    token = json.loads(b).get("result") if c == 200 else None
    if not token:
        return [f"인스타 토큰 조회 실패 ({c})"], info
    c, b = fetch("https://graph.instagram.com/v23.0/me/media?fields=media_type,permalink,timestamp&limit=50&access_token="
                 + urllib.parse.quote(token))
    if c != 200:
        return [f"인스타 API 응답 이상 ({c}) — 토큰 만료/차단 여부 확인"], info
    media = json.loads(b).get("data", [])
    if media:
        last = dt.date.fromisoformat(media[0]["timestamp"][:10])
        info.append(f"인스타 최근 게시 {last} ({(TODAY - last).days}일 전, {media[0]['media_type']})")
    try:
        listed = {i.get("instagram") for i in json.loads((ROOT / "knowledge" / "carousels.json").read_text(encoding="utf-8"))}
    except Exception:
        listed = set()
    missing = [m["permalink"] for m in media if m["media_type"] == "CAROUSEL_ALBUM" and m["permalink"] not in listed]
    if missing:
        notes.append(f"치과지식 페이지에 없는 발행 캐러셀 {len(missing)}개: " + ", ".join(missing[:5]))
    return notes, info


def manual_items():
    f = ROOT / ".claude" / "ai-visibility-state.json"
    try:
        items = json.loads(f.read_text(encoding="utf-8"))["manual_items"]
    except Exception:
        return []
    return [f"[{i['status']}] {i['title']}" + (f" — {i['note']}" if i.get("note") else "")
            for i in items if i.get("status") != "done"]


def main():
    env = env_local()
    with ThreadPoolExecutor(max_workers=4) as ex:
        f_site, f_git = ex.submit(check_site), ex.submit(check_git)
        f_blog, f_ig = ex.submit(check_blog, env), ex.submit(check_instagram, env)
        site_ok, site_bad = f_site.result()
        git_notes = f_git.result()
        blog_notes, blog_info = f_blog.result()
        ig_notes, ig_info = f_ig.result()
    problems = site_bad + git_notes + blog_notes + ig_notes
    pending = manual_items()

    lines = [f"## AI/검색 노출 점검 ({TODAY})",
             "자동 점검 통과: " + (", ".join(site_ok) if site_ok else "없음"),
             *blog_info, *ig_info,
             "### 조치 필요" if problems else "### 조치 필요: 없음",
             *[f"- {p}" for p in problems],
             "### 미완료 수동 항목 (.claude/ai-visibility-state.json)",
             *([f"- {p}" for p in pending] or ["- 없음"]),
             "",
             "세션 첫 응답에서 사용자에게 위 점검 결과를 짧게 보고할 것(조치 필요·미완료 항목 위주). "
             "수동 항목이 완료되면 state 파일의 status를 done으로 바꿀 것."]
    summary = f"AI/검색 노출 점검: 조치 필요 {len(problems)}건 · 미완료 수동 항목 {len(pending)}건"
    print(json.dumps({"systemMessage": summary,
                      "hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": "\n".join(lines)}}, ensure_ascii=True))


if __name__ == "__main__":
    main()
