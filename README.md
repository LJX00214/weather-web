# 生活助手平台（接口测试作业）

- 学号：P20250308013　姓名：李嘉欣
- 功能：天气查询、手机归属地、今日油价、黄历查询、当日新闻、AI 大模型问答（共 6 项 API）

## 一、本地运行

1. 已安装 Python 3.10+（无需第三方依赖）。
2. 在本目录打开命令行，执行：

```
python server.py
```

3. 浏览器访问：`http://127.0.0.1:8000/`

## 二、目录结构

```
weather-web/
├── server.py        # 后端服务 + /api 代理接口（Python 标准库）
├── static/
│   ├── index.html    # 主页面
│   └── preview.html  # 结果预览页（截图用）
├── requirements.txt
├── Procfile
└── README.md
```

## 三、接口清单（本站点代理）

| 功能 | 方式 | 本站点地址 |
| --- | --- | --- |
| 天气查询 | GET | /api/weather?city=江门 |
| 手机归属地 | GET | /api/phone?number=17676860190 |
| 今日油价 | GET | /api/oil |
| 黄历查询 | GET | /api/almanac?date=2026-11-20 |
| 当日新闻 | GET | /api/news |
| AI 问答 | POST | /api/chat（Body: {"question":"..."}） |

## 四、部署到免费云平台（生成在线地址）

本项目含后端代理，不能部署到纯静态托管（GitHub Pages 等），需选择支持 Python 后端运行的平台，例如 Render / Railway /  PythonAnywhere。

### Render（免费 Free 实例）
1. 将本目录代码推送到一个 GitHub 仓库。
2. 登录 https://render.com ，New → Web Service → 连接该仓库。
3. 运行环境选 Python，Build Command 留空，Start Command 填 `python server.py`。
4. 环境变量可选填 `ZHIPU_API_KEY`（不填则用内置默认 Key）。
5. 部署完成后获得 `https://<服务名>.onrender.com` 在线地址，发给老师即可。

> 免费实例空闲一段时间会休眠，首次打开需等待数十秒唤醒，属正常现象。
