# PyCharm 小白运行指南

## 1. 打开项目

打开 PyCharm，选择 `Open`，选中 `interview_rag_agent_project` 文件夹。

## 2. 配置解释器

如果 PyCharm 提示创建虚拟环境，选择 Python 3.10 或 Python 3.11 即可。

如果没有提示：

1. 点击 `File`。
2. 点击 `Settings`。
3. 找到 `Project: interview_rag_agent_project`。
4. 点击 `Python Interpreter`。
5. 选择或创建 `.venv` 虚拟环境。

## 3. 安装依赖

在 PyCharm 底部打开 `Terminal`，执行：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 4. 创建配置文件

Windows CMD：

```bash
copy .env.example .env
```

PowerShell：

```powershell
Copy-Item .env.example .env
```

## 5. 启动后端

运行：

```bash
python run_api.py
```

看到类似下面内容说明成功：

```text
Uvicorn running on http://127.0.0.1:8000
```

## 6. 启动前端

新开一个 Terminal，运行：

```bash
python run_web.py
```

浏览器会自动打开 Streamlit 页面。

## 7. 第一次演示

1. 点击侧边栏的“重建知识库索引”。
2. 在问题框输入：`员工报销需要准备哪些材料？`
3. 点击“提交问题”。
4. 查看回答和参考片段。

## 8. 常见问题

### 后端连接失败

先确认 `python run_api.py` 没有关掉。

### ModuleNotFoundError

说明依赖没有装完整，重新执行：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 没有自然语言大模型回答

需要在 `.env` 中配置：

```env
LLM_API_KEY=你的Key
LLM_BASE_URL=你的模型服务地址
LLM_MODEL_NAME=你的模型名称
```

不配置也能演示检索流程，只是回答会使用本地兜底模式。
