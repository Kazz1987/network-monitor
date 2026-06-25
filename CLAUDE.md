# CLAUDE.md - ネットワーク死活監視ダッシュボード

## プロジェクト概要
ネットワーク機器・サーバーへの定期pingによる死活監視Webアプリ。
ポートフォリオ用途。バックエンド：FastAPI、フロントエンド：React×Vite。

## 技術スタック
- Backend: Python 3.11 / FastAPI / SQLAlchemy / SQLite / ping3 / APScheduler
- Frontend: React 18 / Vite / Recharts / Axios
- Deploy: Render（バックエンド・フロントエンド分離）

## セキュリティルール（絶対に守ること）
- Private IP（10.x, 172.16-31.x, 192.168.x, 127.x, 169.254.x）は必ずブロック
- Pydanticで全入力バリデーション
- SQLAlchemy ORMのみ使用（生SQL禁止）
- CORS許可オリジンは環境変数で管理
- セキュリティヘッダーをmiddlewareで付与
- ping3が使えない場合はsubprocessにフォールバック
- 履歴データは直近24時間分のみ保持

## APIエンドポイント
- GET /api/hosts
- POST /api/hosts
- DELETE /api/hosts/{id}
- GET /api/hosts/{id}/metrics
- POST /api/hosts/{id}/ping
- GET /api/settings
- PUT /api/settings
- GET /health
