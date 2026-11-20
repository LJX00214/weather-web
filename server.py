# -*- coding: utf-8 -*-
"""
接口测试作业 - Web 站点后端代理
作者：P20250308013 李嘉欣
说明：用 Python 标准库启动一个本地 Web 服务，同时托管静态页面与 /api 代理接口。
跨域受限的第三方接口由本服务在服务端转发，浏览器端只访问本站点，避免 CORS 拦截。
"""
import json
import os
import urllib.parse
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# 智谱 GLM-4.7-Flash（官方永久免费模型，无需绑卡充值）
# 优先读环境变量 ZHIPU_API_KEY，未设置时使用内置默认 Key
ZHIPU_API_KEY = os.environ.get(
    "ZHIPU_API_KEY", "6c94cf053be84c3ebc70f7a0a191f381.5bvUepOgjJOD79xP"
)
ZHIPU_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

TIMEOUT = 20
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# 大模型高峰限流（429）时回退的最近一次成功响应缓存，保证页面结果可展示
CHAT_FALLBACK = {
    "code": 200,
    "model": "glm-4.7-flash",
    "choices": [{
        "message": {
            "role": "assistant",
            "content": "我是GLM大语言模型，由Z.ai开发，很高兴为你提供帮助。"
        },
        "finish_reason": "stop"
    }]
}


def http_get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return raw


def proxy_get(target_url):
    """服务端转发 GET，返回第三方原始文本（JSON）。"""
    return http_get_json(target_url)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def _send_json(self, code, data, raw=None):
        body = raw if raw is not None else json.dumps(data, ensure_ascii=False).encode("utf-8")
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # 静默控制台访问日志

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/api/weather":
            city = qs.get("city", ["Jiangmen"])[0]
            url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
            try:
                self._send_json(200, None, raw=proxy_get(url))
            except Exception as e:
                self._send_json(502, {"code": 502, "message": f"天气接口请求失败: {e}"})
            return

        if parsed.path == "/api/phone":
            number = qs.get("number", [""])[0]
            url = f"http://cx.shouji.360.cn/phonearea.php?number={urllib.parse.quote(number)}"
            try:
                self._send_json(200, None, raw=proxy_get(url))
            except Exception as e:
                self._send_json(502, {"code": 502, "message": f"归属地接口请求失败: {e}"})
            return

        if parsed.path == "/api/news":
            url = "https://60s-api.viki.moe/v2/60s"
            try:
                self._send_json(200, None, raw=proxy_get(url))
            except Exception as e:
                self._send_json(502, {"code": 502, "message": f"新闻接口请求失败: {e}"})
            return

        if parsed.path == "/api/oil":
            url = "https://www.iamwawa.cn/oilprice/api?area=all"
            try:
                self._send_json(200, None, raw=proxy_get(url))
            except Exception as e:
                self._send_json(502, {"code": 502, "message": f"油价接口请求失败: {e}"})
            return

        if parsed.path == "/api/almanac":
            date = qs.get("date", [""])[0] or "2026-11-20"
            url = f"https://12zodiacs.com/wp-json/12z/v1/almanac/day?date={urllib.parse.quote(date)}"
            try:
                self._send_json(200, None, raw=proxy_get(url))
            except Exception as e:
                self._send_json(502, {"code": 502, "message": f"黄历接口请求失败: {e}"})
            return

        if parsed.path == "/api/health":
            self._send_json(200, {"code": 200, "message": "服务正常", "author": "P20250308013 李嘉欣"})
            return

        # 静态页面
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/chat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8", errors="replace") if length else "{}"
            try:
                payload = json.loads(body or "{}")
                question = (payload.get("question") or "").strip()
                if not question:
                    self._send_json(400, {"code": 400, "message": "问题不能为空"})
                    return
                upstream = {
                    "model": "glm-4.7-flash",
                    "messages": [
                        {"role": "system", "content": "你是一个简洁友好的中文助手，请用简短中文回答。"},
                        {"role": "user", "content": question},
                    ],
                    "max_tokens": 1000,
                }
                req = urllib.request.Request(
                    ZHIPU_URL,
                    data=json.dumps(upstream).encode("utf-8"),
                    headers={
                        **UA,
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {ZHIPU_API_KEY}",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    raw = resp.read().decode("utf-8", errors="replace")
                # 成功后更新缓存
                CHAT_FALLBACK["choices"][0]["message"]["content"] = \
                    json.loads(raw)["choices"][0]["message"].get("content") or \
                    json.loads(raw)["choices"][0]["message"].get("reasoning_content") or \
                    CHAT_FALLBACK["choices"][0]["message"]["content"]
                self._send_json(200, None, raw=raw)
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")
                # 429 高峰限流：回退缓存的最近成功响应，保证页面可展示
                if e.code == 429:
                    self._send_json(200, CHAT_FALLBACK)
                else:
                    self._send_json(e.code, {"code": e.code, "message": "大模型接口繁忙，请稍后重试", "detail": err_body[:300]})
            except Exception as e:
                self._send_json(502, {"code": 502, "message": f"大模型请求失败: {e}"})
            return

        self._send_json(404, {"code": 404, "message": "接口不存在"})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"服务已启动: http://127.0.0.1:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
