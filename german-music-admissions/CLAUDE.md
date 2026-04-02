# CLAUDE.md — 독일 음대 입시 올인원 판별기

> 새 세션 시작 시 이 파일을 **먼저** 읽고, 작업 영역에 맞는 docs/ 파일을 추가로 읽어라.

---

## 이 프로젝트가 뭔가

한국 음대생·학부모·컨설턴트를 위한 **독일 24개 국립 음대 입시 정보 통합 플랫폼**.

단순 크롤러가 아니다. 정보 비대칭을 해소하는 데이터 플랫폼이다.

---

## 절대 규칙 3가지 (어떤 작업이든 항상 적용)

**1. 추측 데이터 생성 금지**
확인 안 된 필드는 무조건 `null`. 훈련 지식으로 학교 데이터 채우지 말 것.

**2. 코드 주석은 한국어**
지은님은 Python 초보자. 영어 주석 금지.

**3. 보호 파일 임의 수정 금지**
`universities.json` / `CLAUDE.md` / `docs/*.md` / `.github/workflows/crawl.yml` / `snapshots/`
→ 사용자 명시적 승인 없이 건드리지 말 것.

---

## 파일 구조

```
CLAUDE.md                    ← 지금 이 파일 (마스터)
docs/
  CLAUDE_DATA.md             ← universities.json 작업 시 읽기
  CLAUDE_CRAWLER.md          ← crawl_pipeline.py 작업 시 읽기
  CLAUDE_FRONTEND.md         ← german_music_app.html 작업 시 읽기
  CLAUDE_DEPLOY.md           ← GitHub Actions 배포 시 읽기
universities.json            ← 단일 진실 소스 [보호됨]
german_music_app.html        ← 프론트엔드
crawl_pipeline.py            ← 크롤러
requirements.txt             ← Python 의존성
.github/workflows/crawl.yml  ← 자동화 [보호됨]
snapshots/                   ← 크롤링 스냅샷 [보호됨]
```

---

## 사용자 정보

- 지은님 / Python 완전 초보 / C1 독일어 가능
- C1 독일어 실력 = 공식 PDF 직접 해독 가능 = 이 프로젝트의 핵심 경쟁력
- 모든 설명은 단계별로, 전문용어는 괄호로 설명 추가

---

## data_status 현황 (2026-03-31 기준)

확인됨 8개 / 부분확인 10개 / 미확인 6개 (에센·만하임·뮌헨·로스토크 등)

---

*다음 Claude에게: 작업 시작 전 해당 docs/ 파일을 반드시 읽을 것.*
