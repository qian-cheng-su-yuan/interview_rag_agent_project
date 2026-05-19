from app.services.text_splitter import TextSplitter


def test_splitter_creates_chunks():
    splitter = TextSplitter(chunk_size=20, chunk_overlap=5)
    chunks = splitter.split("这是一个用于测试文本切分功能的长句子。" * 5, source="demo.txt")
    assert len(chunks) > 1
    assert chunks[0].source == "demo.txt"
