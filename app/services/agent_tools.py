import re
from collections import Counter
from typing import List

from app.services.llm_client import LLMClient


class AgentTools:
    """Small tools that can be presented as Agent capabilities."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def summarize(self, text: str) -> str:
        messages = [
            {"role": "system", "content": "你是企业知识库助手，请用简洁、准确的方式总结文档。"},
            {"role": "user", "content": f"请总结下面这段内容，输出 3-5 条要点：\n\n{text[:4000]}"},
        ]
        answer, _ = self.llm_client.chat(messages)
        return answer

    def extract_keywords(self, text: str, limit: int = 10) -> List[str]:
        tokens = re.findall(r"[\u4e00-\u9fa5]{2,}|[A-Za-z][A-Za-z0-9_\-]{2,}", text)
        stop_words = {"可以", "进行", "需要", "如果", "一个", "以及", "通过", "系统", "用户", "文档"}
        counter = Counter(token for token in tokens if token not in stop_words)
        return [word for word, _ in counter.most_common(limit)]
