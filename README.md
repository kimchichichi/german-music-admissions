# 독일 음대 입시 올인원 판별기

> 한국 음대생·학부모·컨설턴트를 위한 **독일 24개 국립 음대 입시 정보 통합 플랫폼**

![Status](https://img.shields.io/badge/version-2.1-blue)
![Schools](https://img.shields.io/badge/schools-24-green)
![Data](https://img.shields.io/badge/data%20verified-11%20%7C%20partial%2013-orange)

---

## 📋  프로젝트 소개

단순한 크롤러가 아닙니다. **정보 비대칭을 해소하는 데이터 플랫폼**입니다.

### 핵심 기능
- 🎼 **24개 독일 음대** 입시 정보 통합
- 🔍 **악기별·조건별 필터**: 나에게 맞는 학교 찾기
- 📅 **마감일 관리**: 겨울/여름 학기 모두 지원
- 🌍 **언어 조건**: 각 학교별 독일어 요구 수준
- 🎯 **1차 전형**: 영상 제출? 현장? 서류?
- 💰 **지원 절차**: 비용·플랫폼·제출 방식

---

## 🚀 빠른 시작

### 1. 웹 앱 실행
```bash
# german_music_v4.html을 브라우저에서 열기
open german_music_v4.html

# Mac 터미널
cd /path/to/german-music-admissions
open german_music_v4.html
```

### 2. 데이터 동기화
```bash
# universities.json이 변경된 후 HTML 업데이트
python3 sync_html_data.py
```

### 3. 데이터 검증
```bash
# UI 데이터 동기화 상태 확인
# Claude Code에서: /ui-update 스킬 실행
```

---

## 📁 파일 구조

```
├── README.md                    ← 이 파일
├── CLAUDE.md                    ← 개발 규칙 & 마스터 가이드
├── docs/
│   ├── CLAUDE_DATA.md          ← universities.json 작업 시 읽기
│   ├── CLAUDE_CRAWLER.md       ← crawl_pipeline.py 작업 시 읽기
│   ├── CLAUDE_FRONTEND.md      ← german_music_app.html 작업 시 읽기
│   └── CLAUDE_DEPLOY.md        ← GitHub Actions 배포 시 읽기
│
├── universities.json            ← 단일 진실 소스 (24개 학교 정보)
├── german_music_v4.html        ← 프론트엔드 (단일 HTML 파일)
├── sync_html_data.py           ← 자동 동기화 스크립트
├── crawl_pipeline.py           ← 크롤러 (확장용)
├── requirements.txt            ← Python 의존성
│
├── .github/workflows/
│   └── crawl.yml               ← 자동화 파이프라인
│
└── snapshots/                  ← 크롤링 스냅샷 아카이브
```

---

## 📊 데이터 현황

| 구분 | 학교 수 |
|------|--------|
| **확인됨** (verified) | 11개 |
| **부분확인** (partial) | 13개 |
| **미확인** (unverified) | 0개 |
| **합계** | **24개** |

### 확인된 정보
- ✅ 전공(악기) 목록
- ✅ 마감일 (겨울/여름)
- ✅ 언어 조건
- ✅ 1차 전형 방식
- ✅ 지원 플랫폼

---

## 🎓 포함된 24개 음대

### 베를린권
1. 한스 아이슬러 음악대학 베를린
2. 베를린 예술대학 (음악학부)

### 함부르크권
3. 함부르크 음악연극대학

### 북독일권
4. 브레멘 예술대학 (음악학부)
5. 한노버 음악연극미디어대학
6. 뤼베크 음악대학
7. 로스토크 음악연극대학

### 중부독일권
8. 데트몰트 음악대학
9. 쾰른 음악무용대학
10. 뒤셀도르프 로베르트 슈만 음악대학

### 남서독일권
11. 프랑크푸르트 음악공연예술대학
12. 프라이부르크 음악대학
13. 카를스루에 음악대학
14. 슈투트가르트 음악공연예술대학
15. 트로싱엔 음악대학

### 남동독일권
16. 뉘른베르크 음악대학
17. 바이마르 프란츠 리스트 음악대학
18. 뷔르츠부르크 음악대학

### 동독일권
19. 드레스덴 음악대학 칼 마리아 폰 베버
20. 라이프치히 음악연극대학

### 서독일권
21. 에센 폴크방 예술대학
22. 만하임 음악공연예술대학

### 바이에른
23. 뮌헨 음악연극대학

### 자를란트
24. 자르브뤼켄 자를란트 음악대학

---

## 🔧 기술 스택

### 프론트엔드
- **HTML5** (단일 파일, 서버 불필요)
- **CSS3** (모바일 반응형)
- **Vanilla JavaScript** (프레임워크 무관)
- **Google Fonts** (Playfair Display, Source Sans 3)

### 데이터 관리
- **JSON** (universities.json)
- **Python 3** (동기화 & 크롤링)

### 배포
- **GitHub Pages** (정적 호스팅)
- **GitHub Actions** (자동화)

---

## 📖 사용 가이드

### 1. 학교 찾기
```
1. german_music_v4.html 열기
2. 필터 선택:
   - 악기 (다중 선택)
   - 언어조건
   - 1차 전형 방식
   - 지원 플랫폼
3. 조건에 맞는 학교 카드 클릭
4. 상세 정보 모달 확인
```

### 2. 상세 정보 보기
각 학교 카드에는:
- 📍 도시 & 학교명
- 🎵 제공 악기/전공
- 📅 마감일 (겨울/여름)
- 🌍 언어 조건 & 제출 시점
- 🎯 1차 전형 방식
- 💰 지원비 & 플랫폼
- 📝 주요 공지사항

### 3. 데이터 정확도
- **확인됨**: 공식 웹사이트 & PDF에서 직접 확인
- **부분확인**: 일부 정보는 확인, 일부는 미확인
- **null 필드**: "미확인"으로 표시 (추측값 없음)

---

## 🔄 데이터 업데이트

### 자동 동기화
```bash
# universities.json 수정 후 실행
python3 sync_html_data.py

# 결과
# - JSON 읽기
# - 필드 매핑 (deadline_winter → deadline_w 등)
# - null → "미확인" 변환
# - HTML SCHOOLS 배열 교체
```

### 데이터 추가 규칙
**CLAUDE.md 참고:**
1. ✅ 확인된 정보만 입력
2. ❌ 추측 데이터 금지 (반드시 `null`)
3. ✅ 공식 출처 검증 필수
4. ✅ 한국어 주석만 사용

---

## 📝 주요 필드 설명

### universities.json 구조

```json
{
  "id": 1,
  "name": "학교명 (한국어)",
  "name_de": "학교명 (독일어)",
  "city": "도시",
  "data_status": "확인됨 | 부분확인",

  "bewerbung_url": "https://공식지원페이지",
  "degrees": ["Bachelor", "Master", "Konzertexamen"],
  "instruments": ["악기1", "악기2", ...],

  "deadline_winter": "마감일 (겨울)",
  "deadline_summer": "마감일 (여름)",

  "lang_level": "B2 | TestDaF | 없음 | 미확인",
  "lang_text": "언어 조건 설명",
  "lang_timing": "before_enroll | conditional | 등록전 | 없음",

  "round1_type": "영상 | 현장 | 영상+현장 | 영상+서류",
  "round1_text": "1차 전형 상세 설명",

  "portal": "muvac | 자체포털 | 우편",
  "fee": "지원비 (EUR)",
  "note": "주요 공지사항"
}
```

---

## 🌐 접근 방법

### 로컬 실행 (추천)
```bash
# 파인더에서 german_music_v4.html 더블클릭
# 또는 터미널에서
open german_music_v4.html
```

### 온라인 배포
- GitHub Pages로 호스팅 가능
- `.github/workflows/crawl.yml` 참고

---

## 🔐 데이터 무결성

### 보호 파일 (자동 동기화)
- `universities.json` ← 마스터 데이터 소스
- `german_music_v4.html` ← sync_html_data.py로 자동 갱신

### 사용자 변경 금지
명시적 승인 없이는 수정 불가:
- `CLAUDE.md`
- `docs/*.md`
- `.github/workflows/crawl.yml`
- `snapshots/`

---

## 📞 연락처 & 기여

### 데이터 제보
공식 웹사이트에서 확인한 정보가 있다면:
1. 해당 학교 상세보기 열기
2. "공식 입시 페이지" 링크 확인
3. 누락 정보 발견 시 이슈 제출

### 버그 리포트
기술적 문제 발생 시:
1. 브라우저 개발자도구 (F12) 열기
2. Console 탭에서 에러 확인
3. GitHub Issues에 스크린샷과 함께 제출

---

## 📚 추가 리소스

### 공식 가이드
- [CLAUDE.md](./CLAUDE.md) - 개발 규칙
- [CLAUDE_DATA.md](./docs/CLAUDE_DATA.md) - 데이터 구조
- [CLAUDE_FRONTEND.md](./docs/CLAUDE_FRONTEND.md) - UI 가이드

### 독일 음대 정보
- [RKM (독일 음대 협회)](https://www.rkm-online.de)
- [DAAD](https://www.daad.de) - 독일 유학 정보
- 각 학교 공식 웹사이트

---

## 📈 프로젝트 현황

### ✅ 완료된 작업
- 24개 음대 기본 정보 수집
- 전공(악기) 목록 추가
- 1차 전형 방식 검증
- R1MAP 한국어 매핑
- 자동 동기화 스크립트

### 🚧 진행 중
- 추가 필드 검증
- 데이터 정확도 개선

---

## 📄 라이선스

이 프로젝트는 **교육 목적**으로 공개됩니다.

---

## 🎵 마지막으로

이 플랫폼은 **정보 비대칭을 줄이기 위해** 만들어졌습니다.

공식 정보만 수록하고, 추측은 절대 하지 않습니다.
불확실한 부분은 `null` (미확인)로 표시합니다.

**독일 음대 입시, 이제 더 이상 어렵지 않습니다.** 🎼✨

---

**최종 업데이트**: 2026년 4월 4일
**데이터 기준**: 각 학교 공식 웹사이트 & PDF (2026년 입시)
