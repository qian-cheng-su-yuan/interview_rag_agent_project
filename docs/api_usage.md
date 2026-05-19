# API 使用说明

启动后端：

```bash
python run_api.py
```

接口文档地址：

```text
http://127.0.0.1:8000/docs
```

## 1. 健康检查

```bash
curl http://127.0.0.1:8000/health
```

## 2. 重建知识库

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/rebuild
```

## 3. 提问

```bash
curl -X POST http://127.0.0.1:8000/api/v1/qa/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"员工报销需要准备哪些材料？\",\"top_k\":4}"
```

## 4. 文档总结

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tools/summarize ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"这里放需要总结的文本\"}"
```

## 5. 关键词提取

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tools/keywords ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"这里放需要提取关键词的文本\"}"
```
