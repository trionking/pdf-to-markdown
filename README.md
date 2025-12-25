# PDF to Markdown Converter

PDF 파일을 Markdown으로 변환하고 번역하는 GUI 도구

## 버전

| 파일 | 번역 | 오류 수정 | 비용 |
|------|------|-----------|------|
| `pdf_to_markdown_gui.py` | Google Translate | - | 무료 |
| `pdf_to_markdown_glm.py` | Google Translate | GLM-4 API | 유료 (저렴) |

## 설치

```bash
pip install pymupdf4llm deep-translator zhipuai
```

## 사용법

```bash
python pdf_to_markdown_glm.py
```

## 기능

- PDF → Markdown 변환
- MD 파일 번역 (Google Translate)
- 마크다운 오류 자동 수정 (GLM API)
  - 깨진 표 수정
  - 잘못된 문자 수정
  - 페이지 번호 제거

## API Key

GLM API Key는 https://open.bigmodel.cn 에서 발급

설정 파일 위치: `~/.pdf_to_markdown_config.json`
