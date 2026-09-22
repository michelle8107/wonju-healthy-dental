"""PreToolUse guard: block Notion replace_content on the client report page.

replace_content ignores any selection and overwrites the whole page; on 2026-09-20
this wiped the client report. Partial edits must use update_content (old_str/new_str).
"""
import json
import sys

sys.stderr.reconfigure(encoding="utf-8")

REPORT_ID = "3ca52ea50362816b9c6ec7d0883afee1"

data = json.load(sys.stdin)
inp = data.get("tool_input", {}) or {}
page = str(inp.get("page_id", "")).replace("-", "")
if inp.get("command") == "replace_content" and REPORT_ID in page:
    print(
        "차단: 고객 노션 리포트에 replace_content 금지 — 페이지 전체가 지워집니다. "
        "부분 수정은 update_content(old_str/new_str)로, 새 행 추가도 update_content로 하세요. "
        "전체 복원이 꼭 필요하면 사용자에게 먼저 확인받고 이 훅을 잠시 끄세요.",
        file=sys.stderr,
    )
    sys.exit(2)
