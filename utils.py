"""
このファイルは、画面表示以外の様々な関数定義のファイルです。
多言語対応版
"""

############################################################
# ライブラリの読み込み
############################################################
import os
from dotenv import load_dotenv
import streamlit as st
import logging
import sys
import uuid
import unicodedata
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from typing import List
from sudachipy import tokenizer, dictionary
from langchain.chains import LLMChain
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import constants as ct

############################################################
# 設定関連
############################################################
load_dotenv()

############################################################
# 関数定義
############################################################

def build_error_message(message):
    """
    エラーメッセージと管理者問い合わせテンプレートの連結

    Args:
        message: 画面上に表示するエラーメッセージ

    Returns:
        エラーメッセージと管理者問い合わせテンプレートの連結テキスト
    """
    return "\n".join([message, ct.get_text('COMMON_ERROR_MESSAGE')])

def create_rag_chain(db_name):
    """
    引数として渡されたDB内を参照するRAGのChainを作成

    Args:
        db_name: RAG化対象のデータを格納するデータベース名
    """
    logger = logging.getLogger(ct.LOGGER_NAME)
    # embeddings は 既存DBを読む場合も必要なので先に用意
    embeddings = OpenAIEmbeddings()

    # すでに対象のデータベースが作成済みの場合は読み込み、未作成の場合のみ新規作成する
    if os.path.isdir(db_name):
        db = Chroma(persist_directory=db_name, embedding_function=embeddings)
    else:
        docs_all = []
        if db_name == ct.DB_ALL_PATH:
            folders = os.listdir(ct.RAG_TOP_FOLDER_PATH)
            # 「data」フォルダ直下の各フォルダ名に対して処理
            for folder_path in folders:
                if folder_path.startswith("."):
                    continue
                # フォルダ内の各ファイルのデータをリストに追加
                add_docs(f"{ct.RAG_TOP_FOLDER_PATH}/{folder_path}", docs_all)

        # OSがWindowsの場合、Unicode正規化と、cp932（Windows用の文字コード）で表現できない文字を除去
        for doc in docs_all:
            doc.page_content = adjust_string(doc.page_content)
            for key in doc.metadata:
                doc.metadata[key] = adjust_string(doc.metadata[key])
        
        text_splitter = CharacterTextSplitter(
            chunk_size=ct.CHUNK_SIZE,
            chunk_overlap=ct.CHUNK_OVERLAP,
            separator="\n",
        )
        splitted_docs = text_splitter.split_documents(docs_all)
        db = Chroma.from_documents(splitted_docs, embedding=embeddings, persist_directory=db_name)

    retriever = db.as_retriever(search_kwargs={"k": ct.TOP_K})

    # 多言語対応：現在の言語に基づいてプロンプトテンプレートを取得
    question_generator_template = ct.get_text('SYSTEM_PROMPT_CREATE_INDEPENDENT_TEXT')
    question_generator_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", question_generator_template),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_template = ct.get_text('SYSTEM_PROMPT_INQUIRY')
    question_answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", question_answer_template),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        st.session_state.llm, retriever, question_generator_prompt
    )
    question_answer_chain = create_stuff_documents_chain(st.session_state.llm, question_answer_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    return rag_chain

def add_docs(folder_path, docs_all):
    """
    フォルダ内のファイル一覧を取得

    Args:
        folder_path: フォルダのパス
        docs_all: 各ファイルデータを格納するリスト
    """
    if not os.path.isdir(folder_path):
        return  # フォルダがなければ何もしない
    files = os.listdir(folder_path)
    for file in files:
        # ファイルの拡張子を取得
        file_extension = os.path.splitext(file)[1]
        # 想定していたファイル形式の場合のみ読み込む
        if file_extension in ct.SUPPORTED_EXTENSIONS:
            # ファイルの拡張子に合ったdata loaderを使ってデータ読み込み
            loader = ct.SUPPORTED_EXTENSIONS[file_extension](f"{folder_path}/{file}")
        else:
            continue
        docs = loader.load()
        for doc in docs:
            doc.id = str(uuid.uuid4())  # Chroma用にid属性を付与
        docs_all.extend(docs)

def delete_old_conversation_log(result):
    """
    古い会話履歴の削除

    Args:
        result: LLMからの回答
    """
    # LLMからの回答テキストのトークン数を取得
    response_tokens = len(st.session_state.enc.encode(result))
    # 過去の会話履歴の合計トークン数に加算
    st.session_state.total_tokens += response_tokens

    # トークン数が上限値を下回るまで、順に古い会話履歴を削除
    while st.session_state.total_tokens > ct.MAX_ALLOWED_TOKENS:
        # 最も古い会話履歴を削除
        removed_message = st.session_state.chat_history.pop(1)
        # 最も古い会話履歴のトークン数を取得
        removed_tokens = len(st.session_state.enc.encode(removed_message.content))
        # 過去の会話履歴の合計トークン数から、最も古い会話履歴のトークン数を引く
        st.session_state.total_tokens -= removed_tokens

def execute_chain(chat_message: str) -> str:
    """
    RAGのChainを実行して回答テキストを返す（安全版）

    Args:
        chat_message: ユーザーメッセージ
    Returns:
        回答テキスト（str）
    """
    from typing import Any

    logger = logging.getLogger(ct.LOGGER_NAME)
    ss = st.session_state

    # 1) 履歴の安全初期化
    if "chat_history" not in ss or not isinstance(ss.chat_history, list):
        ss.chat_history = []

    # 2) 実行
    try:
        result: Any = ss.rag_chain.invoke({
            "input": chat_message,
            "chat_history": ss.chat_history
        })
    except Exception as e:
        logger.exception(ct.get_text('RAG_CHAIN_EXECUTION_ERROR_MESSAGE'), exc_info=e)
        raise

    # 3) 結果の取り出し（返却形式の差異に耐える）
    answer: str
    if isinstance(result, dict):
        for key in ("answer", "output_text", "result", "output"):
            if key in result and isinstance(result[key], str):
                answer = result[key]
                break
        else:
            # 文字列が見つからない場合は全体を文字列化
            answer = str(result)
    else:
        answer = str(result)

    # 4) 「情報が見つからない」場合のチェック（多言語対応）
    no_doc_keywords = {
        'ja': ['回答に必要な情報が見つかりませんでした', '情報が見つかりませんでした'],
        'en': ['not found', 'information necessary', 'was not found']
    }
    
    current_lang = getattr(ss, 'language', 'ja')
    if current_lang in no_doc_keywords:
        for keyword in no_doc_keywords[current_lang]:
            if keyword.lower() in answer.lower():
                answer = ct.get_text('NO_DOC_MATCH_MESSAGE')
                break

    # 5) 会話履歴へ追記（LangChainのメッセージ型が無い環境でも落ちないように）
    try:
        from langchain.schema import HumanMessage, AIMessage  # v0系
        ss.chat_history.extend([HumanMessage(content=chat_message), AIMessage(content=answer)])
    except Exception:
        try:
            from langchain_core.messages import HumanMessage, AIMessage  # v1系
            ss.chat_history.extend([HumanMessage(content=chat_message), AIMessage(content=answer)])
        except Exception:
            # フォールバック：プレーンな辞書で保持
            ss.chat_history.append({"role": "user", "content": chat_message})
            ss.chat_history.append({"role": "assistant", "content": answer})

    logger.info({"message": answer})

    return answer

def get_datetime():
    """
    現在日時を取得（日本語フォーマット統一）

    Returns:
        現在日時（日本語フォーマット）
    """
    dt_now = datetime.datetime.now()
    now_datetime = dt_now.strftime('%Y年%m月%d日 %H:%M:%S')
    return now_datetime

def adjust_string(s):
    """
    Windows環境でRAGが正常動作するよう調整
    
    Args:
        s: 調整を行う文字列
    
    Returns:
        調整を行った文字列
    """
    # 調整対象は文字列のみ
    if type(s) is not str:
        return s

    # OSがWindowsの場合、Unicode正規化と、cp932（Windows用の文字コード）で表現できない文字を除去
    if sys.platform.startswith("win"):
        s = unicodedata.normalize('NFC', s)
        s = s.encode("cp932", "ignore").decode("cp932")
        return s
    
    # OSがWindows以外の場合はそのまま返す
    return s

def send_inquiry_to_gmail(chat_message: str) -> str:
    """
    問い合わせメッセージをGmailに転送する（多言語対応）
    
    Args:
        chat_message: ユーザーからの問い合わせメッセージ
        
    Returns:
        送信結果メッセージ
    """
    try:
        # 環境変数から設定を取得
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # アプリパスワードを使用
        to_email = os.getenv("INQUIRY_TO_EMAIL")
        
        # 必要な環境変数がない場合はエラー
        if not all([gmail_user, gmail_password, to_email]):
            return ct.get_text('GMAIL_SETTINGS_ERROR_MESSAGE')
        
        # 現在の言語を取得
        current_lang = getattr(st.session_state, 'language', 'ja')
        
        # メールの作成
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = f"{ct.get_text('CONTACT_FORWARDING_SUBJECT')} - {get_datetime()}"
        
        # メール本文の作成（言語に応じて処理）
        if current_lang == 'en':
            # 英語選択時：英語と日本語の両方でメール内容を作成
            body = ct.get_text('EMAIL_FORMAT_TEMPLATE').format(
                chat_message=chat_message,
                translated_message=translate_to_japanese(chat_message),
                datetime=get_datetime(),
            )
        else:
            # 日本語選択時：従来通り日本語のみ
            body = ct.get_text('EMAIL_FORMAT_TEMPLATE').format(
                chat_message=chat_message,
                datetime=get_datetime()
            )
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Gmail SMTPサーバーに接続して送信
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # TLS暗号化を有効化
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, to_email, text)
        server.quit()
        
        return ct.get_text('CONTACT_THANKS_MESSAGE')
        
    except Exception as e:
        # エラーが発生した場合のログ出力
        error_msg = f"{ct.get_text('GMAIL_SENDING_ERROR_MESSAGE')}: {str(e)}"
        print(error_msg)  # 開発用
        return ct.get_text('GMAIL_SENDING_ERROR_DETAIL_MESSAGE')

def rebuild_rag_chain_for_current_language():
    """
    現在の言語に応じてRAGチェーンを再構築
    """
    if "rag_chain" in st.session_state:
        st.session_state.rag_chain = create_rag_chain(ct.DB_ALL_PATH)

def translate_to_japanese(text: str) -> str:
    """
    英語のテキストを日本語に翻訳する
    
    Args:
        text: 翻訳対象の英語テキスト
        
    Returns:
        日本語に翻訳されたテキスト
    """
    try:
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
        
        # 翻訳用のプロンプトテンプレート
        translation_template = ct.get_text('TRANSLATION_TEMPLATE')
        
        translation_prompt = PromptTemplate(
            input_variables=["english_text"],
            template=translation_template
        )
        
        # LLMチェーンを作成して翻訳実行
        translation_chain = LLMChain(
            llm=st.session_state.llm,
            prompt=translation_prompt
        )
        
        result = translation_chain.run(english_text=text)
        return result.strip()
        
    except Exception as e:
        # 翻訳に失敗した場合は元のテキストを返す
        print(f"Translation error: {str(e)}")
        return f"[翻訳失敗] {text}"


