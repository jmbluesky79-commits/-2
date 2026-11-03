# 다국어 번역기 단계별 개발 프롬프트

> 기준 문서: `prd.md`
> 사용법: 단계마다 아래 프롬프트를 그대로 복사해서 Claude Code에 입력하세요. 한 단계가 끝나고 결과를 확인한 뒤 다음 단계로 넘어갑니다.

---

## 1단계: 기본 뼈대 작성

```
prd.md를 읽고, 다국어 번역기 Streamlit 앱의 기본 뼈대를 만들어줘.

[만들 파일]
1. requirements.txt
   - streamlit, openai, python-dotenv
2. .env.example
   - OPENAI_API_KEY=your-api-key-here
   - OPENAI_MODEL=gpt-6-astra
3. .gitignore
   - .env, venv/, __pycache__/, .streamlit/secrets.toml
4. app.py (뼈대만)
   - st.set_page_config(page_title="다국어 번역기", page_icon="🌐", layout="centered")
   - 제목과 간단한 설명
   - st.text_area 입력창 (key="source_text")
   - st.columns(3)으로 [영어] [일본어] [베트남어] 버튼 3개 배치
   - 번역 결과 영역 자리만 만들어 두기
   - 아직 OpenAI API는 호출하지 말고, 버튼을 누르면 "선택한 언어: 영어"처럼 어떤 버튼을 눌렀는지만 표시

[코드 구조]
- 나중에 기능을 붙이기 쉽게 함수를 나눠줘:
  - load_config(): 설정값 불러오기 (지금은 빈 함수여도 됨)
  - translate(text, target_language): 번역 함수 (지금은 "TODO" 문자열 반환)
  - render_ui(): 화면 구성
  - main()
- 언어 매핑은 상수 딕셔너리로 정의:
  LANGUAGES = {"영어": "English", "일본어": "Japanese", "베트남어": "Vietnamese"}

[완료 확인]
- 가상환경을 만들고 pip install -r requirements.txt 실행
- streamlit run app.py 가 에러 없이 실행되는지 확인
- 만든 파일 목록과 실행 방법을 알려줘
```

---

## 2단계: 주요 기능 추가

```
prd.md의 "3. 기능 요구사항", "5. 기술 사양", "8. 예외 처리 정책"에 맞춰
app.py에 실제 번역 기능을 넣어줘.

[설정 불러오기 - load_config()]
- python-dotenv의 load_dotenv()로 .env를 읽기
- OPENAI_API_KEY: os.getenv → 없으면 st.secrets에서 읽기
  (st.secrets 파일이 없을 때 나는 예외도 try/except로 처리)
- OPENAI_MODEL: 같은 방식, 기본값 "gpt-6-astra"
- API 키가 없으면 st.error로 PRD 8장의 문구를 띄우고 st.stop()

[번역 함수 - translate(text, target_language)]
- openai 패키지의 OpenAI 클라이언트로 chat.completions.create 호출
- model은 OPENAI_MODEL 값 사용 (하드코딩 금지)
- system 프롬프트는 PRD 3.1의 문구 그대로 사용
- 응답 텍스트의 앞뒤 공백 제거 후 반환
- OpenAI 클라이언트는 @st.cache_resource로 한 번만 생성

[버튼 동작]
- 입력이 비었거나 공백뿐이면 API를 호출하지 않고 st.warning("번역할 글을 입력해주세요.")
- 번역하는 동안 st.spinner("번역 중...") 표시
- 결과와 선택한 언어를 st.session_state에 저장해서 다시 그려져도 결과가 남게 하기
- 결과 제목은 "번역 결과 (영어)"처럼 언어 이름 포함

[예외 처리 - PRD 8장 표대로]
- openai.AuthenticationError → API 키 오류 메시지
- openai.NotFoundError, openai.PermissionDeniedError → "모델을 사용할 수 없습니다. OPENAI_MODEL 값을 확인해주세요."
- openai.RateLimitError → "요청이 많습니다. 잠시 후 다시 시도해주세요."
- openai.APIConnectionError, 그 밖의 openai.APIError → "번역 중 오류가 발생했습니다: {에러 메시지}"
- 에러가 나도 앱이 멈추지 않아야 함

[완료 확인]
- python -m py_compile app.py 로 문법 검사
- .env가 없을 때 API 키 에러 메시지가 제대로 뜨는지 확인
- 바뀐 부분을 요약해줘
```

---

## 3단계: UI 디자인

```
prd.md "6. UI 구성"을 바탕으로 번역기 화면을 깔끔하고 보기 좋게 다듬어줘.
기능 코드(translate, load_config, 예외 처리)는 바꾸지 말고 화면만 손봐줘.

[레이아웃]
- 상단: 🌐 아이콘과 제목 "다국어 번역기", 그 아래 한 줄 설명
- 입력창: 높이 200px 정도, placeholder "번역할 글을 입력하세요..."
- 입력창 아래에 글자 수 표시 (예: "123자")
- 버튼 3개: 언어 이름 병기 (영어 · English / 일본어 · 日本語 / 베트남어 · Tiếng Việt), use_container_width=True로 폭을 똑같이
- 결과 영역: 카드 느낌의 박스 안에 번역문 표시
  - 복사하기 쉽게 st.code(result, language=None) 사용 (오른쪽 위 복사 아이콘)
  - 결과가 없을 때는 "언어 버튼을 누르면 여기에 번역 결과가 나타납니다." 안내문

[스타일]
- st.markdown(..., unsafe_allow_html=True)로 최소한의 CSS만 넣기
  - 버튼 둥근 모서리, 마우스를 올리면 색이 살짝 바뀌는 효과
  - 결과 카드 둥근 모서리, 옅은 테두리, 안쪽 여백
- 라이트/다크 테마 둘 다에서 글자가 잘 보이게 할 것 (고정 배경색 대신 Streamlit 테마 변수나 반투명 색 사용)
- .streamlit/config.toml에 주 색상(primaryColor) 설정

[반응형]
- 모바일 폭(약 390px)에서도 버튼과 입력창이 깨지지 않게

[사이드바 (선택)]
- 사용 방법 3줄 안내
- 현재 사용 모델 이름 표시 (API 키는 절대 표시하지 말 것)

[완료 확인]
- streamlit run app.py 로 실행해서 화면이 정상적으로 뜨는지 확인
- 바뀐 디자인 요소를 요약해줘
```

---

## 4단계: PRD 기준 검토 및 버그 점검 (Playwright 활용)

```
지금까지 만든 번역기 앱이 prd.md대로 개발됐는지, 버그는 없는지 자세히 검토해줘.
코드 검토와 Playwright 브라우저 테스트를 함께 해줘.

[준비]
1. streamlit run app.py --server.port 8501 --server.headless true 를 백그라운드로 실행
2. Playwright로 http://localhost:8501 에 접속
   (Streamlit은 화면을 늦게 그리므로, 요소가 나타날 때까지 기다린 뒤 테스트)

[A. 코드 검토 - prd.md와 하나씩 비교]
- 3장 기능 요구사항 F-01 ~ F-08이 모두 구현됐는지
- 3.1 번역 프롬프트와 언어 매핑이 PRD와 같은지
- 4장 비기능 요구사항: API 키 하드코딩 여부, .gitignore에 .env 포함 여부, 모델명을 .env에서 바꿀 수 있는지
- 5.2 프로젝트 구조대로 파일이 다 있는지
- 7.3 st.secrets 대체 처리 여부
- 8장 예외 처리 표의 모든 상황이 처리되는지

[B. Playwright 브라우저 테스트]
각 테스트마다 스크린샷을 찍고, 통과/실패를 기록해줘.
1. 첫 화면: 제목, 입력창, 버튼 3개가 보이는지
2. 빈 입력으로 [영어] 클릭 → 경고 메시지가 뜨고 API를 호출하지 않는지
3. 공백만 입력하고 클릭 → 2번과 같은지
4. "안녕하세요. 오늘 날씨가 좋네요." 입력 후
   - [영어] → 영어 번역이 나오는지
   - [일본어] → 일본어(히라가나/가타카나/한자)가 나오는지
   - [베트남어] → 베트남어(성조 표시가 있는 라틴 문자)가 나오는지
   - 결과 제목에 언어 이름이 맞게 나오는지
5. 여러 줄 입력 → 결과에도 줄바꿈이 유지되는지
6. 번역 후 입력창을 바꿔도(다시 그려져도) 이전 결과가 남는지
7. 번역 중 로딩 표시가 나오는지
8. 긴 글(약 1,000자) 번역이 잘 되는지
9. 특수문자, 이모지, 코드 조각이 섞인 글
10. 모바일 폭(390x844)과 데스크톱 폭(1280x800)에서 화면이 깨지지 않는지
11. 다크 모드에서 글자가 잘 보이는지
12. 브라우저 콘솔에 에러가 없는지

[C. 오류 상황 테스트]
- .env를 잠시 이름을 바꿔 API 키가 없는 상태로 실행 → 에러 메시지 확인 (테스트 후 꼭 원래대로 되돌리기)
- OPENAI_MODEL을 없는 모델명으로 바꿔 실행 → 모델 오류 메시지 확인 (테스트 후 원래대로)
- 에러 메시지에 API 키가 노출되지 않는지 확인

[D. 결과 보고]
아래 형식으로 정리해줘:
1. PRD 요구사항 체크표 (ID | 요구사항 | 결과 ✅/❌ | 근거)
2. PRD 9장 완료 기준 체크리스트 결과
3. 발견한 버그 목록 (심각도 높음/중간/낮음 | 재현 방법 | 원인 | 수정 방안)
4. 개선 제안 (선택)

발견한 버그는 바로 고치지 말고 먼저 목록으로 보여줘. 내가 확인한 뒤 수정을 요청할게.
테스트가 끝나면 Streamlit 서버를 종료하고, .env 등 바꾼 파일이 원래대로인지 확인해줘.
```

---

## 진행 팁
- 단계마다 `streamlit run app.py`로 직접 확인한 뒤 다음 단계로 넘어가세요.
- 4단계는 실제 API를 호출하므로 `.env`에 쓸 수 있는 API 키가 있어야 하고, 사용량(비용)이 조금 발생합니다.
- 4단계에서 버그가 나오면 "D-3의 버그 1, 2번을 수정하고 해당 Playwright 테스트를 다시 돌려줘"처럼 이어서 요청하세요.
