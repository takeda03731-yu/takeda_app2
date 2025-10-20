"""
このファイルは、最初の画面読み込み時にのみ実行される初期化処理が記述されたファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from uuid import uuid4
from dotenv import load_dotenv
import streamlit as st
import tiktoken
from langchain_openai import ChatOpenAI
import utils
import constants as ct

############################################################
# 設定関連
############################################################
load_dotenv()


############################################################
# 関数定義
############################################################

def _ensure_encoder():
    if "enc" not in st.session_state:
        # 使うモデル名（環境変数などから）
        model = os.getenv("OPENAI_MODEL", ct.MODEL)
        try:
            # モデルに合うエンコーディングを自動で選ぶ
            st.session_state["enc"] = tiktoken.encoding_for_model(model)
        except Exception:
            # うまく選べなければ汎用のエンコーディングにフォールバック
            st.session_state["enc"] = tiktoken.get_encoding("cl100k_base")

def initialize():
    """
    画面読み込み時に実行する初期化処理
    """
    # 言語システムの初期化
    if 'language' not in st.session_state:
        st.session_state.language = 'ja'
    
    # エンコーダーの初期化
    _ensure_encoder()
    # 初期化データの用意
    initialize_session_state()
    # ログ出力用にセッションIDを生成
    initialize_session_id()
    # ログ出力の設定
    initialize_logger()
    # LLMの初期化
    initialize_llm()
    # RAGチェーンの初期化
    initialize_rag_chain()


def initialize_session_state():
    """
    初期化データの用意
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_history = []
        # 会話履歴の合計トークン数を加算する用の変数
        st.session_state.total_tokens = 0
    
    # ダークモードの初期化
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

def initialize_session_id():
    """
    セッションIDの作成
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid4().hex


def initialize_logger():
    """
    ログ出力の設定
    """
    os.makedirs(ct.LOG_DIR_PATH, exist_ok=True)

    logger = logging.getLogger(ct.LOGGER_NAME)

    if logger.hasHandlers():
        return

    log_handler = TimedRotatingFileHandler(
        os.path.join(ct.LOG_DIR_PATH, ct.LOG_FILE),
        when="D",
        encoding="utf8"
    )
    formatter = logging.Formatter(
        f"[%(levelname)s] %(asctime)s line %(lineno)s, in %(funcName)s, session_id={st.session_state.session_id}: %(message)s"
    )
    log_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)


def initialize_llm():
    """
    LLMの初期化
    """
    if "llm" not in st.session_state:
        st.session_state.llm = ChatOpenAI(
            model=ct.MODEL,
            temperature=ct.TEMPERATURE,
            streaming=True
            # StreamlitCallbackHandlerを削除（コンテキストエラーの原因）
        )


def initialize_rag_chain():
    """
    RAGチェーンの初期化
    """
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = utils.create_rag_chain(ct.DB_ALL_PATH)


