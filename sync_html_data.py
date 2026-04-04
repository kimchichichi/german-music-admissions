#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
universities.json을 german_music_v4.html의 SCHOOLS 배열로 동기화하는 스크립트.

용도:
  python3 sync_html_data.py

역할:
  1. universities.json 읽기
  2. JSON 필드를 HTML 형식으로 변환
  3. german_music_v4.html의 SCHOOLS 배열 교체
"""

import json
import re
from pathlib import Path


def map_data_status(data_status):
    """
    JSON의 data_status를 HTML의 status 값으로 변환.

    JSON 값         → HTML 값
    '확인됨'       → 'verified'
    '부분확인'     → 'partial'
    None/'미확인'  → 'unverified'
    """
    if data_status == '확인됨':
        return 'verified'
    elif data_status == '부분확인':
        return 'partial'
    else:
        return 'unverified'


def transform_school(school_json):
    """
    JSON 학교 데이터를 HTML SCHOOLS 배열 형식으로 변환.

    null 값은 '미확인'으로 변환하여 HTML에서 제대로 표시되도록 함.
    """
    def null_to_unconfirmed(value):
        """null 값을 '미확인'으로 변환."""
        return '미확인' if value is None else value

    return {
        'id': school_json.get('id'),
        'name': school_json.get('name'),
        'name_de': school_json.get('name_de'),
        'city': school_json.get('city'),
        'status': map_data_status(school_json.get('data_status')),
        'url': school_json.get('bewerbung_url'),
        'degrees': school_json.get('degrees', []),
        'instruments': school_json.get('instruments') or ['미확인 — 공식 홈페이지 참조'],
        'deadline_w': null_to_unconfirmed(school_json.get('deadline_winter')),
        'deadline_s': null_to_unconfirmed(school_json.get('deadline_summer')),
        'lang_level': null_to_unconfirmed(school_json.get('lang_level')),
        'lang_text': null_to_unconfirmed(school_json.get('lang_text')),
        'lang_timing': null_to_unconfirmed(school_json.get('lang_timing')),
        'lang_timing_text': null_to_unconfirmed(school_json.get('lang_timing_text')),
        'round1_type': null_to_unconfirmed(school_json.get('round1_type')),
        'round1_text': null_to_unconfirmed(school_json.get('round1_text')),
        'portal': null_to_unconfirmed(school_json.get('portal')),
        'portal_type': null_to_unconfirmed(school_json.get('portal_type')),
        'method_text': null_to_unconfirmed(school_json.get('method_text')),
        'fee': null_to_unconfirmed(school_json.get('fee')),
        'note': school_json.get('note'),
    }


def serialize_js_value(value):
    """
    Python 값을 JavaScript 리터럴로 변환.
    - 문자열은 작은따옴표로 감싸기
    - null → null
    - 배열/딕셔너리는 JavaScript 형식으로
    """
    if value is None:
        return 'null'
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    elif isinstance(value, str):
        # 문자열 내 따옴표와 개행 이스케이프
        escaped = value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        return f"'{escaped}'"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        items = [serialize_js_value(item) for item in value]
        return '[' + ','.join(items) + ']'
    elif isinstance(value, dict):
        items = []
        for k, v in value.items():
            items.append(f"{k}:{serialize_js_value(v)}")
        return '{' + ','.join(items) + '}'
    else:
        return f"'{str(value)}'"


def generate_schools_array_js(schools):
    """
    학교 목록을 JavaScript SCHOOLS 배열 형식으로 생성.

    반환 형식:
    const SCHOOLS = [
      { id:1, name:'...', ... },
      { id:2, name:'...', ... },
      ...
    ];
    """
    js_code = "const SCHOOLS = [\n"

    for i, school in enumerate(schools):
        js_code += "  {\n"
        for key, value in school.items():
            js_code += f"    {key}:{serialize_js_value(value)},\n"
        js_code += "  },\n"

    js_code += "];"
    return js_code


def main():
    """메인 동기화 함수."""
    # 파일 경로
    json_path = Path('universities.json')
    html_path = Path('german_music_v4.html')

    # 1. universities.json 읽기
    print("📖 JSON 파일 읽기...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    universities = data.get('universities', [])
    print(f"✓ {len(universities)}개 학교 로드됨")

    # 2. 각 학교를 HTML 형식으로 변환
    print("🔄 데이터 형식 변환 중...")
    schools_transformed = [transform_school(s) for s in universities]
    print(f"✓ {len(schools_transformed)}개 학교 변환 완료")

    # 3. JavaScript 코드 생성
    print("📝 JavaScript 코드 생성 중...")
    js_code = generate_schools_array_js(schools_transformed)

    # 4. HTML 파일에서 기존 SCHOOLS 배열 찾아 교체
    print("🔍 HTML 파일 업데이트 중...")
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # SCHOOLS 배열의 시작과 끝 찾기
    # 패턴: const SCHOOLS = [ ... ];
    pattern = r'const SCHOOLS = \[[\s\S]*?\];'

    if not re.search(pattern, html_content):
        print("❌ 오류: HTML에서 SCHOOLS 배열을 찾을 수 없습니다.")
        return False

    # 교체
    new_html_content = re.sub(pattern, js_code, html_content)

    # 5. HTML 파일에 쓰기
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html_content)

    print(f"✓ HTML 파일 업데이트 완료: {html_path}")
    print("\n✅ 동기화 성공!")
    print(f"   - 학교 수: {len(schools_transformed)}")
    print(f"   - verified (확인됨): {sum(1 for s in schools_transformed if s['status'] == 'verified')}")
    print(f"   - partial (부분확인): {sum(1 for s in schools_transformed if s['status'] == 'partial')}")
    print(f"   - unverified (미확인): {sum(1 for s in schools_transformed if s['status'] == 'unverified')}")

    return True


if __name__ == '__main__':
    main()
