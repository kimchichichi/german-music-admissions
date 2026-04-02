# CLAUDE_FRONTEND.md — german_music_app.html 규칙

> 프론트엔드 UI 수정 시 이 파일을 읽어라.
> 마스터 규칙(CLAUDE.md)도 반드시 읽어야 한다.

---

## 핵심 원칙

```
단일 HTML 파일. 서버 불필요. 브라우저에서 바로 열림.
```

별도 CSS 파일, JS 파일 만들지 말 것. 모든 것이 하나의 .html 안에 있어야 한다.

---

## 디자인 시스템

**폰트**
- 제목: `Playfair Display` (Google Fonts)
- 본문: `Source Sans 3` (Google Fonts)

**컬러 팔레트 (mint/pink/purple/teal)**
```css
--mint:   #a8d5c2
--pink:   #f0a8b8
--purple: #b8a8d5
--teal:   #a8c8d5
--bg:     #fafaf8
--text:   #2c2c2c
```

**UI 스타일**
- 모바일 앱 느낌 (bold serif 헤드라인)
- 카드 그리드 레이아웃
- 악기 태그: pill 모양 (border-radius: 20px)
- 아이콘: 컬러 원형 배경

---

## 레이아웃 규칙

- 헤더·필터바: `position: sticky` **사용 안 함** — 스크롤과 함께 움직임
- 모바일 기준: 375px 너비에서 정상 표시
- 카드 상세보기: 모바일 bottom-sheet 모달

---

## null 필드 표시 규칙

```
null → "미확인" 표시 (회색, 작은 글씨)
절대 빈칸으로 두지 말 것
절대 추측값 표시하지 말 것
```

```html
<!-- 예시 -->
<span class="unknown">미확인</span>
```

---

## 필터 기능 목록

| 필터 | 타입 | 옵션 |
|------|------|------|
| 악기 | multi-select | 전체 악기 목록 |
| 언어조건 | single-select | 없음 / B1 / B2 / C1 / TestDaF / 전공별상이 / 미확인 |
| 언어증명서 제출시점 | single-select | 지원전 / 조건부 / 등록전 / 없음 / 미확인 |
| 1차 전형방식 | single-select | 영상 / 서류 / 영상+서류 / 바로현장 / 미확인 |
| 지원 플랫폼 | single-select | muvac / 자체포털 / 우편병행 |

---

## 데이터 로드 방식

현재: universities.json 데이터를 HTML 파일 안에 직접 JS 변수로 내장
향후: `fetch('./universities.json')` 으로 외부 파일 읽기

수정 시 데이터 로드 방식 바꾸지 말 것 (지은님 승인 필요).

---

## 수정해도 되는 것 vs 안 되는 것

| 수정 가능 | 수정 전 승인 필요 |
|-----------|-----------------|
| 카드 UI 디자인 | 필터 로직 변경 |
| 색상·폰트 조정 | 데이터 로드 방식 변경 |
| 모달 레이아웃 | 새 필터 항목 추가 |
| 텍스트 레이블 | universities.json 연동 방식 |

---

## 테스트 방법

```
german_music_app.html 파일을 브라우저에서 열면 끝.
Mac: 파인더에서 파일 더블클릭 또는 터미널에서 open german_music_app.html
```

Chrome 개발자도구 (F12) → Console 탭에서 에러 확인.
모바일 테스트: Chrome → F12 → 화면 상단 모바일 아이콘 클릭 → 375px 선택.
