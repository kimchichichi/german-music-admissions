"""
╔══════════════════════════════════════════════════════════════════╗
║   독일 음대 입시 정보 자동 수집 파이프라인                              ║
║   crawl_pipeline.py                                              ║
║                                                                  ║
║   실행 방식: GitHub Actions (매주 월요일 09:00 KST 자동 실행)          ║
║   또는 로컬: python crawl_pipeline.py                             ║
║                                                                  ║
║   흐름:                                                           ║
║   1. universities.json 에서 24개 학교 목록 읽기                     ║
║   2. 각 학교 입시 페이지 크롤링 (BeautifulSoup)                      ║
║   3. Claude AI로 구조화된 정보 추출                                  ║
║   4. 이전 데이터와 비교 → 변경사항 감지                               ║
║   5. 결과 저장 + 이메일 알림                                         ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import time
import hashlib
import smtplib
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ══════════════════════════════════════════════════
# 0. 환경 변수 (GitHub Secrets 에서 자동으로 읽어옴)
# ══════════════════════════════════════════════════
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EMAIL_SENDER      = os.environ.get("EMAIL_SENDER", "")
EMAIL_PASSWORD    = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_RECEIVER    = os.environ.get("EMAIL_RECEIVER", "")

# 파일 경로
UNIVERSITIES_FILE  = "universities.json"       # 학교 목록 + 기존 데이터
OUTPUT_FILE        = "universities.json"       # 덮어쓰기 (변경 시)
HASH_FILE          = "page_hashes.json"        # 페이지 변경 감지용 해시
LOG_FILE           = "crawl_log.json"          # 실행 로그

# 요청 헤더 (봇 차단 우회)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ══════════════════════════════════════════════════
# 1. 유틸리티 함수
# ══════════════════════════════════════════════════

def log(msg: str, level: str = "INFO"):
    """타임스탬프와 함께 로그 출력"""
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✅", "WARN": "⚠️", "ERR": "❌", "CHANGE": "⚡"}
    print(f"[{ts}] {prefix.get(level, '•')} {msg}")


def load_json(path: str) -> dict | list:
    """JSON 파일 로드. 없으면 빈 dict 반환."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(data: dict | list, path: str):
    """JSON 파일 저장 (들여쓰기 포함, 한글 보존)"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log(f"저장 완료: {path}", "OK")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ══════════════════════════════════════════════════
# 2. 크롤링 — 페이지 본문 텍스트 추출
# ══════════════════════════════════════════════════

def fetch_text(url: str, timeout: int = 20) -> str | None:
    """
    URL에 접속하여 본문 텍스트 추출.
    네비게이션·푸터·스크립트 제거 후 <main> 또는 body 텍스트 반환.
    실패 시 None.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # 노이즈 제거
        for tag in soup(["nav", "header", "footer", "script",
                          "style", "noscript", "aside"]):
            tag.decompose()

        # 본문 우선순위 탐색
        main = (
            soup.find("main")
            or soup.find(id="page-content")
            or soup.find(id="content")
            or soup.find(class_="content-wrapper")
            or soup.find("article")
            or soup.find("body")
        )

        if not main:
            return None

        text = main.get_text(separator="\n", strip=True)
        return text[:5000] if len(text) > 5000 else text

    except requests.exceptions.Timeout:
        log(f"타임아웃: {url}", "WARN")
        return None
    except requests.exceptions.HTTPError as e:
        log(f"HTTP 오류 {e.response.status_code}: {url}", "WARN")
        return None
    except Exception as e:
        log(f"접속 실패: {url} → {e}", "ERR")
        return None


def find_pdf_links(url: str) -> list[str]:
    """
    페이지에서 PDF 링크 추출.
    입시요강·Repertoire·Zulassung 관련 PDF 필터링.
    """
    keywords = [
        "repertoire", "aufnahme", "zulassung", "bewerbung",
        "anforderungen", "prüfung", "studienordnung"
    ]
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "lxml")
        pdfs = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf"):
                # 절대 URL 변환
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    from urllib.parse import urlparse
                    base = urlparse(url)
                    full_url = f"{base.scheme}://{base.netloc}{href}"
                else:
                    full_url = url.rstrip("/") + "/" + href

                # 관련 키워드 필터
                link_text = (a.get_text() + href).lower()
                if any(k in link_text for k in keywords):
                    pdfs.append(full_url)
        return list(set(pdfs))[:5]  # 최대 5개
    except Exception:
        return []


# ══════════════════════════════════════════════════
# 3. Claude AI — 텍스트에서 입시 정보 추출
# ══════════════════════════════════════════════════

def extract_with_claude(
    raw_text: str,
    school_name: str,
    instrument: str,
    existing_data: dict
) -> dict:
    """
    Claude API에 크롤링된 텍스트를 보내서
    구조화된 입시 정보 JSON으로 추출.
    기존 데이터를 함께 보내서 변경된 항목만 업데이트.
    """
    if not ANTHROPIC_API_KEY:
        log("ANTHROPIC_API_KEY 없음 → AI 추출 건너뜀", "WARN")
        return {}

    # 기존 데이터를 컨텍스트로 제공
    existing_str = json.dumps(existing_data, ensure_ascii=False, indent=2) if existing_data else "없음"

    prompt = f"""
너는 독일 음대 입시 전문가다. 아래 텍스트를 분석하여 {school_name}의 {instrument} 전공 입시 정보를 추출해라.

기존 데이터 (변경 여부 비교용):
{existing_str}

크롤링된 텍스트:
{raw_text}

다음 JSON 형식으로만 답해라. 확인된 정보만 채우고, 텍스트에 없으면 반드시 null로 남겨라. 절대 추측하지 마라.

{{
  "학위": ["Bachelor", "Master", "Konzertexamen"] 중 해당하는 것들 또는 null,
  "지원시작일_겨울": "예: 2월 15일" 또는 null,
  "지원마감일_겨울": "예: 4월 8일" 또는 null,
  "지원시작일_여름": "예: 10월 1일" 또는 null,
  "지원마감일_여름": "예: 11월 8일" 또는 null,
  "마감일_예외": "예: Master 성악은 12월 31일" 또는 null,
  "실기시험일": "예: 6월 8~13일" 또는 null,
  "입학가능학기": "겨울만" 또는 "겨울·여름" 또는 null,
  "언어조건_레벨": "없음" 또는 "A2" 또는 "B1" 또는 "B2" 또는 "C1" 또는 "TestDaF TDN3" 또는 "DSH-1" 또는 null,
  "언어조건_상세": "구체적 설명" 또는 null,
  "언어조건_제출시점": "지원전" 또는 "조건부" 또는 "등록전" 또는 "없음" 또는 null,
  "언어조건_제출시점_설명": "구체적 설명" 또는 null,
  "지원방식": "온라인" 또는 "우편" 또는 "온라인+우편" 또는 null,
  "지원플랫폼": "muvac" 또는 "BEMUS" 또는 "자체포털" 또는 구체적 URL 또는 null,
  "지원비": "예: 60 EUR" 또는 null,
  "지원비_환불": true 또는 false 또는 null,
  "1차전형방식": "영상" 또는 "서류" 또는 "영상+서류" 또는 "없음(바로현장)" 또는 null,
  "1차전형_상세": "구체적 설명" 또는 null,
  "2차실기_필수과목": ["청음", "화성법", "피아노부전공"] 해당하는 것들 또는 null,
  "실기곡_요구사항": "구체적 레파토어 요구사항" 또는 null,
  "제출서류": ["신분증", "영상링크", "자기소개서"] 등 또는 null,
  "비고": "기타 중요 정보" 또는 null,
  "데이터_신뢰도": "확인됨" 또는 "부분확인" 또는 "미확인"
}}

JSON만 출력. 설명 없이.
"""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=40,
        )
        resp.raise_for_status()
        raw = resp.json()["content"][0]["text"].strip()

        # JSON 펜스 제거
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)

    except json.JSONDecodeError as e:
        log(f"AI 응답 JSON 파싱 실패: {e}", "ERR")
        return {}
    except Exception as e:
        log(f"Claude API 오류: {e}", "ERR")
        return {}


# ══════════════════════════════════════════════════
# 4. 변경 감지
# ══════════════════════════════════════════════════

def detect_changes(school_id: int, url: str, current_text: str,
                   prev_hashes: dict) -> tuple[bool, str]:
    """
    이전 해시와 현재 해시 비교.
    변경됐으면 (True, 현재해시) 반환.
    """
    key = f"{school_id}_{url}"
    current_hash = sha256(current_text)
    prev_hash = prev_hashes.get(key, "")

    if not prev_hash:
        return False, current_hash  # 최초 등록

    changed = prev_hash != current_hash
    return changed, current_hash


# ══════════════════════════════════════════════════
# 5. 이메일 알림
# ══════════════════════════════════════════════════

def send_email(changes: list[dict], summary: dict):
    """변경 감지된 학교 목록과 크롤링 요약을 이메일로 발송"""
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        log("이메일 환경변수 없음 → 발송 건너뜀 (로컬 테스트)", "WARN")
        return

    today = datetime.now().strftime("%Y년 %m월 %d일")

    rows = "".join(f"""
    <tr>
      <td style="padding:8px;border:1px solid #ddd">{c['name']}</td>
      <td style="padding:8px;border:1px solid #ddd">{c['city']}</td>
      <td style="padding:8px;border:1px solid #ddd">{c.get('changed_fields','변경감지')}</td>
      <td style="padding:8px;border:1px solid #ddd">
        <a href="{c['url']}">{c['url'][:50]}...</a>
      </td>
    </tr>""" for c in changes)

    html = f"""
    <html><body style="font-family:sans-serif;color:#333;max-width:900px">
      <h2 style="color:#8b6914">🎵 독일 음대 입시 크롤링 완료</h2>
      <p><b>실행일:</b> {today}</p>
      <table style="border-collapse:collapse;margin-bottom:20px">
        <tr><td style="padding:4px 12px 4px 0"><b>총 학교 수</b></td><td>{summary['total']}</td></tr>
        <tr><td style="padding:4px 12px 4px 0"><b>크롤링 성공</b></td><td>{summary['success']}</td></tr>
        <tr><td style="padding:4px 12px 4px 0"><b>변경 감지</b></td><td>{summary['changed']}</td></tr>
        <tr><td style="padding:4px 12px 4px 0"><b>실패</b></td><td>{summary['failed']}</td></tr>
      </table>
      {"<h3>⚡ 변경 감지 학교</h3><table style='border-collapse:collapse;width:100%'><tr style='background:#f5f0e8'><th style='padding:8px;border:1px solid #ddd'>학교</th><th style='padding:8px;border:1px solid #ddd'>도시</th><th style='padding:8px;border:1px solid #ddd'>변경 항목</th><th style='padding:8px;border:1px solid #ddd'>URL</th></tr>" + rows + "</table>" if changes else "<p>변경된 학교 없음.</p>"}
      <hr>
      <p style="font-size:11px;color:#999">독일 음대 입시 자동 모니터링 시스템 — GitHub Actions</p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[독일음대] 크롤링 완료 — 변경 {summary['changed']}건 ({today})"
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECEIVER
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as srv:
            srv.login(EMAIL_SENDER, EMAIL_PASSWORD)
            srv.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        log(f"이메일 발송 → {EMAIL_RECEIVER}", "OK")
    except Exception as e:
        log(f"이메일 발송 실패: {e}", "ERR")


# ══════════════════════════════════════════════════
# 6. 메인 파이프라인
# ══════════════════════════════════════════════════

def run():
    start_time = datetime.now()
    log("=" * 60)
    log("독일 음대 입시 크롤링 파이프라인 시작")
    log(f"실행 시각: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)

    # ── 데이터 로드
    data = load_json(UNIVERSITIES_FILE)
    if not data or "universities" not in data:
        log("universities.json 파일 없음 또는 형식 오류!", "ERR")
        return

    universities = data["universities"]
    prev_hashes  = load_json(HASH_FILE)
    curr_hashes  = {}

    changed_schools = []
    results = {
        "total": len(universities),
        "success": 0,
        "changed": 0,
        "failed": 0,
        "skipped": 0,
    }

    # ── 각 학교 순회
    for i, school in enumerate(universities, 1):
        sid   = school["id"]
        name  = school["name"]
        city  = school["city"]
        burl  = school["bewerbung_url"]

        log(f"\n[{i:02d}/{len(universities)}] {name} ({city})")
        log(f"  URL: {burl}")

        # 1단계: 페이지 크롤링
        text = fetch_text(burl)
        if not text:
            log("  크롤링 실패 — 건너뜀", "WARN")
            results["failed"] += 1
            school["crawl_status"] = "failed"
            school["last_crawled"] = datetime.now().isoformat()
            time.sleep(2)
            continue

        log(f"  본문 {len(text)}자 추출", "OK")
        results["success"] += 1

        # 2단계: 변경 감지
        changed, curr_hash = detect_changes(sid, burl, text, prev_hashes)
        curr_hashes[f"{sid}_{burl}"] = curr_hash

        if changed:
            log(f"  페이지 변경 감지!", "CHANGE")
            results["changed"] += 1
        else:
            log("  변경 없음")

        # 3단계: PDF 링크 수집
        pdfs = find_pdf_links(burl)
        if pdfs:
            log(f"  PDF {len(pdfs)}개 발견: {pdfs[0][:60]}...")
            school["pdf_links"] = pdfs

        # 4단계: AI로 정보 추출 (변경됐거나 기존 AI 데이터 없을 때)
        has_ai_data = bool(school.get("ai_extracted_data"))
        if changed or not has_ai_data:
            log("  AI 정보 추출 중...")
            # 첫 번째 악기로 대표 추출 (악기별 상세는 별도 파이프라인)
            instrument = school.get("instruments", ["전공"])[0] if school.get("instruments") else "전공"
            existing   = school.get("ai_extracted_data", {})
            ai_data    = extract_with_claude(text, name, instrument, existing)

            if ai_data:
                school["ai_extracted_data"] = ai_data
                school["ai_extracted_at"]   = datetime.now().isoformat()
                log(f"  AI 추출 완료 (신뢰도: {ai_data.get('데이터_신뢰도','?')})", "OK")

                # AI 데이터를 최상위 필드로 병합 (기존 수동 입력값 우선)
                merge_ai_to_school(school, ai_data)

                if changed:
                    changed_schools.append({
                        "name": name,
                        "city": city,
                        "url":  burl,
                        "changed_fields": "페이지 변경 감지 → AI 재추출 완료",
                    })
        else:
            log("  변경 없음 + 기존 AI 데이터 있음 → 건너뜀")
            results["skipped"] += 1

        school["crawl_status"] = "success"
        school["last_crawled"] = datetime.now().isoformat()
        school["page_changed"] = changed

        # 요청 간격 (서버 부하 방지)
        time.sleep(2)

    # ── 결과 저장
    data["last_updated"]  = datetime.now().strftime("%Y-%m-%d")
    data["last_crawled"]  = datetime.now().isoformat()
    data["universities"]  = universities
    save_json(data, OUTPUT_FILE)

    # 해시 저장
    save_json(curr_hashes, HASH_FILE)

    # 실행 로그 저장
    log_data = {
        "run_at":  start_time.isoformat(),
        "results": results,
        "changed": [c["name"] for c in changed_schools],
        "duration_sec": (datetime.now() - start_time).seconds,
    }
    save_json(log_data, LOG_FILE)

    # ── 요약 출력
    log("\n" + "=" * 60)
    log(f"크롤링 완료!")
    log(f"  총: {results['total']} | 성공: {results['success']} | 변경: {results['changed']} | 실패: {results['failed']}")
    log("=" * 60)

    # ── 이메일 발송
    if changed_schools or results["failed"] > 0:
        send_email(changed_schools, results)
    else:
        log("변경 없음 → 이메일 발송 건너뜀")


def merge_ai_to_school(school: dict, ai: dict):
    """
    AI가 추출한 데이터를 학교 데이터의 최상위 필드로 병합.
    기존 수동 입력값(null 아닌 값)은 덮어쓰지 않음.
    """
    field_map = {
        "학위":                "degrees",
        "지원시작일_겨울":       "deadline_winter_start",
        "지원마감일_겨울":       "deadline_winter",
        "지원시작일_여름":       "deadline_summer_start",
        "지원마감일_여름":       "deadline_summer",
        "마감일_예외":           "deadline_note",
        "실기시험일":           "audition_dates",
        "입학가능학기":          "semester",
        "언어조건_레벨":         "lang_level",
        "언어조건_상세":         "lang_text",
        "언어조건_제출시점":     "lang_timing",
        "언어조건_제출시점_설명": "lang_timing_text",
        "지원방식":              "method_text",
        "지원플랫폼":            "portal",
        "지원비":               "fee",
        "1차전형방식":           "round1_type",
        "1차전형_상세":          "round1_text",
        "2차실기_필수과목":      "round2_required",
        "실기곡_요구사항":       "repertoire",
        "제출서류":              "docs",
        "비고":                 "note",
        "데이터_신뢰도":         "data_status",
    }
    for ai_key, school_key in field_map.items():
        ai_val = ai.get(ai_key)
        if ai_val is None:
            continue
        # 기존 값이 없거나 "미확인"인 경우에만 AI 값으로 업데이트
        existing = school.get(school_key)
        if not existing or existing in ["미확인", "unknown", "", []]:
            school[school_key] = ai_val


if __name__ == "__main__":
    run()
