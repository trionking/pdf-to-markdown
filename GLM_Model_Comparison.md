# GLM-4-Plus vs GLM-4-Flash 비교

## 모델 비교표

| 항목 | GLM-4-Plus | GLM-4-Flash |
|------|------------|-------------|
| **포지션** | 최고 성능 플래그십 | 극속 저가형 |
| **입력 가격** | ¥50/1M tokens (~$7/1M) | ¥0.1/1M tokens (~$0.01/1M) |
| **출력 가격** | ¥50/1M tokens (~$7/1M) | ¥0.1/1M tokens (~$0.01/1M) |
| **가격 차이** | 기준 | **500배 저렴** |
| **컨텍스트** | 128K tokens | 128K tokens |
| **출력 속도** | ~30 token/s | ~72 token/s (**2.4배 빠름**) |
| **성능** | 최고 품질 | 약간 낮음 (실용적 수준) |
| **추천 용도** | 고품질 요구 작업 | 대량 처리, 비용 절감 |
| **무료 여부** | 유료 | **무료** (2024년부터) |

## 실제 비용 예시 (100페이지 PDF 처리)

| 모델 | 예상 토큰 | 비용 |
|------|-----------|------|
| GLM-4-Plus | ~500K | **~$3.50** |
| GLM-4-Flash | ~500K | **~$0.005** (거의 무료) |

## 권장 사항

| 상황 | 추천 모델 |
|------|-----------|
| 최고 품질 번역/수정 필요 | GLM-4-Plus |
| 대량 문서 처리 | **GLM-4-Flash** |
| 비용 절감 우선 | **GLM-4-Flash** |
| 빠른 처리 속도 필요 | **GLM-4-Flash** |

## 결론

마크다운 오류 수정 같은 작업은 GLM-4-Flash로 충분하며, 비용이 500배 저렴하고 속도도 2배 이상 빠릅니다.

## 참고

- [ZHIPU AI Pricing](https://open.bigmodel.cn/pricing)
- [GLM-4 Documentation](https://docs.bigmodel.cn/cn/guide/models/text/glm-4)
- [GLM-4-Plus Guide](https://bigmodel.cn/dev/howuse/glm-4)
