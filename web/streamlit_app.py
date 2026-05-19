import requests
import streamlit as st

API_BASE_URL = st.sidebar.text_input("后端地址", value="http://127.0.0.1:8000")

st.set_page_config(page_title="企业知识库 AI Agent", page_icon="🤖", layout="wide")
st.title("企业知识库 AI Agent 问答系统")
st.caption("FastAPI + Streamlit + RAG + OpenAI-compatible LLM")


def api_post(path: str, **kwargs):
    url = f"{API_BASE_URL}{path}"
    response = requests.post(url, timeout=120, **kwargs)
    response.raise_for_status()
    return response.json()


def api_get(path: str, **kwargs):
    url = f"{API_BASE_URL}{path}"
    response = requests.get(url, timeout=30, **kwargs)
    response.raise_for_status()
    return response.json()


with st.sidebar:
    st.header("操作面板")
    if st.button("检测后端状态"):
        try:
            data = api_get("/health")
            st.success(f"后端正常：{data['status']}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"后端连接失败：{exc}")

    if st.button("重建知识库索引"):
        try:
            data = api_post("/api/v1/documents/rebuild")
            st.success(f"已重建：{data['file_count']} 个文件，{data['chunk_count']} 个片段")
        except Exception as exc:  # noqa: BLE001
            st.error(f"重建失败：{exc}")

    st.divider()
    uploaded_file = st.file_uploader("上传企业资料", type=["txt", "md", "pdf"])
    if uploaded_file and st.button("上传并建立索引"):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            data = api_post("/api/v1/documents/upload", files=files)
            st.success(f"上传成功：{data['filename']}，切分 {data['chunk_count']} 个片段")
        except Exception as exc:  # noqa: BLE001
            st.error(f"上传失败：{exc}")

left, right = st.columns([2, 1])

with left:
    st.subheader("知识库问答")
    examples = [
        "员工报销需要准备哪些材料？",
        "请假流程是什么？",
        "新员工入职需要完成哪些事项？",
        "资料中没有提到的内容应该怎么回答？",
    ]
    selected = st.selectbox("示例问题", ["自定义"] + examples)
    default_question = "" if selected == "自定义" else selected
    question = st.text_area("请输入问题", value=default_question, height=100)
    top_k = st.slider("检索片段数量", min_value=1, max_value=8, value=4)

    if st.button("提交问题", type="primary"):
        if not question.strip():
            st.warning("请先输入问题。")
        else:
            try:
                data = api_post("/api/v1/qa/ask", json={"question": question, "top_k": top_k})
                st.markdown("### 回答")
                st.write(data["answer"])
                st.info(f"耗时：{data['elapsed_ms']} ms｜是否调用大模型：{data['used_llm']}")

                st.markdown("### 参考片段")
                for item in data["sources"]:
                    with st.expander(f"{item['source']}｜相似度 {item['score']}"):
                        st.write(item["content"])
            except Exception as exc:  # noqa: BLE001
                st.error(f"请求失败：{exc}")
                st.caption("请确认已经运行：python run_api.py")

with right:
    st.subheader("Agent 工具")
    tool_text = st.text_area("输入一段文本，用于总结或提取关键词", height=160)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("文档总结"):
            if not tool_text.strip():
                st.warning("请输入文本。")
            else:
                try:
                    data = api_post("/api/v1/tools/summarize", json={"text": tool_text})
                    st.write(data["summary"])
                except Exception as exc:  # noqa: BLE001
                    st.error(f"总结失败：{exc}")
    with col2:
        if st.button("关键词"):
            if not tool_text.strip():
                st.warning("请输入文本。")
            else:
                try:
                    data = api_post("/api/v1/tools/keywords", json={"text": tool_text})
                    st.write("、".join(data["keywords"]))
                except Exception as exc:  # noqa: BLE001
                    st.error(f"提取失败：{exc}")

st.divider()
st.subheader("最近问答日志")
try:
    logs = api_get("/api/v1/logs/recent", params={"limit": 5})
    if not logs:
        st.caption("暂无日志。")
    for item in logs:
        with st.expander(f"{item['created_at']}｜{item['question']}"):
            st.write(item["answer"])
            st.caption(f"耗时：{item['elapsed_ms']} ms")
except Exception:
    st.caption("后端未启动时不显示日志。")
