/**
 * Cloudflare Worker — Anthropic API 프록시
 * 
 * 브라우저에서 직접 Anthropic API를 호출하면 CORS 차단 + API 키 노출 문제가 있어
 * 이 Worker가 중간에서 요청을 중계합니다.
 * 
 * 환경변수 설정 (Cloudflare Dashboard → Workers → Settings → Variables):
 *   ANTHROPIC_API_KEY = sk-ant-xxxxx (본인 키)
 *   ALLOWED_ORIGIN   = https://your-domain.com (선택, 기본값은 * = 모든 도메인 허용)
 */

export default {
  async fetch(request, env) {
    // CORS 허용 도메인 (환경변수 또는 기본값 *)
    const allowedOrigin = env.ALLOWED_ORIGIN || '*';

    // CORS preflight (OPTIONS) 처리
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': allowedOrigin,
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    // POST만 허용
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': allowedOrigin,
        },
      });
    }

    // API 키 확인
    const apiKey = env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return new Response(JSON.stringify({ error: 'ANTHROPIC_API_KEY not configured' }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': allowedOrigin,
        },
      });
    }

    try {
      // 요청 본문 읽기
      const body = await request.text();

      // Anthropic API로 전달
      const anthropicResponse = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
          'anthropic-version': '2023-06-01',
        },
        body,
      });

      // 스트리밍 응답을 그대로 전달
      const responseHeaders = new Headers({
        'Access-Control-Allow-Origin': allowedOrigin,
        'Content-Type': anthropicResponse.headers.get('Content-Type') || 'text/event-stream',
      });

      return new Response(anthropicResponse.body, {
        status: anthropicResponse.status,
        headers: responseHeaders,
      });

    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': allowedOrigin,
        },
      });
    }
  },
};
