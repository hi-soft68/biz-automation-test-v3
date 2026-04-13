# 松井酒造 AI業務エージェント

松井酒造合名会社の業務効率化のために構築した、Claude AIを活用した業務エージェントのプロトタイプです。

## 機能

| エージェント | 主な機能 |
|------------|---------|
| 🏢 全社横断 | 総合相談・AI化業務洗い出し・ロードマップ作成 |
| 📦 受発注・在庫管理 | 在庫分析・受注整理・需要予測・自動化設計 |
| 🍶 醸造・生産管理 | 仕込みスケジュール・品質分析・工程最適化 |
| 💼 営業・顧客対応 | 提案書作成・問い合わせ対応・新規開拓支援 |
| 📈 経営分析・AI戦略 | ROI試算・収益分析・ロードマップ・取締役会資料 |
| 🎤 業務ヒアリング支援 | 課題抽出・自動化ポイント特定・改善提案 |

## デプロイ手順（Streamlit Community Cloud）

### 1. GitHubリポジトリの作成

```bash
# このディレクトリをGitリポジトリとして初期化
git init
git add .
git commit -m "initial commit"

# GitHubに新規リポジトリを作成し、プッシュ
git remote add origin https://github.com/<your-username>/matsui-ai-agent.git
git push -u origin main
```

### 2. Streamlit Community Cloudにデプロイ

1. [share.streamlit.io](https://share.streamlit.io) にアクセス
2. GitHubアカウントでログイン
3. **「New app」** をクリック
4. リポジトリ・ブランチ・`app.py` を選択
5. **「Deploy!」** をクリック

### 3. APIキーをSecretsに設定

Streamlit Cloud の「Settings」→「Secrets」に以下を追加：

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-..."
```

これによりURL上でAPIキーを公開せずに、Claudeの本番応答が利用可能になります。

---

## ローカル実行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 技術スタック

- **フロントエンド**: Streamlit
- **AI**: Anthropic Claude API (claude-opus-4-5)
- **デプロイ**: Streamlit Community Cloud（無料）
- **言語**: Python 3.10+
