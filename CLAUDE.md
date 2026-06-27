# CLAUDE.md - ネットワーク死活監視ダッシュボード

## プロジェクト概要
ネットワーク機器・サーバーへの定期pingによる死活監視Webアプリ。
ポートフォリオ用途。バックエンド：FastAPI、フロントエンド：React×Vite。

## 技術スタック
- Backend: Python 3.11 / FastAPI / SQLAlchemy / SQLite / ping3 / APScheduler / httpx
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
- SLACK_WEBHOOK_URLは環境変数で管理（コードにハードコード禁止）

## APIエンドポイント
- GET /api/hosts
- POST /api/hosts
- DELETE /api/hosts/{id}
- GET /api/hosts/{id}/metrics
- POST /api/hosts/{id}/ping
- GET /api/hosts/{id}/ports
- POST /api/hosts/{id}/ports
- DELETE /api/hosts/{id}/ports/{port_id}
- GET /api/hosts/{id}/ssl
- GET /api/settings
- PUT /api/settings
- GET /health

## 主要サービス・モジュール

### backend/app/services/
- `port_checker.py` — TCP socket接続でポート開閉を確認（timeout=3秒）
- `ssl_checker.py` — SSL証明書の有効期限を取得（ホスト名のみ対応、IPは返却なし）
- `slack_notifier.py` — Slack Incoming Webhook通知。クールダウン管理（ホストダウン・ポートダウン：1時間、SSL：24時間）

### backend/app/routers/
- `ports.py` — PortMonitorモデルのCRUD（GET/POST/DELETE）
- `ssl.py` — SslMonitorレコードの参照（GET）

### frontend/src/components/
- `PortMonitorPanel.jsx` — ポート監視パネル（追加・削除・状態表示）
- `SslPanel.jsx` — SSL証明書の残り日数・期限表示
- `WelcomeModal.jsx` — 初回アクセス時のポートフォリオ説明モーダル

### frontend/src/hooks/
- `usePorts.js` — ポートAPI呼び出しカスタムフック
- `useSsl.js` — SSL API呼び出しカスタムフック

## スケジューラ（APScheduler）
- ping監視：設定間隔ごとに実行（デフォルト60秒）
- ポート監視：ping監視と同じジョブ内で実行
- SSL証明書チェック：毎日09:00 UTC に全ホストを自動チェック
