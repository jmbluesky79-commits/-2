# PRD: 다국어 번역기 (Streamlit + OpenAI)

| 항목 | 내용 |
|---|---|
| 문서 버전 | v1.0 |
| 작성일 | 2026-11-03 |
| 제품명 | 다국어 번역기 (Multi-Language Translator) |
| 플랫폼 | Streamlit 웹 앱 (Python) |
| 번역 엔진 | OpenAI API – `gpt-6-astra` 모델 |

---

## 1. 개요

### 1.1 배경
사용자가 입력한 글을 버튼 한 번으로 영어, 일본어, 베트남어로 빠르게 번역할 수 있는 간단한 웹 도구가 필요하다.

### 1.2 목표
- 텍스트 입력 → 언어 버튼 클릭 → 번역 결과 표시까지 **3단계 이내**로 끝나는 간단한 UX 제공
- OpenAI `gpt-6-astra` 모델을 사용한 자연스러운 번역 품질 확보
- API 키를 `.env` 파일로 관리해 코드에 비밀 정보가 노출되지 않도록 함
- Streamlit 앱으로 만들어 로컬 실행 및 클라우드 배포가 쉬워야 함

### 1.3 범위 밖 (Non-Goals)
- 지원 언어 외 다른 언어로의 번역
- 파일(PDF, Word 등) 업로드 번역
- 사용자 로그인 / 번역 기록 DB 저장
- 음성 입력/출력

---

## 2. 사용자 및 사용 시나리오

### 2.1 대상 사용자
- 한국어(또는 기타 언어) 글을 외국어로 빠르게 번역하고 싶은 일반 사용자
- 해외 고객/동료와 소통이 필요한 직장인, 학생

### 2.2 사용자 스토리
1. 사용자는 텍스트 입력창에 번역할 글을 입력한다.
2. 사용자는 **[영어]**, **[일본어]**, **[베트남어]** 버튼 중 하나를 누른다.
3. 앱은 OpenAI `gpt-6-astra` 모델로 해당 언어 번역을 요청한다.
4. 번역 결과가 화면 아래에 표시되고, 사용자는 결과를 복사해 사용한다.

---

## 3. 기능 요구사항

| ID | 기능 | 설명 | 우선순위 |
|---|---|---|---|
| F-01 | 텍스트 입력 | 여러 줄 입력이 가능한 텍스트 영역(`st.text_area`) 제공 | 필수 |
| F-02 | 언어 버튼 | `영어`, `일본어`, `베트남어` 버튼 3개를 가로로 나란히 배치(`st.columns`) | 필수 |
| F-03 | 번역 실행 | 버튼 클릭 시 입력 텍스트를 선택한 언어로 번역 | 필수 |
| F-04 | 결과 표시 | 번역 결과를 화면에 표시하고, 복사하기 쉽게 `st.code` 또는 텍스트 영역으로 제공 | 필수 |
| F-05 | 로딩 표시 | 번역 중 `st.spinner("번역 중...")` 표시 | 필수 |
| F-06 | 빈 입력 검증 | 입력값이 비어 있으면 API 호출 없이 경고 메시지 표시 | 필수 |
| F-07 | 오류 처리 | API 키 누락, 네트워크 오류, API 오류 시 사용자 친화적인 에러 메시지 표시 | 필수 |
| F-08 | 결과 유지 | `st.session_state`로 마지막 번역 결과와 선택 언어를 유지 | 권장 |

### 3.1 번역 프롬프트 요구사항
- System 프롬프트 예시:
  > "You are a professional translator. Translate the user's text into {target_language}. Output only the translated text without explanations. Preserve line breaks and formatting."
- 대상 언어 매핑:

| 버튼 | target_language |
|---|---|
| 영어 | English |
| 일본어 | Japanese |
| 베트남어 | Vietnamese |

- 번역문만 출력하고 설명, 주석, 따옴표는 붙이지 않는다.
- 원문의 줄바꿈과 문단 구조를 유지한다.

---

## 4. 비기능 요구사항

| 구분 | 요구사항 |
|---|---|
| 보안 | API 키는 `.env` 파일에 저장하고 `python-dotenv`로 불러온다. 코드에 하드코딩 금지. `.env`는 `.gitignore`에 추가 |
| 성능 | 일반 문단(약 500자 이하) 기준 수 초 이내 응답 |
| 사용성 | 별도 설명 없이 바로 사용할 수 있는 단일 페이지 UI |
| 유지보수 | 모델명은 `.env`의 `OPENAI_MODEL`로 바꿀 수 있게 구성 (기본값 `gpt-6-astra`) |
| 호환성 | Python 3.10 이상 |

---

## 5. 기술 사양

### 5.1 기술 스택
- **언어**: Python 3.10+
- **UI 프레임워크**: Streamlit
- **LLM API**: OpenAI Python SDK (`openai`)
- **환경 변수 관리**: `python-dotenv`

### 5.2 프로젝트 구조
```
번역기/
├── app.py              # Streamlit 메인 앱
├── .env                # API 키, 모델명 (Git 커밋 금지)
├── .env.example        # .env 템플릿
├── .gitignore          # .env 등 제외
├── requirements.txt    # 의존성 목록
└── prd.md              # 본 문서
```

### 5.3 환경 변수 (`.env`)
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-6-astra
```

### 5.4 의존성 (`requirements.txt`)
```txt
streamlit
openai
python-dotenv
```

### 5.5 핵심 처리 흐름
```
[사용자 입력] → [언어 버튼 클릭]
      → 빈 입력 검사
      → .env에서 OPENAI_API_KEY / OPENAI_MODEL 로드
      → OpenAI API 호출 (model = gpt-6-astra)
      → 응답 텍스트 추출
      → 화면에 번역 결과 표시
```

### 5.6 API 호출 예시 (참고용)
```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-6-astra")

def translate(text: str, target_language: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                f"You are a professional translator. Translate the user's text into {target_language}. "
                "Output only the translated text without explanations. Preserve line breaks and formatting."
            )},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()
```

> 참고: 모델 이름은 OpenAI 계정에서 실제로 쓸 수 있는 정확한 모델 ID와 같아야 한다 (대소문자 구분: `GPT-6-Astra`는 404, `gpt-6-astra`가 정확한 ID). 다르면 `.env`의 `OPENAI_MODEL` 값만 고치면 된다.

---

## 6. UI 구성

```
┌──────────────────────────────────────────┐
│  🌐 다국어 번역기                          │
│                                          │
│  번역할 글을 입력하세요                    │
│  ┌────────────────────────────────────┐  │
│  │                                    │  │
│  │                                    │  │
│  └────────────────────────────────────┘  │
│                                          │
│  [영어·English] [일본어·日本語] [베트남어·Tiếng Việt] │
│                                          │
│  ── 번역 결과 (영어) ──                    │
│  ┌────────────────────────────────────┐  │
│  │ Translated text...                 │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## 7. 실행 및 배포

### 7.1 로컬 실행 명령어 (Windows PowerShell)
```powershell
# 1. 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. 의존성 설치
pip install -r requirements.txt

# 3. .env 파일 작성 (.env.example 복사 후 키 입력)
copy .env.example .env

# 4. 앱 실행
streamlit run app.py
```
실행 후 브라우저에서 `http://localhost:8501` 접속

### 7.2 서버 배포 명령어 (외부 접속 허용)
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```
백그라운드 실행 (Linux 서버):
```bash
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
```

### 7.3 Streamlit Community Cloud 배포
1. 프로젝트를 GitHub 저장소에 push한다 (`.env`는 제외).
2. https://share.streamlit.io 에서 저장소와 `app.py`를 선택해 배포한다.
3. **App settings → Secrets**에 다음을 등록한다:
   ```toml
   OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxx"
   OPENAI_MODEL = "gpt-6-astra"
   ```
4. 코드에서는 `.env`가 없을 때 `st.secrets`에서 값을 읽도록 처리한다:
   ```python
   api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
   ```

### 7.4 `.gitignore`
```gitignore
.env
venv/
__pycache__/
.streamlit/secrets.toml
```

---

## 8. 예외 처리 정책

| 상황 | 동작 |
|---|---|
| 입력 텍스트 없음 | `st.warning("번역할 글을 입력해주세요.")` |
| API 키 없음 | `st.error("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")` |
| 모델명 오류 / 권한 없음 | `st.error("모델을 사용할 수 없습니다. OPENAI_MODEL 값을 확인해주세요.")` |
| 네트워크/API 오류 | `st.error(f"번역 중 오류가 발생했습니다: {에러 메시지}")` |
| 요청 한도 초과 (429) | `st.error("요청이 많습니다. 잠시 후 다시 시도해주세요.")` |

---

## 9. 완료 기준 (Acceptance Criteria)

- [ ] 텍스트를 입력하고 `영어` 버튼을 누르면 영어 번역문이 표시된다.
- [ ] `일본어`, `베트남어` 버튼도 각각 올바른 언어로 번역된다.
- [ ] 빈 입력일 때 API를 호출하지 않고 경고가 표시된다.
- [ ] API 키는 `.env`(로컬) 또는 Streamlit Secrets(클라우드)에서만 읽고, 코드에 하드코딩되지 않는다.
- [ ] 사용 모델은 `gpt-6-astra`이며, `.env`에서 바꿀 수 있다.
- [ ] `streamlit run app.py` 명령으로 로컬에서 정상 실행된다.
- [ ] Streamlit Community Cloud 또는 서버 환경에 배포해 외부에서 접속할 수 있다.

---

## 10. 향후 확장 (Optional)
- 지원 언어 추가 (중국어, 스페인어 등)
- 원문 언어 자동 감지 표시
- 번역 결과 복사 버튼 / 다운로드(.txt)
- 번역 기록(세션 내 히스토리) 표시
- 존댓말/반말, 격식체 등 번역 톤 선택 옵션
