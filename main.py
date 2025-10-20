"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
from dotenv import load_dotenv
import logging
import streamlit as st
import utils
import traceback
from initialize import initialize
import components as cn
import constants as ct
from initialize import _ensure_encoder

############################################################
# 設定関連
############################################################

_ensure_encoder()

# 言語システムの初期化（ページタイトル設定前に実行）
if 'language' not in st.session_state:
    st.session_state.language = 'ja'

st.set_page_config(
    page_title=ct.get_text('APP_NAME'),
    page_icon="⛑️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

logger = logging.getLogger(ct.LOGGER_NAME)


############################################################
# 初期化処理
############################################################
try:
    initialize()
except Exception as e:
    logger.error(f"{ct.get_text('INITIALIZE_ERROR_MESSAGE')}\n{e}\n{traceback.format_exc()}")
    st.error(utils.build_error_message(ct.get_text('INITIALIZE_ERROR_MESSAGE')) + "\n" + traceback.format_exc(), icon=ct.get_text('ERROR_ICON'))
    st.stop()

# アプリ起動時のログ出力
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.get_text('APP_BOOT_MESSAGE'))

############################################################
# 初期表示
############################################################
# タイトル表示
cn.display_app_title()

# サイドバー表示
cn.display_sidebar()

# AIメッセージの初期表示
cn.display_initial_ai_message()


############################################################
# スタイリング処理
############################################################
# ダークモード状態に応じて動的にCSSを適用
st.markdown(ct.get_current_style(), unsafe_allow_html=True)

############################################################
# チャット入力の受け付け
############################################################
chat_message = st.chat_input(ct.get_text('CHAT_INPUT_HELPER_TEXT'))

############################################################
# 会話ログの表示
############################################################
try:
    cn.display_conversation_log(chat_message)
except Exception as e:
    logger.error(f"{ct.get_text('CONVERSATION_LOG_ERROR_MESSAGE')}\n{e}\n{traceback.format_exc()}")
    st.error(utils.build_error_message(ct.get_text('CONVERSATION_LOG_ERROR_MESSAGE')) + "\n" + traceback.format_exc(), icon=ct.get_text('ERROR_ICON'))
    st.stop()

############################################################
# チャット送信時の処理
############################################################
if chat_message:
    # ==========================================
    # 会話履歴の上限を超えた場合、受け付けない
    # ==========================================
    # ユーザーメッセージのトークン数を取得
    input_tokens = len(st.session_state.enc.encode(chat_message))
    # トークン数が、受付上限を超えている場合にエラーメッセージを表示
    if input_tokens > ct.MAX_ALLOWED_TOKENS:
        with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
            st.error(ct.get_formatted_text('INPUT_TEXT_LIMIT_ERROR_MESSAGE', max_tokens=ct.MAX_ALLOWED_TOKENS))
            st.stop()
    # トークン数が受付上限を超えていない場合、会話ログ全体のトークン数に加算
    st.session_state.total_tokens += input_tokens

    # ==========================================
    # 1. ユーザーメッセージの表示
    # ==========================================
    logger.info({"message": chat_message})

    with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
        st.markdown(chat_message)
    
        # ==========================================
    # 2. LLMからの回答取得 or 問い合わせ処理
    # ==========================================
    try:
        if st.session_state.contact_mode == ct.get_text('CONTACT_MODE_OFF'):
            with st.spinner(ct.get_text('SPINNER_TEXT')):
                result = utils.execute_chain(chat_message)
        else:
            with st.spinner(ct.get_text('SPINNER_CONTACT_TEXT')):
                # Gmail転送機能を使用
                result = utils.send_inquiry_to_gmail(chat_message)
    except Exception as e:
        logger.error(f"{ct.get_text('MAIN_PROCESS_ERROR_MESSAGE')}\n{e}\n{traceback.format_exc()}")
        st.error(utils.build_error_message(ct.get_text('MAIN_PROCESS_ERROR_MESSAGE')) + "\n" + traceback.format_exc(), icon=ct.get_text('ERROR_ICON'))
        st.stop()
    
    # ==========================================
    # 3. 古い会話履歴を削除
    # ==========================================
    utils.delete_old_conversation_log(result)
    # ==========================================
    # 4. LLMからの回答表示
    # ==========================================
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        st.markdown(result)
    
    # ==========================================
    # 5. 会話ログへの追加
    # ==========================================
    st.session_state.messages.append({"role": "user", "content": chat_message})
    st.session_state.messages.append({"role": "assistant", "content": result})
