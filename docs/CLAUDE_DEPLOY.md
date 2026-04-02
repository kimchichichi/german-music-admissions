# CLAUDE_DEPLOY.md — GitHub Actions 배포 규칙

> GitHub Actions 설정·배포·디버깅 시 이 파일을 읽어라.
> 마스터 규칙(CLAUDE.md)도 반드시 읽어야 한다.

---

## 자동화 개요

```
매주 월요일 09:00 KST (= UTC 00:00)
GitHub Actions가 자동으로 crawl_pipeline.py 실행
→ 변경 감지 시 이메일 알림 + universities.json 자동 커밋
```

비용: 무료 (GitHub Actions 월 2,000분 무료, 우리 작업은 ~5분/회)

---

## 필수 Secrets 4개

GitHub 저장소 → Settings → Secrets and variables → Actions → "New repository secret"

| Secret 이름 | 값 | 주의 |
|-------------|-----|------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | claude.ai 또는 console.anthropic.com에서 발급 |
| `EMAIL_SENDER` | `보내는이@gmail.com` | Gmail만 지원 |
| `EMAIL_PASSWORD` | `xxxxxxxxxxxx` (16자리) | ⚠️ 일반 비밀번호 아님, 앱 비밀번호 |
| `EMAIL_RECEIVER` | `받는이@email.com` | 어떤 이메일이든 가능 |

### Gmail 앱 비밀번호 발급 방법

1. Google 계정 로그인 → myaccount.google.com
2. 보안 탭 클릭
3. "2단계 인증" 활성화 (안 되어있으면 먼저 활성화)
4. 검색창에 "앱 비밀번호" 검색
5. 앱: "메일" / 기기: "Mac" 선택 → 생성
6. 16자리 코드 복사 (공백 없이 입력)

---

## crawl.yml 구조 설명

```yaml
on:
  schedule:
    - cron: "0 0 * * 1"    # 매주 월요일 00:00 UTC = 09:00 KST
  workflow_dispatch:        # 수동 실행 버튼 활성화
```

**수동 실행 방법:**
GitHub → 저장소 → Actions 탭 → "독일음대-입시정보-자동수집" → "Run workflow" 버튼

`force_extract: true` 체크하면 페이지 변경 없어도 AI 추출 강제 실행.

---

## 첫 배포 순서 (생초보용)

### Step 1. GitHub 저장소 만들기
1. github.com 로그인
2. 우측 상단 `+` → "New repository"
3. Repository name: `german-music-admissions` (영어, 공백 없이)
4. Private 선택 (공개하지 않으려면)
5. "Create repository" 클릭

### Step 2. 파일 올리기
1. 저장소 메인 페이지 → "uploading an existing file" 링크 클릭
2. 아래 파일들을 드래그앤드롭:
   - `universities.json`
   - `crawl_pipeline.py`
   - `requirements.txt`
   - `CLAUDE.md`
   - `german_music_app.html`
3. "Commit changes" 클릭

### Step 3. workflows 폴더 만들기
GitHub에서는 폴더를 직접 만들 수 없어서 파일 이름으로 만든다.
1. 저장소에서 "Add file" → "Create new file"
2. 파일 이름에 `.github/workflows/crawl.yml` 입력
   (슬래시 입력하면 자동으로 폴더 구조 생성됨)
3. `crawl.yml` 내용 붙여넣기
4. "Commit changes" 클릭

### Step 4. Secrets 설정
1. 저장소 → Settings → Secrets and variables → Actions
2. "New repository secret" 4번 반복

### Step 5. 첫 수동 실행
1. Actions 탭 → "독일음대-입시정보-자동수집"
2. "Run workflow" → "Run workflow" 클릭
3. 주황색 점 → 초록색 체크 되면 성공
4. 이메일 수신 확인

---

## 실행 결과 확인 방법

**성공 시:** Actions 탭에서 초록 체크 ✓
**실패 시:** 빨간 X → 클릭 → 어떤 Step에서 실패했는지 확인

**자동 커밋 확인:** 저장소 메인 → 커밋 내역에 "🎵 자동 크롤링: 날짜 업데이트" 생성됨

---

## 자주 발생하는 배포 오류

| 오류 메시지 | 원인 | 해결 |
|-------------|------|------|
| `Secret not found` | Secrets 이름 오타 | 대소문자 정확히 확인 |
| `Authentication failed` | Gmail 앱 비밀번호 오류 | 재발급 후 Secret 업데이트 |
| `ModuleNotFoundError` | requirements.txt 누락 | 파일 업로드 확인 |
| `Permission denied` to push | 저장소 권한 설정 | Settings → Actions → "Read and write permissions" 활성화 |

### "Read and write permissions" 활성화 방법
저장소 → Settings → Actions → General → "Workflow permissions"
→ "Read and write permissions" 선택 → Save

---

## crawl.yml 수정 금지 항목

- `cron` 스케줄 변경 → 지은님 승인 필요
- `secrets.*` 참조 방식 변경 → 절대 금지
- `git push` 단계 삭제 → 절대 금지 (자동 커밋 기능 사라짐)
