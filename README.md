# 企业知识库 AI Agent 问答系统

> 面向 AI Agent 开发 / 大模型应用开发 / RAG 应用开发 / AI 应用后端岗位的本地可演示项目。

本项目采用企业项目中常见的“后端 API + 前端演示页 + 服务层 + 配置层 + 数据存储层”结构，支持上传企业资料，自动切分文本、构建向量索引，并通过 RAG 流程完成知识库问答、参考片段展示、文档总结、关键词提取和问答日志记录。

## 1. 项目亮点

- **结构企业化**：按 `api / core / schemas / services / utils` 分层，便于维护和面试讲解。
- **RAG 完整链路**：文档读取 → 文本清洗 → 分段切片 → 向量检索 → Prompt 拼接 → 大模型回答。
- **可无 Key 演示**：没有配置大模型 API Key 时，会使用本地检索片段生成兜底回答，方便面试现场演示。
- **支持 OpenAI 兼容接口**：可接入 DeepSeek、Qwen、阿里云百炼等兼容 Chat Completions 的接口。
- **前后端分离**：FastAPI 提供接口，Streamlit 作为本地演示页面。
- **工程化配置**：使用 `.env` 管理模型地址、模型名称、日志路径等参数。
- **Agent 工具能力**：包含文档总结、关键词提取、问答日志查看等简单工具能力。

## 2. 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端接口 | FastAPI、Uvicorn、Pydantic |
| 前端演示 | Streamlit、Requests |
| RAG 检索 | scikit-learn TF-IDF 向量化、余弦相似度 |
| 文档处理 | TXT、MD、PDF，pypdf |
| 大模型调用 | OpenAI-compatible Chat Completions |
| 配置管理 | python-dotenv |
| 开发工具 | PyCharm |

说明：为了方便本地快速运行，本项目默认使用轻量级 TF-IDF 向量检索。面试时可以说明：生产环境可替换为 Chroma、FAISS、Milvus、Elasticsearch 或企业内部向量数据库。

## 3. 项目结构

```text
interview_rag_agent_project/
├── app/
│   ├── api/v1/routes.py             # API 路由层
│   ├── core/config.py               # 配置管理
│   ├── core/logger.py               # 日志配置
│   ├── schemas/                     # 请求/响应模型
│   ├── services/                    # 核心业务逻辑
│   │   ├── document_loader.py        # 文档读取
│   │   ├── text_splitter.py          # 文本切分
│   │   ├── vector_store.py           # 向量检索
│   │   ├── llm_client.py             # 大模型调用
│   │   ├── rag_service.py            # RAG 主流程
│   │   └── agent_tools.py            # Agent 工具能力
│   ├── utils/file_utils.py           # 文件工具
│   └── main.py                       # FastAPI 入口
├── web/streamlit_app.py              # Streamlit 前端页面
├── data/knowledge_base/              # 示例知识库文件
├── data/uploads/                     # 用户上传文件目录
├── storage/                          # 索引和日志目录
├── docs/                             # 项目说明文档
├── tests/                            # 简单单元测试
├── .env.example                      # 环境变量模板
├── requirements.txt                  # 依赖清单
├── run_api.py                        # 启动后端
└── run_web.py                        # 启动前端
```

## 4. PyCharm 运行步骤

### 第一步：打开项目

用 PyCharm 打开 `interview_rag_agent_project` 文件夹。

### 第二步：创建虚拟环境

PyCharm 一般会自动提示创建虚拟环境。也可以在终端执行：

```bash
python -m venv .venv
```

Windows 激活：

```bash
.venv\Scripts\activate
```

### 第三步：安装依赖

国内网络建议使用镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 第四步：复制配置文件

```bash
copy .env.example .env
```

没有 API Key 也能运行；有 Key 时修改 `.env`：

```env
LLM_API_KEY=你的API_KEY
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus
```

### 第五步：启动后端

```bash
python run_api.py
```

浏览器打开：

```text
http://127.0.0.1:8000/docs
```

### 第六步：启动前端

新开一个终端：

```bash
python run_web.py
```

浏览器打开 Streamlit 页面后，可以上传文档并开始问答。


## 5. 项目流程
用户
 ↓
Streamlit 前端
 ↓
FastAPI 后端接口
 ↓
RAGService 核心流程
 ↓
文档读取 → 文本切分 → 本地索引 → 相似度检索
 ↓
Prompt 组装
 ↓
大模型 API
 ↓
回答 + 参考片段 + 日志
