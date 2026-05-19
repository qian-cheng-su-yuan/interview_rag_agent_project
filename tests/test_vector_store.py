from pathlib import Path

from app.services.text_splitter import TextChunk
from app.services.vector_store import LocalVectorStore


def test_vector_store_search(tmp_path: Path):
    store = LocalVectorStore(tmp_path / "chunks.json")
    store.build(
        [
            TextChunk(chunk_id="1", source="policy.txt", content="员工报销需要发票和付款凭证。"),
            TextChunk(chunk_id="2", source="leave.txt", content="请假需要提前提交申请。"),
        ]
    )
    results = store.search("报销材料", top_k=1)
    assert results
    assert results[0]["source"] == "policy.txt"
