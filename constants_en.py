"""
英語の定数定義ファイル
"""

############################################################
# ライブラリの読み込み
############################################################
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import UnstructuredExcelLoader

############################################################
# 英語定数の定義
############################################################

# ==========================================
# 画面表示系
# ==========================================
APP_NAME = "⛑️🏗️Construction Site Inquiry Chatbot"
CHAT_INPUT_HELPER_TEXT = "Please send your message from here."
APP_BOOT_MESSAGE = "Application has been started."
WARNING_ICON = ":material/warning:"
ERROR_ICON = ":material/error:"
SPINNER_TEXT = "Searching..."
SPINNER_CONTACT_TEXT = "Sending your inquiry to our staff. Please do not operate the screen and wait."
CONTACT_THANKS_MESSAGE = """Thank you for your inquiry.
Our staff will review the content and respond.
However, inquiries received on Saturdays, Sundays, holidays, and year-end/New Year holidays will be handled on the next business day.
Thank you for your understanding.
If urgent, please contact Mr. Takeda's mobile phone listed on the flyer."""

CONTACT_MODE_HEADER = "## Inquiry Mode"
CONTACT_MODE_SELECTION_TEXT = "Inquiry Mode Selection"
CONTACT_MODE_DESCRIPTION_TEXT = "**【What is Inquiry Mode?】**"
CONTACT_MODE_DESCRIPTION_DETAIL_TEXT = "When you turn inquiry mode 'ON' and send a message, it will be delivered directly to the person in charge."
CONTACT_MODE_BOT_INTRODUCTION_TEXT = "This is a generative AI chatbot that answers questions about this construction work. Please select inquiry mode and ask questions from the chat field at the bottom of the screen."
CONTACT_MODE_BOT_SPECIFICITY_TEXT = "When the inquiry mode is turned off, the inquiry chatbot will still answer your questions."
CONTACT_MODE_OFF = "OFF (Use as AI chatbot)"
CONTACT_MODE_ON = "ON (Direct inquiry to staff)"

# ==========================================
# プロンプトテンプレート
# ==========================================
SYSTEM_PROMPT_CREATE_INDEPENDENT_TEXT = "Based on conversation history and latest input, generate independent input text that can be understood without conversation history."
NO_DOC_MATCH_MESSAGE = "The information necessary for an answer was not found. Please change your construction-related question and send it again."

SYSTEM_PROMPT_INQUIRY = """You are an assistant that responds to inquiries from residents at construction sites based on specifications and construction plans.
Please respond to user input based on the following conditions, and answer in ENGLISH.

【Conditions】
1. Only when there is relevance between user input content and the following context, please respond based on the following context.
2. If the relevance between user input content and the following context is clearly low, respond with "The information necessary for an answer was not found. Please change your construction-related question and send it again."
3. Do not answer with speculation, but answer based on the following context.
4. Please answer in as much detail as possible using markdown notation.
5. When using h tags for headings in markdown notation, make the largest heading h3.
6. For complex questions, please answer each item in detail.
7. For questions about the end of construction and construction period, be sure to check the bulletin board at the site or ask the construction manager to confirm.
8. For questions about flyer distribution, answer that flyers will be distributed 2-3 days before construction in front of homes.
9. For questions about construction location, answer that it is Nanatsu-ike Heights, Hachihonmatsu-minami 4-chome, Higashihiroshima City, Hiroshima Prefecture.
10. If deemed necessary, you may provide general information without being based on the following context.
11. IMPORTANT: Always respond in ENGLISH regardless of the input language.

{context}"""

# ==========================================
# エラー・警告メッセージ
# ==========================================
COMMON_ERROR_MESSAGE = "If this error occurs repeatedly, please contact the administrator."
INITIALIZE_ERROR_MESSAGE = "Initialization process failed."
CONVERSATION_LOG_ERROR_MESSAGE = "Failed to display past conversation history."
MAIN_PROCESS_ERROR_MESSAGE = "Failed to process user input."
DISP_ANSWER_ERROR_MESSAGE = "Failed to display answer."
INPUT_TEXT_LIMIT_ERROR_MESSAGE = "The number of characters in the input text exceeds the acceptance limit ({max_tokens}). Please enter again so as not to exceed the acceptance limit."
RAG_CHAIN_EXECUTION_ERROR_MESSAGE = "RAG chain execution failed."
GMAIL_SETTINGS_ERROR_MESSAGE = "Gmail settings are incomplete. Please contact the administrator."
CONTACT_FORWARDING_SUBJECT = "[Inquiry] Transfer from AI Chatbot"
GMAIL_SENDING_ERROR_MESSAGE = "Gmail sending error"
GMAIL_SENDING_ERROR_DETAIL_MESSAGE = "An error occurred while sending email. Please contact the administrator."

# ==========================================
# メール送信フォーマット
# ==========================================
EMAIL_FORMAT_TEMPLATE = """以下の問い合わせがAIチャットボットから転送されました。

【問い合わせ内容（英語）】
{chat_message}

【問い合わせ内容（日本語翻訳）】
{translated_message}

【受信日時】
{datetime}

【送信元】
AIチャットボットシステム

このメールは自動送信されています。"""


TRANSLATION_TEMPLATE = """以下の英語のテキストを自然な日本語に翻訳してください。
翻訳結果のみを返してください。

英語テキスト: {english_text}

日本語翻訳:"""

# ==========================================
# 言語選択
# ==========================================
LANGUAGE_SELECTION_HEADER = "## 言語選択 / Language Selection"
LANGUAGE_SELECTION_TEXT = "Please select a language"
SUPPORTED_LANGUAGES = {
    "ja": "日本語",
    "en": "English"
}

# ==========================================
# テーマ切り替え
# ==========================================
THEME_TOGGLE_HEADER = "## 🎨 Theme Toggle"
DARK_MODE_BUTTON = "🌙 Dark Mode"
LIGHT_MODE_BUTTON = "☀️ Light Mode"