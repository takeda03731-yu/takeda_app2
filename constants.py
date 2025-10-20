"""
このファイルは、固定の文字列や数値などのデータを変数として一括管理するファイルです。
多言語対応版
"""

############################################################
# ライブラリの読み込み
############################################################
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
import streamlit as st

############################################################
# 多言語対応の設定
############################################################

def get_language_constants():
    """
    選択された言語に応じた定数を取得
    """
    # セッション状態から言語を取得（デフォルトは日本語）
    lang = getattr(st.session_state, 'language', 'ja')
    
    if lang == 'en':
        import constants_en as lang_constants
    else:  # デフォルトは日本語
        import constants_ja as lang_constants
    
    return lang_constants

############################################################
# 言語に依存しない定数（システム設定等）
############################################################

# ==========================================
# ファイルパス系
# ==========================================
USER_ICON_FILE_PATH = "./images/user_icon.jpg"
AI_ICON_FILE_PATH = "./images/ai_icon.jpg"
LOG_DIR_PATH = "./logs"
LOGGER_NAME = "ApplicationLog"
LOG_FILE = "application.log"

# ==========================================
# LLM設定系
# ==========================================
MODEL = "gpt-4o-mini"
TEMPERATURE = 0.5
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
TOP_K = 8
RETRIEVER_WEIGHTS = [0.5, 0.5]

# ==========================================
# トークン関連
# ==========================================
MAX_ALLOWED_TOKENS = 1000
ENCODING_KIND = "cl100k_base"

# ==========================================
# RAG参照用のデータソース系
# ==========================================
RAG_TOP_FOLDER_PATH = "./data/rag"

SUPPORTED_EXTENSIONS = {
    ".pdf": PyMuPDFLoader,
    ".xlsx": lambda path: UnstructuredExcelLoader(path, mode="elements"),
    ".xls":  lambda path: UnstructuredExcelLoader(path, mode="elements"),
}

DB_ALL_PATH = "./.db_all"
DB_COMPANY_PATH = "./.db_company"

# ==========================================
# スタイリング
# ==========================================
LIGHT_MODE_STYLE = """
<style>
    /* 1) 同じ幅を両方に適用できるよう、変数で一元管理 */
    :root{ --content-max: 800px; }  /* ← 好きな幅に */

    /* 2) 本文側（タイトル等）の最大幅 */
    [data-testid="stAppViewContainer"] .block-container{
        max-width: var(--content-max);
        padding-left: 2rem;
        padding-right: 2rem;
        margin: 0 auto;
    }

    /* 3) チャット入力バーにも同じ最大幅を適用して中央寄せ */
    /* 主要バージョン */
    [data-testid="stChatInput"]{
        max-width: var(--content-max);
        margin: 0 auto 1rem;
    }
    /* ラッパーがある版（環境差のフォールバック） */
    [data-testid="stChatInput"] > div{
        max-width: var(--content-max);
        margin: 0 auto;
    }
    /* さらに古い/別ビルドのフォールバック（必要な場合だけ生かす） */
    [data-testid="stBottomBlockContainer"]{
        max-width: var(--content-max);
        margin: 0 auto;
    }
    .stHorizontalBlock {
        margin-top: -14px;
    }
    .stChatMessage + .stHorizontalBlock .stColumn:nth-of-type(2) {
        margin-left: -24px;
    }
    @media screen and (max-width: 480px) {
        .stChatMessage + .stHorizontalBlock {
            flex-wrap: nowrap;
            margin-left: 56px;
        }
        .stChatMessage + .stHorizontalBlock .stColumn:nth-of-type(2) {
            margin-left: -206px;
        }
    }
</style>
"""

DARK_MODE_STYLE = """
<style>
    /* 1) 同じ幅を両方に適用できるよう、変数で一元管理 */
    :root{ --content-max: 800px; }  /* ← 好きな幅に */

    /* ダークモード用のカラーパレット */
    :root {
        --bg-color: #0e1117;
        --secondary-bg: #262730;
        --text-color: #fafafa;
        --border-color: #464853;
        --chat-user-bg: #1e3a8a;
        --chat-ai-bg: #1f2937;
        --chat-input-bg: #3a3f4b;  /* チャット入力用の明るい背景色 */
        --chat-input-border: #6b7280;  /* チャット入力用のボーダー色 */
    }

    /* 最上位のHTML要素とbody要素 */
    html, body {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 全体の背景色 */
    .stApp {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
    }

    /* メインコンテナ */
    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-color) !important;
    }

    [data-testid="stAppViewContainer"] .block-container{
        max-width: var(--content-max);
        padding-left: 2rem;
        padding-right: 2rem;
        margin: 0 auto;
        background-color: var(--bg-color) !important;
    }

    /* メインコンテナの外側の余白部分 */
    [data-testid="stAppViewContainer"] > .main {
        background-color: var(--bg-color) !important;
        padding: 0 !important;
    }

    /* ヘッダー部分 */
    [data-testid="stHeader"] {
        background-color: var(--bg-color) !important;
    }

    /* フッター部分 */
    [data-testid="stBottom"] {
        background-color: var(--bg-color) !important;
    }

    /* Streamlitのデフォルト余白をリセット */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }

    /* 画面全体の余白をゼロに */
    .reportview-container {
        background-color: var(--bg-color) !important;
    }

    /* サイドバー */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-bg) !important;
    }

    /* サイドバーのコンテンツ */
    [data-testid="stSidebar"] > div {
        background-color: var(--secondary-bg) !important;
    }

    /* チャット入力バー */
    [data-testid="stChatInput"]{
        max-width: var(--content-max);
        margin: 0 auto 1rem;
        background-color: var(--bg-color) !important;
    }
    
    [data-testid="stChatInput"] > div{
        max-width: var(--content-max);
        margin: 0 auto;
        background-color: var(--bg-color) !important;
    }
    
    [data-testid="stBottomBlockContainer"]{
        max-width: var(--content-max);
        margin: 0 auto;
        background-color: var(--bg-color) !important;
    }

    /* チャット入力エリアの背景 */
    [data-testid="stChatInputContainer"] {
        background-color: var(--bg-color) !important;
    }

    /* チャット入力フィールド自体 */
    [data-testid="stChatInput"] input {
        background-color: var(--chat-input-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--chat-input-border) !important;
        border-radius: 8px !important;
    }

    /* チャット入力フィールドのプレースホルダー */
    [data-testid="stChatInput"] input::placeholder {
        color: rgba(250, 250, 250, 0.7) !important;
    }

    /* チャット送信ボタン */
    [data-testid="stChatInput"] button {
        background-color: var(--chat-input-border) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--chat-input-border) !important;
        border-radius: 8px !important;
    }

    /* チャット送信ボタンのホバー効果 */
    [data-testid="stChatInput"] button:hover {
        background-color: var(--text-color) !important;
        color: var(--bg-color) !important;
    }

    /* 下部エリア全体 */
    section[data-testid="stBottom"] {
        background-color: var(--bg-color) !important;
    }

    /* フッター要素 */
    footer {
        background-color: var(--bg-color) !important;
    }

    /* 余白やパディングエリア */
    .stApp > div:last-child {
        background-color: var(--bg-color) !important;
    }

    /* チャットメッセージ */
    [data-testid="stChatMessage"] {
        background-color: var(--secondary-bg) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-color) !important;
    }

    /* テキスト要素 */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
        color: var(--text-color) !important;
    }

    /* セレクトボックス */
    .stSelectbox > div > div {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
        border-color: var(--border-color) !important;
    }

    /* サイドバー内のセレクトボックス */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
        border-color: var(--border-color) !important;
    }

    /* サイドバー内の全ての要素 */
    [data-testid="stSidebar"] * {
        color: var(--text-color) !important;
    }

    /* サイドバー内のマークダウン要素 */
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-color) !important;
    }

    [data-testid="stSidebar"] .stMarkdown p {
        color: var(--text-color) !important;
    }

    /* ボタン */
    .stButton > button {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
        border-color: var(--border-color) !important;
    }

    .stButton > button:hover {
        background-color: var(--border-color) !important;
    }

    /* 成功・警告メッセージ */
    .stAlert {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
        border-color: var(--border-color) !important;
    }

    /* コードブロック */
    .stCode {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
    }

    /* コードブロック内のテキスト */
    .stCode > div {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
    }

    /* コードブロック内のpre要素 */
    .stCode pre {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
    }

    /* コードブロック内のcode要素 */
    .stCode code {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
    }

    /* サイドバー内のコードブロック */
    [data-testid="stSidebar"] .stCode {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
    }

    [data-testid="stSidebar"] .stCode > div {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
    }

    [data-testid="stSidebar"] .stCode pre {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
    }

    [data-testid="stSidebar"] .stCode code {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
    }

    /* Streamlitのデフォルトパディングを調整 */
    .css-1d391kg, .css-1lcbmhc, .css-1outpf7 {
        background-color: var(--bg-color) !important;
    }

    /* 上下左右の余白を完全に除去 */
    .stApp > header,
    .stApp > footer,
    .stApp > div[data-testid="stDecoration"] {
        background-color: var(--bg-color) !important;
    }

    /* ビューポート全体の背景 */
    #root > div {
        background-color: var(--bg-color) !important;
    }

    /* Streamlitの固定フッター */
    .stAppBottom {
        background-color: var(--bg-color) !important;
    }

    /* 入力フィールドの親コンテナ */
    .stChatFloatingInputContainer {
        background-color: var(--bg-color) !important;
    }

    /* ボトムエリアの全ての div 要素 */
    [data-testid="stBottom"] div {
        background-color: var(--bg-color) !important;
    }

    /* 画面下部の余白部分 */
    .stApp::after {
        background-color: var(--bg-color) !important;
    }

    /* チャット入力周辺のより具体的なセレクタ */
    [data-testid="chatInput"] {
        background-color: var(--bg-color) !important;
    }

    /* チャット入力の具体的なスタイリング */
    [data-testid="stChatInput"] textarea {
        background-color: var(--chat-input-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--chat-input-border) !important;
        border-radius: 8px !important;
    }

    /* チャット入力のフォーカス状態 */
    [data-testid="stChatInput"] input:focus,
    [data-testid="stChatInput"] textarea:focus {
        border-color: #9ca3af !important;
        box-shadow: 0 0 0 2px rgba(156, 163, 175, 0.3) !important;
        background-color: #4b5563 !important;
    }

    /* チャット入力コンテナの背景色を除外 */
    [data-testid="stChatInput"] > div > div {
        background-color: transparent !important;
    }

    /* メインコンテナの周辺余白 */
    .main .block-container::before,
    .main .block-container::after {
        background-color: var(--bg-color) !important;
    }

    /* Streamlitデフォルトのパディング領域 */
    .reportview-container .main .block-container {
        background-color: var(--bg-color) !important;
    }

    .stHorizontalBlock {
        margin-top: -14px;
    }
    .stChatMessage + .stHorizontalBlock .stColumn:nth-of-type(2) {
        margin-left: -24px;
    }
    @media screen and (max-width: 480px) {
        .stChatMessage + .stHorizontalBlock {
            flex-wrap: nowrap;
            margin-left: 56px;
        }
        .stChatMessage + .stHorizontalBlock .stColumn:nth-of-type(2) {
            margin-left: -206px;
        }
    }
</style>
"""

# 後方互換性のためのデフォルトスタイル
STYLE = LIGHT_MODE_STYLE

############################################################
# 動的に言語定数を取得する関数
############################################################

def get_text(key):
    """
    指定されたキーの多言語テキストを取得
    """
    lang_constants = get_language_constants()
    return getattr(lang_constants, key, f"[Missing: {key}]")

def get_formatted_text(key, **kwargs):
    """
    フォーマット付きテキストを取得
    """
    text = get_text(key)
    if kwargs:
        if 'max_tokens' in text:
            kwargs['max_tokens'] = MAX_ALLOWED_TOKENS
        return text.format(**kwargs)
    return text

def get_current_style():
    """
    現在のテーマに応じたスタイルを取得
    """
    is_dark_mode = getattr(st.session_state, 'dark_mode', False)
    return DARK_MODE_STYLE if is_dark_mode else LIGHT_MODE_STYLE