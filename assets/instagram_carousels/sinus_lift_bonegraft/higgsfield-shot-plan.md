# 상악동 거상술 영상 — Higgsfield 샷 플랜 (2026-09-17 작성)

## 경위
- 참조: https://www.instagram.com/reel/DdUee2SxGGx/ (mundodontoo, 측방 창 상악동 거상술, 본인들도 "AI 콘텐츠" 표기)
- 1차로 2D 모식도 영상(`00_video.mp4`, 30초, ASMR)을 만들었으나 사용자 피드백 "그림이 직관적이지 않다 → 3D로".
- 2차로 numpy SDF 레이마칭 3D 렌더러(`scripts/sinus_lift_3d.py`)를 자체 제작. 기구·창·점막·이식재·
  차폐막·임플란트가 전부 CSG 파라미터로 동작하지만, 뼈 형태가 "턱뼈"로 읽히지 않아 사용자가 중단시키고
  **Higgsfield로 생성하기로 결정**.
- 이 세션에서는 Higgsfield MCP 도구가 로드되지 않았고(계정 커넥터라 세션 시작 시점에만 등록됨),
  크롬 확장도 중간에 연결이 끊겨 생성까지 가지 못했다. **다음 세션에서 이 파일대로 이어서 진행할 것.**

## 저작권 방침 (사용자 지시: "카피에 안 걸리게")
- 참조 릴스의 영상·캡션·나레이션은 일절 사용하지 않는다. 시술 절차 자체는 의학적 사실이라 저작권 대상이 아님.
- 화면은 아래 프롬프트로 새로 생성, 자막·나레이션·색보정·ASMR은 이미 만든 우리 것을 쓴다.
- 생성물에 특정 제작자의 화면 구성(건조 표본 위 오버레이 등)을 그대로 재현하지 않는다.

## 샷 리스트 (5컷 × 5초, 9:16 생성 후 4:5로 센터 크롭)
메모리 원칙대로 **컷당 첫 테이크만 사용, 투기적 변형 생성 금지**. 5컷 ≈ 163크레딧(32.5/컷).

| # | 프롬프트 요지 | 비고 |
|---|---|---|
| 1 | 위 어금니 부위 상악골 클로즈업. 어금니 한 자리가 비어 있고 그 위 뼈가 얇다. 카메라 천천히 전진 | establishing |
| 2 | 바깥(볼쪽) 뼈벽에 타원형 창이 만들어진다 | 기구는 넣지 말 것(무섭게 보임) |
| 3 | 창 안쪽의 얇은 분홍 막이 찢어지지 않고 부드럽게 위로 들려 올라간다 | 핵심 컷 |
| 4 | 들린 공간에 흰 알갱이 형태의 뼈이식재가 아래부터 차오른다 | |
| 5 | 나사 형태 임플란트가 아래에서 올라와 자리 잡는다 | |

- 모델/파라미터는 `geonchi-shorts` 스킬의 "Video generation" 절을 따른다
  (`seedance_2_5`, `generate_audio: false`, `generate_video_batch` → `jobs_wait`).
- 레퍼런스 이미지가 필요하면 `scripts/sinus_lift_3d.py`로 뽑은 스틸을 `omni_reference`로 넣어
  해부 구조를 고정할 수 있다(형태 통제용).

## 재사용할 자산 (다시 만들지 말 것)
- ASMR 오디오: `scripts/_sinus_anim_frames/asmr.wav` (30.4초, -21.7dBFS).
  장면별 사운드 시작 시각은 `scripts/gen-sinus-lift-anim.py`의 `build_audio()` 참조.
  새 컷 길이에 맞춰 `place()` 시각만 조정하면 된다. **사용자 평가: "소리는 좋다"**
- 캐러셀 8장: `01.png` ~ `08.png` (노랑/골드 팔레트, 사용자 확인 완료)
- 캡션: `caption.txt` (의료광고법 검토 완료)
- 발행: `scripts/publish-instagram-carousel.mjs` — 이미 mp4 혼합 캐러셀 지원하도록 수정해 둠
  (mp4는 `media_type=VIDEO` 자식으로 올리고 인코딩 완료까지 폴링)

## 남은 순서
1. Higgsfield 5컷 생성 → 4:5 크롭 → 자막(`gen-sinus-lift-anim.py`의 자막 레이어 재사용) + ASMR 합성
2. 사용자 확인
3. `publish-instagram-carousel.mjs <폴더> "<caption.txt 내용>"` 로 영상+8장 한 게시물 발행
4. `knowledge/carousels.json` 맨 앞에 항목 추가 → `python knowledge/build.py` → 커밋·푸시
5. Redis `dental-blog:recent-topics`에 주제 추가

## 2026-09-18 1차 생성 결과 (텍스트→영상, 레퍼런스 없음, 130크레딧 차감)
클립: `dental-blog-autopost/scripts/_sinus_hf_clips/shot{1,2,3,5}.mp4` (720x1280, 5.04초), 컷별 콘택트시트 `sheet*.jpg`
| # | job_id | 판정 |
|---|---|---|
| 1 | 3b109743-76b8-4c5a-b73e-5f7be9374009 | 쓸 만함 — 두개골 측면, 어금니 자리로 줌인 |
| 2 | b5066dd7-d5f3-45a7-b268-6564d0794d33 | **해부학적으로 틀림** — 뼈가 아니라 치아 머리에 구멍(충치처럼 보임) |
| 3 | 0dbd9bfa-5a92-46dc-af7f-f55b0701bba9 | 쓸 만함 — 렌즈형 공간에서 분홍 점막이 위로 들림 |
| 4 | 9b684e07-2820-416c-9f5c-3de4c0b6edb8 | NSFW 필터 오탐으로 실패(크레딧 환불) — 프롬프트 표현 바꿔 재시도 필요 |
| 5 | 14c48960-5f27-4df0-9f34-6edcfc24c7d7 | **틀림** — 임플란트가 멀쩡한 치아를 뚫고 위로 길게 솟음 |

교훈: 텍스트만으로는 seedance가 "뼈 vs 치아" 구분을 못 한다. 해부 구조를 고정하려면 스틸 이미지를 먼저 만들고
(이미지 생성은 싸서 반복 가능) 그 이미지를 시작 프레임/레퍼런스로 영상화하는 편이 낫다.

합성 스크립트: `dental-blog-autopost/scripts/gen-sinus-lift-video.py` (인트로 2.6초 + 4.6초×5컷 + 아웃트로 3.2초 = 28.8초,
자막·ASMR을 새 타이밍으로 재배치, 아웃트로에 "AI로 생성한 3D 애니메이션" 고지). caption.txt도 같은 고지로 수정(원본은 caption_2d_backup.txt).

## 2026-09-18 결정 변경: 영상 중단 → 3D 스틸 캐러셀 (사용자 "그냥 스틸 이미지로 형상화하자, 동영상 하지말고")
- 스틸은 `gpt_image_2_5`(장당 1크레딧). 단면도는 기준 1장(`anatomy`)을 만든 뒤 **이전 결과를 레퍼런스로 편집을 이어가서**
  (점막 거상 → 이식재 → 임플란트) 구도·재질을 일치시켰다. 텍스트만으로 영상 생성했을 때 생긴 해부 오류가 없었다.
- 원본: `src_3d/` (anatomy / step1_window / step2_lift / step3_graft / step4_implant). job_id: ed69dacb(anatomy), 2b42fdd6(window),
  4dc1ed3f(lift), 0bf687ae(graft), 7117316e(implant).
- 캐러셀 10장으로 재구성(`gen-sinus-lift-carousel.py`의 `slide_image`), 각 그림 장에 AI 생성 고지. 옛 2D 영상은 `_archive_2d/`로 옮김
  (발행 스크립트가 폴더의 mp4를 집어가므로 최상위에 두면 안 됨).
- 남은 순서: 사용자 확인 → 발행 → knowledge/carousels.json → Redis. 영상 합성 스크립트 `gen-sinus-lift-video.py`는 미사용.
