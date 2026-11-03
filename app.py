import os
from pathlib import Path

import openai
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

ENV_PATH = Path(__file__).resolve().parent / ".env"
LANGUAGES = {"영어": "English", "일본어": "Japanese", "베트남어": "Vietnamese"}
DEFAULT_MODEL = "gpt-6-astra"
SYSTEM_PROMPT = (
    "You are a professional translator. Translate the user's text into {target_language}. "
    "Output only the translated text without explanations. Preserve line breaks and formatting."
)


def _get_setting(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value:
        return value.strip()
    try:
        value = st.secrets.get(name)
    except Exception:  # secrets.toml 없음 등
        value = None
    return value.strip() if isinstance(value, str) and value.strip() else default


def load_config() -> dict:
    load_dotenv(ENV_PATH)
    api_key = _get_setting("OPENAI_API_KEY")
    model = _get_setting("OPENAI_MODEL", DEFAULT_MODEL)
    if not api_key:
        st.error("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        st.stop()
    return {"api_key": api_key, "model": model}


@st.cache_resource
def get_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key, timeout=60, max_retries=2)


def translate(text: str, target_language: str, config: dict) -> str:
    client = get_client(config["api_key"])
    response = client.chat.completions.create(
        model=config["model"],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(target_language=target_language)},
            {"role": "user", "content": text},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def run_translation(label: str, config: dict) -> None:
    text = st.session_state.get("source_text", "")
    if not text.strip():
        st.warning("번역할 글을 입력해주세요.")
        return
    try:
        with st.spinner("번역 중..."):
            result = translate(text, LANGUAGES[label], config)
    except openai.AuthenticationError:
        st.error("API 키가 올바르지 않습니다. .env 파일의 OPENAI_API_KEY를 확인해주세요.")
    except (openai.NotFoundError, openai.PermissionDeniedError):
        st.error("모델을 사용할 수 없습니다. OPENAI_MODEL 값을 확인해주세요.")
    except openai.RateLimitError:
        st.error("요청이 많습니다. 잠시 후 다시 시도해주세요.")
    except openai.APIConnectionError:
        st.error("번역 중 오류가 발생했습니다: 네트워크에 연결할 수 없습니다.")
    except openai.APIError as e:
        st.error(f"번역 중 오류가 발생했습니다: {e.message}")
    except Exception as e:  # 예상하지 못한 오류도 앱이 멈추지 않게 처리
        st.error(f"번역 중 알 수 없는 오류가 발생했습니다. ({type(e).__name__})")
    else:
        if not result:
            st.warning("번역 결과가 비어 있습니다. 잠시 후 다시 시도해주세요.")
            return
        st.session_state["result"] = result
        st.session_state["result_lang"] = label


# 국기 이모지는 Windows에서 "US/JP/VN" 글자로 보이므로 각 언어 이름을 함께 표기
LANG_BUTTONS = {"영어": "영어 · English", "일본어": "일본어 · 日本語", "베트남어": "베트남어 · Tiếng Việt"}

CUSTOM_CSS = """
<style>
h1, [data-testid="stCaptionContainer"] { word-break: keep-all; }
div.stButton > button {
    border-radius: 12px;
    padding: 0.6rem 0.5rem;
    font-weight: 600;
    transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
}
div.stButton > button:hover {
    border-color: var(--primary-color, #4F6BED);
    background-color: rgba(79, 107, 237, 0.10);
}
div.stButton > button:active { transform: scale(0.98); }
.char-count { text-align: right; font-size: 0.85rem; opacity: 0.65; margin-top: -0.5rem; }
.empty-result {
    border: 1px dashed rgba(128, 128, 128, 0.45);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    opacity: 0.75;
}
</style>
"""


def render_sidebar(config: dict) -> None:
    with st.sidebar:
        st.header("사용 방법")
        st.markdown(
            "1. 번역할 글을 입력합니다.\n"
            "2. 원하는 언어 버튼을 누릅니다.\n"
            "3. 결과 오른쪽 위 아이콘으로 복사합니다."
        )
        st.divider()
        st.caption(f"사용 모델: `{config['model']}`")


def render_ui(config: dict) -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    render_sidebar(config)

    st.title("🌐 다국어 번역기")
    st.caption("글을 입력하고 언어 버튼을 누르면 영어 · 일본어 · 베트남어로 번역해 드립니다.")

    text = st.text_area(
        "번역할 글",
        key="source_text",
        height=200,
        placeholder="번역할 글을 입력하세요...",
        label_visibility="collapsed",
    )
    st.markdown(f'<div class="char-count">{len(text)}자</div>', unsafe_allow_html=True)

    clicked = None
    cols = st.columns(3)
    for col, (label, button_text) in zip(cols, LANG_BUTTONS.items()):
        if col.button(button_text, key=f"btn_{label}", use_container_width=True):
            clicked = label

    if clicked:
        run_translation(clicked, config)

    with st.container(border=True):
        if st.session_state.get("result"):
            lang = st.session_state["result_lang"]
            st.markdown(f"**번역 결과 ({LANG_BUTTONS[lang]})**")
            st.code(st.session_state["result"], language=None, wrap_lines=True)
        else:
            st.markdown(
                '<div class="empty-result">언어 버튼을 누르면 여기에 번역 결과가 나타납니다.</div>',
                unsafe_allow_html=True,
            )


def main():
    st.set_page_config(page_title="다국어 번역기", page_icon="🌐", layout="centered")
    config = load_config()
    render_ui(config)


if __name__ == "__main__":
    main()
