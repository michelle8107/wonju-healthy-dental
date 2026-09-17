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
