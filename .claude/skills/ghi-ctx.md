# ghi-ctx skill

当需要知道哪个issue还没有被 bot 回复时使用。

## 使用方式

运行命令：
```
ghi-ctx <repo>
# 或（默认 owner 为 gitluopu）
```

## 输出说明

返回 JSON：
- `needHandleIssue`: 是否有需要 bot 处理的 issue
- `issues[]`: 需要处理的 issue 列表
  - `issueId`: issue 编号
  - `context`: bot 最后一次发言及之前所有内容（Markdown）
  - `problem`: bot 最后一次发言之后用户的新消息（Markdown）
