# 结构化输出规范（v0.1）

当前阶段默认要求 **JSON-first** 输出。

规则：
- 默认返回一个 JSON 对象
- 可额外附带 Markdown 说明，但 JSON 必须可被直接解析
- 如模型无法稳定输出 JSON，才允许 fallback 到 Markdown / FILE block

## 通用字段

所有 action 都应尽量包含：

```json
{
  "status": "success",
  "action": "analyze|write|review|fix",
  "result_format": "json_v1",
  "summary": "简短摘要",
  "warnings": [],
  "errors": []
}
```

## Analyze

```json
{
  "status": "success",
  "action": "analyze",
  "result_format": "json_v1",
  "summary": "实施方案摘要",
  "tasks": [
    {
      "id": "T001",
      "name": "项目初始化",
      "priority": "P0",
      "dependencies": [],
      "output_files": ["package.json", "src/main.ts"],
      "status": "pending"
    }
  ],
  "plan_markdown": "完整 Markdown 实施方案",
  "warnings": [],
  "errors": []
}
```

## Write / Fix

```json
{
  "status": "success",
  "action": "write",
  "result_format": "json_v1",
  "summary": "代码生成摘要",
  "file_operations": [
    {
      "path": "src/main.ts",
      "operation": "create",
      "description": "入口文件",
      "content": "...完整代码..."
    }
  ],
  "warnings": [],
  "errors": []
}
```

## Review

```json
{
  "status": "success",
  "action": "review",
  "result_format": "json_v1",
  "summary": "审查摘要",
  "passed": true,
  "score": 8.5,
  "issues": [
    {
      "severity": "warning",
      "type": "maintainability",
      "path": "src/main.ts",
      "line": 12,
      "message": "可进一步拆分函数",
      "suggestion": "拆出 util 方法"
    }
  ],
  "raw_text": "可选 Markdown 审查报告",
  "warnings": [],
  "errors": []
}
```

## fallback 兼容策略

- analyze: 允许返回 Markdown plan
- write/fix: 允许返回 FILE block
- review: 允许返回 Markdown review

但这些都只应作为兼容，不应再作为主协议。
