# 工具体系的"状态归属"分析

- 分析对象：统一问数 Agent（`chat.yaml`）的 10 个工具及其状态流向
- 分析日期：2026-09-29
- 分析依据：源码逐处核实（引用的 `文件:行` 均已打开确认）
- 关联文档：`docs/reviews/unified-agent-review-2026-09-29.md`（整体评审）

---

## 一、结论

**这不是"工具无状态"，而是"状态没有归属"。**

系统在概念上选择了「工具无状态 + 状态全部放在对话文本里」，但在实现上状态又同时存在于 **4 个存储介质**（闭包、进程内全局字典、LangGraph 检查点、DB 表）里，而这四处之间**没有划分规则、没有单一真值源、没有恢复协议**。

于是拿到了两者的缺点：

| | 无状态本该带来的 | 实际 |
|---|---|---|
| 可并行 | 工具互不影响，可直接并发 | ❌ 串行执行，且有未加锁的 read-modify-write |
| 可缓存 | 纯函数可直接 memo | ❌ 只有失败去重，成功无 memo，用 prompt 当缓存 |
| 可重放 | 输入即全部因果 | ❌ `tool_steps` 不存 args，只能全量 dump prompt |
| 契约清晰 | 入参出参都有类型 | ❌ 入参 Pydantic 强校验，出参 `data: Any` |

| | 有状态本该带来的 | 实际 |
|---|---|---|
| 少 token | SQL/句柄传一次 | ❌ 上轮 SQL 靠 `fold_turn` 重新排版成字符串塞回历史 |
| 零漂移 | 引用而非复制 | ❌ 模型必须逐字复述 SQL 才能改它 |
| 可校验 | 不变量写在代码里 | ❌ 效率类不变量降级为 prompt 口头约定 |

**一句话**：签名是函数式的，副作用是全局的。这是最难维护的一种组合——读者从签名看不出副作用，出错时也指不到副作用。

---

## 二、事实基线（已核实）

### 2.1 工具的"无状态"只是签名上的

`build_agent_tools(llm_service, access_scope)`（`apps/chat/tools/registry.py:413`）用**闭包**捕获 request-scoped 对象，10 个工具全是 `StructuredTool.from_function` 包一层内嵌函数（`registry.py:418-503`）。

也就是说：工具不是纯函数，它们是**带环境快照的闭包**。`llm_service` 里挂着 datasource、protocol、session、`chat_question`；`access_scope` 挂着权限。这些在签名里一个字都看不到。

### 2.2 状态实际散落在 4 个介质

| # | 存储 | 内容 | 生命周期 |
|---|---|---|---|
| 1 | 闭包捕获 | `llm_service` / `access_scope` | 单次 run 构建，进程内 |
| 2 | 进程内全局字典 `_contexts[run_id]`（`runtime_context.py:26`） | `bound_tools` / `llm` / `knowledge_plane` / `probe_sql_calls` / `sql_delivered` / `access_scope` | 进程内，进程没了就没了 |
| 3 | LangGraph 检查点 state | `tool_rounds` / `tool_steps` / `knowledge_plane` / `probe_sql_calls` / `memory_slots` / `turn_message_start` / `open_tool_spans` | 可持久化、可中断恢复 |
| 4 | DB 表 `result_dataset`（`process_timeline.py:837-917`） | 交付结果集行数据 | 唯一真正持久的 |

同一份 `knowledge_plane` **同时存在于 #2 和 #3**，每个工具轮要在两者之间来回搬 4 次（见 §3.3）。

---

## 三、问题清单

### P0-1 同一个事实，6 处独立推导，4 个不同存储

事实：「本轮是否已交付 SQL / 交付的是哪条 SQL」。这个判断被独立实现了 6 次：

| # | 位置 | 数据来源 |
|---|---|---|
| 1 | `unified_agent._agent_has_sql_result`（`unified_agent.py:116-138`） | 图 state 的 `tool_steps` + 本轮 ToolMessage |
| 2 | `agent_finalize.has_publishable_query_result`（`agent_finalize.py:61-83`） | 复用 #1，兜底查 DB `result_dataset` |
| 3 | `complete_answer._sql_already_delivered`（`complete_answer.py:15-20`） | 进程内全局袋的 `sql_delivered` |
| 4 | `turn_fold._baseline_sql`（`turn_fold.py:162-178`） | ToolMessage 的 `data.sql`（优先 `required != False`） |
| 5 | `agent_finalize` 组装 `TurnAnswerV1`（`agent_finalize.py:135`） | DB `result_dataset` |
| 6 | `MemorySlots.active_baseline_sql`（`memory_slots.py:32`） | 由 `agent_finalize.py:349` 写入 |

第 6 条最要命：`active_baseline_sql` **有字段、有写入、有持久化，但没有读者**。它的唯一读取方法 `extract_change_baseline()`（`memory_slots.py:49-57`）在 `apps/` 与 `tests/` 里**零调用**（已 grep 确认）。

后果：加一条"交付 SQL"的新语义（比如"交付但被用户撤回"）要同时改 6 个地方，漏一个就是静默不一致。这 6 处的判定阈值已经不一致了——#3 只看进程内标志，#1 看 state，两者在不同进程里会给出不同答案。

### P0-2 控制面信号塞在数据面里

`normalize_tool_result`（`tooling.py:349-397`）强制工具返回**恰好** `{ok, summary, data, error, failure}`，看起来非常严格。但 `data: Any`——真正的语义全在里面，靠字符串 key 约定：

| key | 谁读 | 语义 |
|---|---|---|
| `data.interrupt_required` | `route_after_tools_execution`（`unified_agent.py:697-701`） | **图路由依据** |
| `data.required` | `_agent_has_sql_result`、`turn_fold._baseline_sql` | 交付 vs 探查 |
| `data.skipped == "knowledge_budget"` | `_tool_message_skipped`（`tooling.py:589-592`） | 知识预算计数 |
| `data.terminal_answer` | `has_terminal_text_answer`（`complete_answer.py:58`） | 终答出口 |
| `data.sql` | 4 处 | 改 SQL 的基准 |
| `data.dataset_id` | `execute_tools_node`（`tooling.py:737`） | 挂结果卡 |

最直接的证据是 `_GENERIC_SKIP_KEYS`（`tooling.py:413-424`）——渲染器必须维护一份**控制面 key 的黑名单**，才能在给模型看的文本里把这些字段滤掉。需要黑名单，就说明两个平面混在了一起。

`route_after_tools_execution` 靠 `data` 里的魔法字段决定下一步走哪个节点，这是最危险的一处：**图拓扑的决策依据是一个无类型 dict 的字符串 key**。重命名这个 key 不会报错，只会静默走错分支。

### P0-3 工具通过进程内全局字典写状态，写入路径要靠"刮"

`get_table_schema` 实际做了 4 件事（`catalog_tools.py:382-462`）：

1. 读全局袋：`load_plane()` → `peek_runtime(run_id)`（`catalog_tools.py:145-150`）
2. 改全局袋：`plane.merge_recall(...)` 后 `save_plane()` → `attach_runtime(run_id, knowledge_plane=...)`（`catalog_tools.py:407-427`）
3. 改 `llm_service.chat_question.db_schema = catalog`（`catalog_tools.py:423-426`）——**第三个状态通道**
4. 返回值里再带一份 `schema_text`（`catalog_tools.py:452-462`）

然后 `execute_tools_node` 在**工具循环结束后**，回头把全局袋"刮"出来写进图 state（`tooling.py:847-862`）：

```python
snap = peek_runtime(run_id) if run_id else None
plane = AgentKnowledgePlane.from_dump(
    (snap or {}).get("knowledge_plane") or state.get("knowledge_plane")
)
```

而 `agent_loop` 每轮开头又把 state 里的 plane **写回**全局袋（`unified_agent.py:419-424`）。完整回路：

```
工具 load_plane() ─读─┐
                      ├─ 进程内全局袋 ─刮─ execute_tools_node ─写─ 图 state
工具 save_plane() ─写─┘                                              │
                      └──────── agent_loop 每轮写回 ◄────────────────┘
```

一轮一个值，4 次搬动（读、写、刮、回写），跨越 3 个介质。

**为什么这是错的**：无状态工具的定义是"没有副作用"，但这里的工具**有副作用，只是副作用是隐式的**。图 state 的写入点是 `execute_tools_node`，而不是"某个工具真的产出了数据"——中间靠一个约定俗成的全局袋搭桥。任何绕过 `execute_tools_node` 的调用路径（测试、MCP、直连）都不会记录这层状态。

顺带：`save_plane` 的写入没有版本号或时间戳，`load_plane` 读到的可能是**同一轮里前一个工具刚刚改过的版本**（同一进程内共享）。这意味着工具之间存在**隐式顺序依赖**——同轮两个 `get_table_schema` 调用的结果取决于执行顺序。现在串行所以"看起来是对的"。

### P0-4 结构化状态建好了，消费端被显式摘掉

这是"不对劲"最纯粹的一处：

- `MemorySlots.active_baseline_sql` 存上一轮交付的 SQL（`memory_slots.py:32-35`）
- `agent_finalize.py:349` 每轮把它写进 state
- `build_agent_system_prompt(memory_slots=..., change_baseline=...)` —— 两个参数都标着 **`# noqa: ARG001 — kept for callers`**（`agent_prompt.py:158-159`），即**故意不使用**
- `AgentKnowledgePlane.apply_to_system_message` 里的同名参数标着 `# noqa: ARG002`（`agent_knowledge.py:468`），`rebuild_system_message` 标 `ARG001`（`agent_knowledge.py:806`）
- `render_memory_slots` 的 docstring：*"Compact caliber surface for tests / UI; **no longer injected into System**"*（`agent_prompt.py:134-135`）
- `build_continued_messages(history, question, knowledge_plane)`（`session_transcript.py:143-150`）**没有 `memory_slots` 参数**

于是上一轮 SQL 的传递路径变成了：结构化 state → **被忽略** → 模型只能从原始 transcript 里读 → `fold_turn` 把它**重新排版成自然语言**塞回历史（`turn_fold.py:111-129`）：

```
<turn_fold level="1">
问：…
SQL：
SELECT ...
用到：…
</turn_fold>
```

即：**结构化状态被降级成字符串，模型再从字符串里解析回来。** `fold_turn` 的 `_baseline_sql` 是第 4 份"哪条 SQL 是基准"的实现，它从 ToolMessage 里猜 `data.sql`；猜错（比如选中了探查 SQL）没有任何地方能发现。

一个更硬的问题：`turn_message_start`（`unified_agent.py:94-113`）把"本轮"的窗口切成 `messages[idx:]`，而 `_agent_has_sql_result` 只认这个窗口。transcript 折叠 + 窗口切片的组合意味着：**"上一轮的 SQL 在哪"这件事，答案取决于折叠级别和当前游标，而不是取决于任何一个字段。**

### P0-5 状态恢复协议不完整

`_hydrate_chat`（`runtime_context.py:139-176`）在需要重建运行时只回填 **4 个 key**：`llm_service` / `access_scope` / `llm` / `bound_tools`。

| key | 换进程后会怎样 |
|---|---|
| `bound_tools` / `llm` | 重建，✅ |
| `access_scope` | 重建，✅（故意不序列化权限，注释写得很清楚） |
| `knowledge_plane` | 无兜底，但 `agent_loop` 每轮从 state 回填（`unified_agent.py:419-424`）→ 侥幸可用 |
| `probe_sql_calls` | 同上 → 侥幸可用 |
| **`sql_delivered`** | **无任何兜底**。`complete_answer.py:20` 读到 `None` → 守卫静默关闭 |

`sql_delivered`（写入点 `execute_sql.py:301`）是**唯一只存在于进程内全局袋、且没有 state 镜像**的控制标志。它保护的不变量是"已交付 SQL 后禁止调用 `complete_without_sql`"（`complete_answer.py:25-30`）——而这个不变量完全可以由 state 里的 `tool_steps` 推导（`_agent_has_sql_result` 就是这么做的）。

**同一个不变量有两套实现，一套持久、一套不持久，且代码选了不持久的那套。** 这不是"无状态"，这是状态放错了地方。

### P1-1 成功路径没有幂等、没有 memo，用 prompt 当缓存

`_tool_call_signature` 的失败去重（`tooling.py:832-845`）只对**失败**生效。成功路径：

- 同一条 SQL 先探查后交付 → 打两次库（`_consume_probe_budget` 的注释明确说"仍要执行"）
- 重复 `get_table_schema` → 重复渲染 schema（虽然会被 `plane.tables` 拦住一句提示）
- 重复 `lookup_values` → 重复做值索引匹配

因为工具无状态，没有 `(ds_id, sql) → dataset_id` 的 memo。于是系统只能把缓存责任外推给模型，写进工具描述里：

> `GetTableSchemaInput.tables`：*"Do not pass tables already returned in this conversation's ToolMessages."*（`registry.py:206`）

**用 prompt 做缓存**——这既不省 token（模型要先想一遍）也不可靠（折叠后模型看不见）。

### P1-2 不变量的分布不对称：安全在代码，效率在 prompt

这个代码库把**安全类**不变量做得非常好，全部在代码里：

- 目录探查拒绝（`execute_sql.py:167-173`）
- Wiki 枚举探查拒绝（`execute_sql.py:58-78`）
- AST 派生真实表 + `validate_plan` 白名单（`execute_sql.py:199-207`）
- 参数级 Pydantic 校验（10 个 `args_schema`）

而**效率类**不变量全部在 prompt 或说明里：

- "本对话已返回过的表禁止再调"（`agent_prompt.py:41`、`registry.py:206`）
- "首轮并行"（`agent_prompt.py:52`）——运行时是串行的（`tooling.py:672`）
- "齐备即停"（`agent_prompt.py:53`）
- "单表禁用 relations"（`agent_prompt.py:42`）

反差本身说明了问题：**凡是有状态能承载的规则都被做成了代码，凡是需要状态才能验证的规则都被降级成了祈祷。** 而"不要重复展开表"这一条其实**有**半套代码实现（`plane.tables` 的 dedup，`catalog_tools.py:400`），但它的正确性挂在 §P0-3 那个全局袋上。

### P1-3 并行被状态写入点绑死

上一次评审的 P1-1（prompt 承诺并行、代码串行）根因就在这里，不是"忘了并发"：

- `open_tool_spans` 是 dict，但 `tool_steps` 是 append（顺序敏感，`tooling.py:814-831`）
- 每个工具可能改 `knowledge_plane`（`catalog_tools.py:427`、`wiki_search.py:38`）
- `_consume_probe_budget` 是**无锁 read-modify-write**（`execute_sql.py:96-99`）：

```python
used = int(_runtime_snapshot().get("probe_sql_calls") or 0)   # 读（无锁）
run_id, _token = current_worker_identity()
if run_id:
    attach_runtime(run_id, probe_sql_calls=used + 1)          # 写（有锁）
```

今天串行，所以没 bug。一旦按 prompt 的承诺上并发，这里立刻丢更新。**"无状态"没有换来并行，隐式状态反而是不能并行的原因。**

### P1-4 审计被迫全量 dump——和 PII 问题是同一个根因

因为没有一个可序列化的"state"对象，`agent_loop` 只能把**整个 messages** 写进 span（`unified_agent.py:61-79` + `:541`）：

```python
row = {"type": ..., "content": str(getattr(message, "content", "") or ""), ...}
```

里面有 `execute_sql_sandbox` 的 `preview_rows`（真实业务数据）。`sanitize_audit_value` 只按 key 名脱敏，对长文本 `content` 完全透传。

这和上一次评审的 P2-1 是同一件事的两面：**没有 state 模型 → 无法记录"变了什么" → 只能记录"整份输入" → 于是 PII 落库。** 修 PII 的正确姿势不是采样，是先有 state 模型。

### P2 不可重放

`tool_steps` 只存 `{tool, result, ok}` / `{error, failure, tool}`（`tooling.py:814-831`）——**不存 args**。args 只在 `_tool_call_signature` 里被哈希一次（不落库），以及 span 里有一份。

所以：能不能重放一轮，取决于 ChatLog span 表保留多久。想"用同一组工具调用重跑一遍"在架构上做不到。

---

## 四、评估：当前设计实际买到了什么

公平地说，这套设计有一个真实收益：**图 state 保持可序列化，且不含 ORM 对象。**

`runtime_context.py:100-108` 的注释写了这个取舍：

> Checkpoints intentionally contain no ORM-backed request objects. Access scope is therefore recomputed from the current user and datasource instead of being retained in memory or serialized as stale permission data.

这是对的，而且权限重算比序列化快照更安全。问题不在"把不可序列化的东西放外面"，在于**把可序列化的东西也一起放在了外面**：`knowledge_plane`、`probe_sql_calls`、`sql_delivered` 全是纯 dict/bool，完全适合放进 state，却被放进了进程内全局袋。

**分界线应该是"能不能 msgpack 序列化"，而不是"是不是运行时对象"。** 现在这条线画错了位置——它把 request 对象和业务状态一起划到了外面。

---

## 五、两条出路

### 路线 A：把隐式状态显式化（`TurnContext`）

引入一个显式、可序列化、随图 state 走的状态对象：

```python
class TurnContext(BaseModel):
    rounds: int
    probe_calls: int
    delivered: bool
    datasets: list[DatasetRef]          # dataset_id / title / chart_type / sql
    current_sql: SqlRef | None          # revision + sql + tables
    opened_tables: list[str]
    opened_pages: list[str]
    excluded: list[str]
    calibers: dict[str, Any]
```

规则变成：**工具只能读写 `ctx`，禁止 import `runtime_context`。** 控制面信号从 `data` 上提为显式的 `signals: ToolSignals`。

收益：图路由不再猜 key；`_consume_probe_budget` 变成 `ctx.probe_calls += 1`（单写入点，可并发）；审计只落 ctx 的 diff；6 处"是否已交付"的判断收敛成 1 处。

### 路线 B：把状态外移到资源句柄（推荐先做）

保持工具"纯函数"的性质，但把**输入从内容改成引用**：

| 现在 | 改成 |
|---|---|
| `execute_sql_sandbox(sql="SELECT…")` | `execute_sql_sandbox(sql_ref="rev_7")` |
| `patch_and_compile_sql(base_sql="SELECT…", action=…)` | `patch_and_compile_sql(sql_ref="rev_7", action=…)` |
| `compare_results(base_sql=…, new_sql=…)` | `compare_results(base_ref="rev_7", new_ref="rev_8")` |

SQL workspace 就是一张 `run_id → revisions` 的表（`result_dataset` 已经在做类似的事，可以直接扩展）。

收益直接对上痛点：

- **token**：SQL 不再进模型上下文两次（出一次、进一次）
- **漂移归零**：模型不可能改到它没碰过的字节
- **可缓存**：`(ds_id, sql_hash)` 命中就直接返回旧 `dataset_id`
- **可并行**：工具仍是纯函数，`sql_ref` 是不可变引用
- **可审计**：重放只需要 `(rev_id, tool_name, args)`

代价是 prompt 要教模型"用句柄"，但 `patch_and_compile_sql` 已经在用 `base_sql` 传整条 SQL 了，改成传 id 对模型只会更简单。

### 推荐

**A 和 B 不冲突，是同一件事的两面**：B 是数据面引用化，A 是控制面显式化。建议 B 先落一片（SQL 句柄），因为它单独就能消掉 P0-4 / P1-1 / 一半的 P0-1，而且改动面小、可回滚。

---

## 六、最小落地顺序（每步可独立验证）

| 步 | 动作 | 消掉的问题 | 验证方式 |
|---|---|---|---|
| 1 | `sql_delivered` 改为从 state 的 `tool_steps` 派生，删掉进程内标志 | P0-5 | 单测：delivered 后调 `complete_without_sql` 被拒 |
| 2 | `data` 里的控制面 key 上提为 `ToolResult.signals`（Pydantic 枚举） | P0-2 | `_GENERIC_SKIP_KEYS` 可以删除；路由有类型 |
| 3 | `_consume_probe_budget` 的计数移到 `execute_tools_node`（单写入点） | P1-3 | 并发压测：N 个并行探查计数准确 |
| 4 | `patch_and_compile_sql` / `execute_sql_sandbox` 接受 `sql_ref` | P0-4 / P1-1 | 端到端：增量修改轮不出现 SQL 字面量 |
| 5 | 统一 `runtime_context` 访问层，工具禁止直接 import | P0-3 | import 检查 / 架构测试 |
| 6 | 6 处"是否已交付"判断收敛为 1 个函数 | P0-1 | 删掉 `active_baseline_sql` 或把它接进 prompt |

第 1 步大概 1 小时，第 2 步半天。

---

## 七、需要拍板的判断点

- [ ] **第 6 条怎么处理**：`memory_slots.active_baseline_sql` 是要**接回 prompt**（承认"上一轮 SQL 是结构化状态"），还是**连字段一起删掉**（承认"就是靠 transcript"）？现在这个中间态是最差的。
- [ ] **SQL workspace 用什么承载**：复用 `result_dataset` 加 `revision` 列，还是新建 `sql_revision` 表？
- [ ] **是否接受"工具可以读 ctx"**：这会让工具不再是纯函数，但消除了全部隐式全局。需要确认架构上接受。
- [ ] **多进程部署的现状**：`CONVERSATION_MAX_WORKERS=32` 是单进程线程池还是多 worker？这决定 `sql_delivered`（P0-5）是理论问题还是线上问题。
- [ ] `chat_question.db_schema` 可以直接删吗？"写了没人读"的第三例（已核实）：写入点是 live 的 `catalog_tools.py:426`，而全仓读取点都在已退役的 `nlq/` 模块里（`planning.py:229` / `context.py:596` / `presentation.py:93,558`），live 路径无读者。删掉可少一个状态位。
