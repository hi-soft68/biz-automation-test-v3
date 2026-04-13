from anthropic import Anthropic

import streamlit as st

# ────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ────────────────────────────────────────────────────
st.set_page_config(
    page_title="松井酒造 AI業務エージェント",
    page_icon="🍶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────────────────────────────
# GLOBAL CSS
# ────────────────────────────────────────────────────
st.markdown("""
<style>
/* --- Base --- */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0d0b !important;
    color: #e8e0cc !important;
}
[data-testid="stSidebar"] {
    background-color: #111110 !important;
    border-right: 1px solid #2a2a20 !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbarActions"] {
    display: none !important;
}

#MainMenu {
    display: none !important;
}

footer {
    display: none !important;
}

/* --- Typography --- */
h1, h2, h3 { color: #c8a84b !important; }

/* --- Input / chat input --- */
[data-testid="stChatInput"] textarea {
    background-color: #1a1a14 !important;
    color: #e8e0cc !important;
    border: 1px solid #2e2e24 !important;
    border-radius: 8px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #7a6530 !important;
    box-shadow: 0 0 0 1px #7a6530 !important;
}

/* --- Buttons --- */
.stButton > button {
    background-color: #1a1a14 !important;
    color: #c8a84b !important;
    border: 1px solid #2e2e24 !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    transition: all 0.18s !important;
    text-align: left !important;
    width: 100% !important;
}
.stButton > button:hover {
    background-color: rgba(200,168,75,0.12) !important;
    border-color: #7a6530 !important;
    color: #d9b85a !important;
}

/* --- Radio --- */
[data-testid="stRadio"] label { color: #a09880 !important; font-size: 13px !important; }
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p { color: #a09880 !important; }

/* --- Chat messages --- */
[data-testid="stChatMessage"] {
    background-color: #141410 !important;
    border: 1px solid #222218 !important;
    border-radius: 10px !important;
    margin-bottom: 6px !important;
}

/* --- Expander --- */
[data-testid="stExpander"] {
    background-color: #111110 !important;
    border: 1px solid #222218 !important;
    border-radius: 8px !important;
}

/* --- Text inputs --- */
[data-testid="stTextInput"] input {
    background-color: #1a1a14 !important;
    color: #e8e0cc !important;
    border: 1px solid #2e2e24 !important;
}

/* --- Divider --- */
hr { border-color: #2a2a20 !important; }

/* --- Selectbox --- */
[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #1a1a14 !important;
    border-color: #2e2e24 !important;
}

/* --- Scroll area --- */
section.main > div { padding-top: 12px !important; }

/* --- Gold badge --- */
.gold-badge {
    display: inline-block;
    padding: 2px 10px;
    border: 1px solid #7a6530;
    border-radius: 12px;
    font-size: 11px;
    color: #c8a84b;
    background: rgba(200,168,75,0.08);
    letter-spacing: 0.08em;
}

/* --- Dept card --- */
.dept-card {
    background: #141410;
    border: 1px solid #2e2e24;
    border-left: 3px solid #c8a84b;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 12px;
    font-size: 13px;
    color: #a09880;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────
# SYSTEM PROMPTS PER DEPARTMENT
# ────────────────────────────────────────────────────
BASE_CONTEXT = """
【会社情報】
社名：松井酒造合名会社
事業：日本酒の製造・販売（純米大吟醸・純米吟醸・本醸造・にごり酒 等）
規模：中規模蔵元、全国の酒販店・百貨店・飲食店等に卸売
課題：業務の属人化・紙ベースの管理・データ活用不足

【共通方針】
- 日本酒業界の専門知識を活かし、実務レベルの具体的な回答をする
- 数値・日程・優先順位を明示する
- 箇条書き・表・ロードマップ形式を積極的に活用する
- 「現時点でわからないこと」は正直に伝え、必要な情報を聞き返す
- すべて日本語で回答する
"""

DEPARTMENTS = {
    "🏢 全社横断 / 総合相談": {
        "desc": "どの部門の質問にも対応する総合AIエージェント。まず何でも相談してください。",
        "system": BASE_CONTEXT + """
【あなたの役割】全社横断のAIビジネスエージェント。
受発注・醸造・営業・経営・人事・IT・教育など、あらゆる業務領域の相談を受け付け、
適切な解決策・自動化プランを提示する。
課題が明確でない場合は、的確な質問で課題を引き出す。
""",
        "presets": [
            ("📋 AI化できる業務を洗い出す", "現在の主な業務フローを教えていただければ、AIで自動化・効率化できる箇所を優先度付きで洗い出します。まず各部門で最も時間がかかっている作業はどれですか？"),
            ("🗺️ AI導入ロードマップを作成", "御社のAI導入ロードマップを作成してください。短期（1〜3ヶ月）・中期（3〜6ヶ月）・長期（6〜12ヶ月）の3フェーズで、優先度・期待効果・必要コストを含めてください。"),
            ("💰 AI投資ROIを試算", "AIエージェント導入による投資対効果（ROI）を試算してください。主な業務カテゴリ別の削減工数と、年間コスト削減額の目安を出してください。"),
            ("📊 部門別課題ヒアリングを開始", "各部門担当者へのヒアリングを始めます。課題を引き出すための質問を、部門ごとに体系的に行ってください。まず受発注部門から始めましょう。"),
        ]
    },
    "📦 受発注・在庫管理": {
        "desc": "受注処理・在庫確認・出荷調整・仕入れ管理を自動化・効率化するエージェント。",
        "system": BASE_CONTEXT + """
【あなたの役割】受発注・在庫管理専門AIエージェント。
以下の業務をサポートする：
- 受注データの整理・優先度付け・異常検知
- 在庫の過不足分析と補充推奨
- 出荷スケジュール最適化
- 仕入れ（原材料・副資材）の発注タイミング提案
- 季節需要予測（年末ギフト・花見・お中元等）
実際の運用ではERPや在庫DBと連携し、リアルタイムデータで回答する。
""",
        "presets": [
            ("📊 在庫・出荷状況レポート作成", "今月の在庫状況を確認して、出荷予定と照らし合わせて不足しそうな銘柄を教えてください。対応優先度も付けてください。"),
            ("⚠️ 在庫アラート設計", "在庫管理のアラートルールを設計してください。どの指標で、どのタイミングで誰に通知すべきか、フロー図も含めて提案してください。"),
            ("📈 年末需要予測と発注計画", "年末商戦（11〜12月）に向けた銘柄別需要予測と、それに基づく原材料の発注計画を立ててください。"),
            ("🔄 受発注の自動化フロー設計", "現在の受注〜在庫確認〜出荷指示の業務フローをAIで自動化するとしたら、どのような設計が最適ですか？"),
        ]
    },
    "🍶 醸造・生産管理": {
        "desc": "仕込みスケジュール・醸造データ分析・品質管理・工程最適化を支援するエージェント。",
        "system": BASE_CONTEXT + """
【あなたの役割】醸造・生産管理専門AIエージェント。日本酒醸造の深い専門知識を持つ。
以下の業務をサポートする：
- 年間・月次の仕込みスケジュール立案（三段仕込み・酒母・麹管理含む）
- 醸造ログ（日本酒度・酸度・アルコール・温度）の分析と異常検知
- 品質トラブルの原因特定と対処法の提案
- 原材料（精米・麹米・仕込み水）の品質管理
- 省エネ・コスト最適化の提案
用語：精米歩合・山廃・生酛・麹・酒母・醪・上槽・火入れ・瓶燗等を適切に使用。
""",
        "presets": [
            ("📅 仕込みスケジュール立案", "今期の純米大吟醸の仕込みスケジュールを立案してください。洗米・浸漬から麹づくり・酒母・三段仕込み・上槽・火入れまでの全工程を含めてください。"),
            ("🔬 醸造データ異常分析", "醪の日本酒度が想定より+3高く推移しています。考えられる原因と対処法を教えてください。"),
            ("♻️ 醸造工程の効率化提案", "醸造工程においてAI・センサー・自動化で省力化できる箇所を洗い出し、優先度付きで提案してください。"),
            ("📋 品質管理チェックリスト作成", "醸造工程の各ステップで実施すべき品質チェック項目を、担当者・タイミング・基準値付きで一覧化してください。"),
        ]
    },
    "💼 営業・顧客対応": {
        "desc": "提案書作成・商品案内・顧客フォロー・新規開拓を支援するエージェント。",
        "system": BASE_CONTEXT + """
【あなたの役割】営業・顧客対応専門AIエージェント。
以下の業務をサポートする：
- 取引先（百貨店・酒販店・飲食店・EC）向け提案書の自動生成
- 商品の特徴・ペアリング・ストーリーを訴求する商品説明文の作成
- 顧客からの問い合わせ・クレーム対応メールのドラフト
- 新規開拓先のリストアップと営業アプローチ策定
- ギフトセット・季節商品の企画提案
文体は丁寧かつ温かみがあり、日本酒文化への敬意を込めた表現を使う。
""",
        "presets": [
            ("📄 百貨店向けギフト提案書作成", "大手百貨店の担当者向けに、年末ギフトセットの提案書ドラフトを作成してください。商品構成・価格帯・納期・特徴・訴求ポイントを含めてください。"),
            ("✉️ 問い合わせ対応メール作成", "酒販店から「辛口で食中酒に合う純米酒を5本紹介してほしい」という問い合わせが来ました。丁寧な回答メールを作成してください。"),
            ("🎯 新規飲食店開拓アプローチ", "日本酒に力を入れている高級和食レストランへの新規営業アプローチを提案してください。初回コンタクトから成約までのステップも含めてください。"),
            ("📢 SNS・EC用商品説明文の作成", "純米大吟醸の魅力をECサイトとInstagramで訴求する商品説明文を、それぞれのトーンに合わせて作成してください。"),
        ]
    },
    "📈 経営分析・AI戦略": {
        "desc": "売上分析・コスト最適化・AI導入ロードマップ・取締役会向け資料作成を支援するエージェント。",
        "system": BASE_CONTEXT + """
【あなたの役割】経営分析・AI戦略専門エージェント。経営層の意思決定を支援する。
以下の業務をサポートする：
- 売上・利益・コストのチャネル別・銘柄別分析
- AI・DX導入の投資対効果（ROI）試算
- 競合分析と差別化戦略の立案
- 取締役会・幹部会議向けレポート・資料の骨子作成
- 中期経営計画・AI活用ロードマップの策定
数値は具体的に示し、経営判断に直結するインサイトを提供する。
""",
        "presets": [
            ("💰 AI導入ROI詳細試算", "AIエージェント導入の詳細ROI試算を行ってください。部門別の削減工数・コスト削減額・初期投資・投資回収期間を試算し、取締役会向けに説明できる形でまとめてください。"),
            ("📊 チャネル別収益分析", "百貨店・酒販店・飲食店・EC・直販の各チャネル別に、収益貢献度・成長性・今後の注力優先度を分析・提案してください。"),
            ("🗺️ 年間AI活用ロードマップ", "年内いっぱいを目途とした、AIエージェント段階的導入のロードマップを作成してください。各フェーズの目標・KPI・必要リソースを明示してください。"),
            ("📑 取締役会向けDX報告書骨子", "AI・DX推進の取締役会向け報告書の骨子を作成してください。現状課題・導入効果・投資計画・リスクを含めてください。"),
        ]
    },
    "🎤 業務ヒアリング支援": {
        "desc": "各部門担当者へのヒアリングをAIがサポート。課題の抽出・自動化ポイントの特定・改善提案まで行うエージェント。",
        "system": BASE_CONTEXT + """
【あなたの役割】業務ヒアリング・課題抽出専門AIエージェント。
コンサルタントとして、業務担当者から適切に課題を引き出し、AI活用に繋げる。
進め方：
1. 対象部門・担当者の業務内容を確認する
2. 「時間がかかる作業」「繰り返し作業」「ミスが起きやすい作業」「属人化している作業」を質問で引き出す
3. 引き出した課題をAI活用の観点で整理・分類する
4. 優先度付きの改善提案とAI活用案をまとめる
5. 必要に応じて自動化フロー・ツール提案まで行う
質問は一度に1〜2個に絞り、担当者が答えやすいよう具体的に聞く。
ヒアリング結果は最後に「課題整理シート」としてまとめる。
""",
        "presets": [
            ("🎤 受発注部門ヒアリング開始", "受発注・在庫管理部門のヒアリングを始めます。現在の業務フローと課題を聞き出してください。"),
            ("🎤 醸造部門ヒアリング開始", "醸造・製造部門の担当者へのヒアリングを開始してください。日常の手作業・記録作業を中心に課題を引き出してください。"),
            ("🎤 営業部門ヒアリング開始", "営業・顧客対応部門のヒアリングを始めます。提案書作成・顧客フォロー・問い合わせ対応で困っていることを引き出してください。"),
            ("📋 課題整理シートを作成", "これまでのヒアリング内容をもとに、部門別・優先度別の課題整理シートを作成してください。AI活用による解決策も併記してください。"),
        ]
    },
}

# ────────────────────────────────────────────────────
# SESSION STATE INIT
# ────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dept" not in st.session_state:
    st.session_state.dept = list(DEPARTMENTS.keys())[0]
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = ""

# ────────────────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 12px 0 18px;">
        <div style="width:52px;height:52px;border:1.5px solid #c8a84b;border-radius:50%;
                    display:inline-flex;align-items:center;justify-content:center;
                    font-size:22px;color:#c8a84b;margin-bottom:8px;">松</div>
        <div style="color:#c8a84b;font-size:15px;font-weight:600;letter-spacing:0.05em;">松井酒造</div>
        <div style="color:#5a5040;font-size:10px;letter-spacing:0.12em;margin-top:2px;">AI BUSINESS AGENT</div>
    </div>
    """, unsafe_allow_html=True)

    # ── API KEY ──
    with st.expander("🔑 API キー設定", expanded=not bool(st.session_state.api_key)):
        # Try secrets first
        secret_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if secret_key:
            st.session_state.api_key = secret_key
            st.markdown('<span class="gold-badge">✅ APIキー設定済み</span>', unsafe_allow_html=True)
        else:
            key_input = st.text_input(
                "Anthropic API Key",
                value=st.session_state.api_key,
                type="password",
                placeholder="sk-ant-api03-...",
                label_visibility="collapsed"
            )
            if key_input:
                st.session_state.api_key = key_input
                st.success("APIキーが設定されました", icon="✅")
            else:
                st.info("APIキーを入力するとClaudeがリアルタイムで回答します", icon="ℹ️")

    st.markdown("---")

    # ── DEPARTMENT ──
    st.markdown('<div style="color:#7a6530;font-size:10px;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:8px;">担当エージェント選択</div>', unsafe_allow_html=True)

    dept_keys = list(DEPARTMENTS.keys())
    selected_dept = st.radio(
        "部門",
        dept_keys,
        index=dept_keys.index(st.session_state.dept),
        label_visibility="collapsed"
    )

    if selected_dept != st.session_state.dept:
        st.session_state.dept = selected_dept
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # ── PRESETS ──
    st.markdown('<div style="color:#7a6530;font-size:10px;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:8px;">クイック質問</div>', unsafe_allow_html=True)

    current_presets = DEPARTMENTS[st.session_state.dept]["presets"]
    for label, prompt in current_presets:
        if st.button(label, key=f"preset_{label}"):
            st.session_state.preset_prompt = prompt
            st.rerun()

    st.markdown("---")

    # ── CLEAR ──
    if st.button("🗑️ 会話をリセット"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div style="color:#2e2e24;font-size:9px;text-align:center;margin-top:20px;line-height:1.8;letter-spacing:0.08em;">
    MATSUI SAKE BREWERY<br>AI AGENT PROTOTYPE v1.0<br>POWERED BY CLAUDE
    </div>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────────────
# MAIN AREA
# ────────────────────────────────────────────────────
dept_info = DEPARTMENTS[st.session_state.dept]

# Header
col1, col2 = st.columns([6, 2])
with col1:
    st.markdown(f"## {st.session_state.dept}")
    st.markdown(f'<div class="dept-card">{dept_info["desc"]}</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.api_key:
        st.markdown('<br><div style="text-align:right"><span class="gold-badge">🟢 AI 接続中</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<br><div style="text-align:right"><span class="gold-badge" style="border-color:#444;color:#666;">⚪ デモモード</span></div>', unsafe_allow_html=True)

st.markdown("---")

# ── Welcome message ──
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:32px 20px;">
        <div style="color:#c8a84b;font-size:16px;margin-bottom:12px;">このエージェントに何でもご相談ください</div>
        <div style="color:#5a5040;font-size:12px;line-height:1.9;max-width:500px;margin:0 auto;">
        左サイドバーのクイック質問ボタンをクリックするか、<br>
        下の入力欄に自由に質問を入力してください。<br>
        実際の業務データと連携することでリアルタイム応答が可能になります。
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Display chat history ──
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🍶"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ────────────────────────────────────────────────────
# HANDLE PRESET INJECTION
# ────────────────────────────────────────────────────
preset_to_send = ""
if st.session_state.preset_prompt:
    preset_to_send = st.session_state.preset_prompt
    st.session_state.preset_prompt = ""

# ────────────────────────────────────────────────────
# DEMO RESPONSES (no API key)
# ────────────────────────────────────────────────────
DEMO_RESPONSES = {
    "ロードマップ": """## 松井酒造 AI導入ロードマップ（年間計画）

### Phase 1：基盤構築（1〜3ヶ月目）
**目標：** 現状把握と優先業務の自動化PoC

| 施策 | 内容 | 期待効果 |
|------|------|---------|
| 業務ヒアリング | 全部門の課題調査・優先度マッピング | 課題の可視化 |
| 受発注自動化PoC | 注文メール→在庫チェック→出荷指示の自動フロー | 工数▲40h/月 |
| AI問い合わせ対応 | FAQチャットボット導入（顧客向け） | 工数▲20h/月 |

### Phase 2：拡張（4〜6ヶ月目）
**目標：** 主要部門への本格展開

| 施策 | 内容 | 期待効果 |
|------|------|---------|
| 醸造データ分析 | センサーデータ連携・品質アラート自動化 | 不良品率▲30% |
| 営業資料自動生成 | 取引先別の提案書を自動ドラフト | 工数▲30h/月 |
| 在庫需要予測 | 季節需要・販売トレンド分析 | 欠品率▲50% |

### Phase 3：高度化・定着（7〜12ヶ月目）
**目標：** 全社AI活用文化の醸成

| 施策 | 内容 | 期待効果 |
|------|------|---------|
| 経営ダッシュボード | KPI自動集計・経営報告の自動化 | 工数▲20h/月 |
| 社員AI教育 | 全部門向けAI活用トレーニング | 自走率向上 |
| 継続改善体制 | 月次レビューと改善サイクルの確立 | PDCAの高速化 |

---
**💰 年間削減効果（試算）：約400〜600万円 / 投資回収：3〜4ヶ月**

APIキーを設定すると、御社の具体的な状況に合わせた詳細計画を生成できます。""",

    "roi": """## AI エージェント導入 ROI 試算レポート

### 業務別 削減時間・コスト試算

| 業務カテゴリ | 現状工数/月 | AI導入後 | 削減工数 |
|------------|-----------|---------|--------|
| 受注・在庫確認 | 40h | 8h | **32h** |
| 提案書・書類作成 | 30h | 5h | **25h** |
| 問い合わせ対応 | 25h | 5h | **20h** |
| データ集計・報告 | 20h | 3h | **17h** |
| 合計 | **115h** | **21h** | **94h** |

### 金額換算（@3,500円/h）

```
月間削減コスト：329,000円
年間削減コスト：3,948,000円（約400万円）
```

### 投資試算

```
初期構築費用：700,000〜1,000,000円
月額運用費用：   50,000〜80,000円/月
```

### 投資回収シミュレーション

| 月 | 累計投資 | 累計削減 | 収支 |
|----|---------|---------|------|
| 1ヶ月目 | 850,000円 | 329,000円 | △521,000円 |
| 2ヶ月目 | 915,000円 | 658,000円 | △257,000円 |
| **3ヶ月目** | 980,000円 | 987,000円 | **▶ 黒字転換** |
| 12ヶ月目 | 1,610,000円 | 3,948,000円 | **+2,338,000円** |

**📌 結論：3ヶ月で回収。年間約230万円の純利益貢献。**""",

    "仕込み": """## 純米大吟醸 仕込みスケジュール案

### 2026年度 第一期仕込み

**▶ 洗米・浸漬（10/15〜10/16）**
- 精米歩合50%の山田錦使用
- 浸漬時間：20時間（水分吸収率30%目標）

**▶ 蒸米・放冷（10/17）**
- 蒸し時間：60分 / 放冷後温度：35℃

**▶ 麹づくり（10/17〜10/20）**
- 製麹期間：3日間 / 麹室温度：30〜32℃管理

**▶ 酒母仕込み（10/21〜11/10）**
- 山廃仕込み：20日間 / 目標日本酒度：+12〜+15

**▶ 本仕込み（三段仕込み）**
- 初添え：11/11 / 仲添え：11/13 / 留添え：11/16

**▶ 醪管理期間（11/16〜12/20）**
- 発酵温度：8〜12℃低温管理 / 目標アルコール：17〜18度

**▶ 上槽・火入れ（12/21〜12/25）**
- 袋吊りによる搾り / 65℃火入れ処理

---
⚠️ **注意事項：** 気温が例年より高い場合、麹室の温度管理を強化してください。
📋 **次のアクション：** 原料米の在庫確認と水質検査データの確認を推奨します。""",

    "在庫": """## 在庫・出荷状況レポート

### 現在の在庫状況（概要）

| 銘柄 | 在庫 | 予約済 | 残余 | ステータス |
|------|------|-------|------|----------|
| 純米大吟醸 | 240本 | 180本 | 60本 | ⚠️ 要注意 |
| 純米吟醸 | 580本 | 210本 | 370本 | ✅ 問題なし |
| 本醸造 | 920本 | 310本 | 610本 | ✅ 問題なし |
| にごり酒 | 85本 | 90本 | **-5本** | 🔴 不足 |

### 緊急対応が必要な銘柄

🔴 **にごり酒：5本不足**
→ 追加生産 or 既存顧客へのキャンセル交渉が必要

⚠️ **純米大吟醸：残余60本**
→ 新規受注の一時停止を検討 / 増産計画を立案

### 推奨アクション（優先度順）

1. にごり酒の追加確保先を至急確認
2. 純米大吟醸の新規受注受付を一時停止
3. 年末商戦向け増産計画の策定（来週中）
4. 取引先への出荷スケジュール再調整""",
}

def get_demo_response(prompt: str) -> str:
    p = prompt
    if any(k in p for k in ["ロードマップ", "計画", "フェーズ", "段階"]):
        return DEMO_RESPONSES["ロードマップ"]
    if any(k in p for k in ["roi", "ROI", "投資", "試算", "コスト削減", "効果"]):
        return DEMO_RESPONSES["roi"]
    if any(k in p for k in ["仕込み", "醸造", "麹", "酒母", "醪", "スケジュール"]):
        return DEMO_RESPONSES["仕込み"]
    if any(k in p for k in ["在庫", "出荷", "受注", "在庫状況"]):
        return DEMO_RESPONSES["在庫"]
    return f"""ご質問ありがとうございます。

**「{p[:40]}{'...' if len(p) > 40 else ''}」** についてお答えします。

実際のシステム運用時は、以下のデータソースと連携してリアルタイムで回答します：

| データソース | 連携内容 |
|------------|---------|
| 🗄️ 基幹システム | 受発注・在庫・売上データ |
| 🍶 醸造管理DB | 品質ログ・工程記録 |
| 👥 顧客CRM | 取引先・商談・問い合わせ履歴 |
| 📄 社内ドキュメント | 規程・マニュアル・過去提案書 |

---

現在は**デモモード**のため、代表的な回答パターンを表示しています。

**APIキーを設定すると：**
- Claudeによるリアルタイム・高精度な応答に切り替わります
- 御社の状況に合わせた具体的な提案が可能になります

左サイドバーのクイック質問ボタンで、各業務シナリオのデモをご覧いただけます。"""

# ────────────────────────────────────────────────────
# CHAT INPUT & RESPONSE
# ────────────────────────────────────────────────────
user_prompt = st.chat_input("業務に関する質問や指示を入力してください...")

# Use preset if set
final_prompt = preset_to_send or user_prompt

if final_prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": final_prompt})

    with st.chat_message("user", avatar="👤"):
        st.markdown(final_prompt)

    with st.chat_message("assistant", avatar="🍶"):
        if st.session_state.api_key:
            # ── Real Claude API (streaming) ──
            client = Anthropic(api_key=st.session_state.api_key)
            api_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            try:
                with client.messages.stream(
                    model="claude-opus-4-5",
                    max_tokens=2048,
                    system=dept_info["system"],
                    messages=api_messages,
                ) as stream:
                    response_text = st.write_stream(stream.text_stream)
            except Exception as e:
                response_text = f"⚠️ APIエラー: {e}\n\nAPIキーをご確認ください。"
                st.error(response_text)
        else:
            # ── Demo mode ──
            import time
            placeholder = st.empty()
            demo_text = get_demo_response(final_prompt)
            displayed = ""
            for char in demo_text:
                displayed += char
                placeholder.markdown(displayed + "▌")
                time.sleep(0.004)
            placeholder.markdown(demo_text)
            response_text = demo_text

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.rerun()
