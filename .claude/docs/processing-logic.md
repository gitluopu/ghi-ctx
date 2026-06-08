# ghi-ctx 内部处理逻辑

以 `ghi-ctx small-talk` 为例说明完整流程。

## 1. 获取所有 open issue

```
GET /repos/gitluopu/small-talk/issues?state=open&per_page=100
```

返回 issue 列表，每个 issue 包含 `number`、`body`（正文）、`user`、`created_at` 等字段。

## 2. 逐个构建完整 timeline

GitHub 的 `GET /repos/{owner}/{repo}/issues/{number}/timeline` **不包含 issue 正文**，只从创建后的第一个事件开始。

因此对每个 issue 手动将正文拼接为第一条事件：

```
synthetic "opened" event (from issue.body)
  +
GET /repos/gitluopu/small-talk/issues/{number}/timeline
```

合并后得到该 issue 的完整事件列表。

## 3. 过滤有效事件 & 打标签

遍历 timeline，只保留 actor 为已知身份的事件：

| GitHub login | 标签 |
|---|---|
| `gitluopu` | `user` |
| `ai-paul-bot` / `ai-paul-bot[bot]` | `bot` |

actor 字段：大多数事件用 `actor`，评论事件（`commented`）用 `user`，两个都尝试读取。其他 login 的事件直接跳过。

## 4. 判断 caseA / caseB

看过滤后最后一条事件的标签：

- **caseA**：最后是 `bot` → bot 已处理，跳过该 issue
- **caseB**：最后是 `user` → bot 还需处理，进入下一步

## 5. 切分 context / problem（仅 caseB）

找到 bot 最后一次发言的位置 `last_bot_idx`：

```
[0 .. last_bot_idx]  → context（历史上下文）
[last_bot_idx+1 ..]  → problem（待处理的新消息）
```

特殊情况：bot 从未发言过，则 `context` 为空，所有事件都是 `problem`。

## 6. 渲染为 Markdown

每条事件渲染为：

```markdown
### [user/bot] {event_type}
{body}
```

多条事件之间用 `---` 分隔。

## 7. 输出 JSON

```json
{
  "needHandleIssue": true,
  "issues": [
    {
      "issueId": 17,
      "context": "...",
      "problem": "..."
    }
  ]
}
```

`needHandleIssue` 为 `true` 当且仅当存在至少一个 caseB issue。
