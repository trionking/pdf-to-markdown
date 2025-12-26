# PDF to Markdown Converter

PDF 파일을 Markdown으로 변환하고 번역하는 GUI 도구

## 버전

| 파일 | 모델 | 처리 방식 | 라이브러리 | 비용 |
|------|------|-----------|------------|------|
| `pdf_to_markdown_gui.py` | - | 순차 | deep-translator | 무료 |
| `pdf_to_markdown_glm.py` | glm-4-plus | 순차 스트리밍 | zhipuai | $0.60~$2.20/1M |
| `pdf_to_markdown_glm_flash.py` | glm-4-flash | **병렬 (4개 동시)** | httpx | **$0.01/1M** |

### 추천: `pdf_to_markdown_glm_flash.py`

- **100배 이상 빠른 처리 속도** (병렬 처리 + 빠른 모델)
- **60~200배 저렴한 비용** ($0.01/1M tokens)
- 가벼운 httpx 라이브러리 사용

## 설치

```bash
# 기본 (무료 버전)
pip install pymupdf4llm deep-translator

# GLM 오류 수정 버전 (선택)
pip install httpx          # glm_flash 버전용 (추천)
pip install zhipuai         # glm 버전용
```

## 사용법

```bash
# 추천 (빠르고 저렴)
python pdf_to_markdown_glm_flash.py

# 기존 버전
python pdf_to_markdown_glm.py
python pdf_to_markdown_gui.py
```

## 기능

- PDF → Markdown 변환
- MD 파일 번역 (Google Translate, 무료)
- 마크다운 오류 자동 수정 (GLM API)
  - 깨진 표 수정
  - 잘못된 문자 수정
  - 페이지 번호 제거

## 성능 비교

| 항목 | glm.py (기존) | glm_flash.py (신규) |
|------|---------------|---------------------|
| 모델 | glm-4-plus | glm-4-flash |
| 처리 방식 | 순차 스트리밍 | 병렬 처리 (4개 동시) |
| 속도 | 느림 | **100배+ 빠름** |
| 비용 | $0.60~$2.20/1M | **$0.01/1M** |
| 라이브러리 | zhipuai (무거움) | httpx (가벼움) |

## API Key

GLM API Key는 https://open.bigmodel.cn 에서 발급

설정 파일 위치: `~/.pdf_to_markdown_config.json`
