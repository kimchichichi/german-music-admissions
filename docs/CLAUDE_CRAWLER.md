# CLAUDE_CRAWLER.md — crawl_pipeline.py 규칙

> crawl_pipeline.py를 수정하거나 디버깅할 때 이 파일을 읽어라.
> 마스터 규칙(CLAUDE.md)도 반드시 읽어야 한다.

---

## 크롤러의 역할 (딱 하나)

```
페이지 변경 감지 → 이메일 알림
```

데이터 확정은 크롤러가 하지 않는다. 지은님이 한다.
AI 추출(`extract_with_claude`)은 참고용일 뿐, universities.json을 자동 확정하지 않는다.

---

## 파이프라인 흐름

```
1. universities.json 읽기 (24개 학교)
        ↓
2. 각 학교 bewerbung_url 크롤링 (BeautifulSoup)
        ↓
3. 이전 해시(page_hashes.json)와 비교
        ↓
4. 변경 감지 시 → AI로 변경 내용 분석 (참고용)
        ↓
5. universities.json 업데이트 + 이메일 발송
```

---

## 환경 변수 4개

| 변수명 | 설명 | 없으면 |
|--------|------|--------|
| `ANTHROPIC_API_KEY` | Claude API 키 | AI 추출 건너뜀 (크롤링은 계속) |
| `EMAIL_SENDER` | 발신 Gmail | 이메일 발송 건너뜀 |
| `EMAIL_PASSWORD` | Gmail 앱 비밀번호 | 이메일 발송 건너뜀 |
| `EMAIL_RECEIVER` | 수신 이메일 | 이메일 발송 건너뜀 |

> 환경변수 없어도 크롤링 자체는 실행된다. 로컬 테스트 시 유용.

---

## 자동 생성 파일들

```
page_hashes.json   ← 변경 감지용 SHA256 해시. 삭제하면 첫 실행으로 인식.
crawl_log.json     ← 실행 결과 로그. 오류 추적용.
snapshots/         ← 크롤링 원본 텍스트. 보호됨, 삭제 금지.
```

---

## merge_ai_to_school() 함수 규칙

AI가 추출한 데이터를 universities.json에 병합할 때:

```python
# 기존 값이 있으면 → 절대 덮어쓰지 않음
# 기존 값이 null이거나 "미확인"일 때만 → AI 값으로 채움
```

즉, 지은님이 직접 입력한 값은 AI가 절대 덮어쓰지 않는다.

---

## 코드 수정 시 주의사항

- 모든 주석은 **한국어**
- `time.sleep(2)` — 서버 부하 방지용, 줄이지 말 것
- `timeout=20` — 느린 학교 사이트 대비, 줄이지 말 것
- `text[:5000]` — AI 토큰 비용 제한, 늘리려면 지은님 승인 필요

---

## 자주 발생하는 오류와 해결법

| 오류 | 원인 | 해결 |
|------|------|------|
| `HTTP 403` | 봇 차단 | HEADERS User-Agent 확인 |
| `Timeout` | 학교 서버 느림 | 정상, 로그에 기록되고 넘어감 |
| `JSON 파싱 실패` | AI 응답 형식 오류 | `re.sub(r"```json|```", "", raw)` 확인 |
| `이메일 발송 실패` | 앱 비밀번호 오류 | Gmail 앱 비밀번호 재생성 |

---

## 로컬 테스트 방법

```bash
# 터미널에서 (Mac 기준)
cd 프로젝트폴더
pip install -r requirements.txt
python crawl_pipeline.py
```

이메일 없이 크롤링만 테스트하려면 환경변수 없이 실행하면 된다.
"이메일 환경변수 없음 → 발송 건너뜀" 메시지가 뜨면 정상.
