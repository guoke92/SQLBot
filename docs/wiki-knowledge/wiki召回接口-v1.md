# Wiki 召回接口 v1（SQLBot 侧运行时接线）

> **V0 验证期路径**：直接调用 llm-wiki `POST /search`（RRF/聚合/图扩展白拿），
> SQLBot 侧按 v0 §7.1 做客户端 ground 块解析（Python 实现：`backend/apps/knowledge/wiki/contract.py`，
> 与 TS 参考实现共享 fixture）。
> 本文件的 `mode=business/physical` 配额语义、提示词拼接协议、金标回归门禁是 SQLBot 侧适配器的
> 运行时约定，v0 未覆盖；`recall.py` 进程内管道定位为参考实现与阶段二独立 daemon 的种子。
> 接口契约：召回返回**渲染好的文本段**（直拼提示词），不返回结构化槽位。
> 运行时确定性由门禁体系（plan_gate / 硬校验 / T4 扩表 / 反弹重校验）保证，不由知识系统结构保证。
> 参照实现：llm-wiki `search.rs`（RRF/页面聚合/图扩展配额）+ `page_embedding.rs`（指纹失效）。

## 1. 接口签名

```python
def recall(
    query: str, *, oid: int, ds_ids: list[int],
    top_k: int = 8,
    mode: Literal["business", "physical"] = "business",
    vector_scores: Mapping[str, float] | None = None,   # 可注入向量通道；None=纯词法降级
) -> list[RenderedPassage]: ...

@dataclass(frozen=True)
class RenderedPassage:
    page_key: str
    title: str
    score: float
    source: Literal["lexical", "graph"]     # vector 通道接入后扩展 "vector"
    related_to: tuple[str, ...]              # graph 命中时的种子页溯源
    text: str                                # 渲染好的 markdown 段（直拼提示词）
```

`mode="business"`：业务语义阶段，窗口大（5~10 页），图配额原样生效；
`mode="physical"`：门禁/SQL 阶段，窗口小，图扩展降格为候选竞争。

## 2. 检索管道（公式与 llm-wiki 源码一致）

```
切块   按标题层级切 + 围栏/锚点块原子（永不切断）+ chunk 携带 heading_path（进向量文本）
嵌入   块级向量 + 指纹失效（页面 version+embedding config 变更才重嵌）
超采   top_k × 3（≥30）个 chunk
融合   RRF：score = Σ 1/(60 + rank)   （词法路 × 向量路；向量故障静默降级纯词法）
聚合   page = top + min(0.3 × Σ(尾部 chunk 分), 1 − top)
图扩展 邻接 = [[wikilink]] 双向边（别名归一化解析）
       种子 = 直接命中前 20；邻居分 = Σ 1/(rank+1)
       配额 business = ceil(limit × (0.30 − 0.15 × 向量覆盖率))，clamp[1, limit−1]
       邻居分 /61 缩放；带 related_to 溯源
围栏   published only + oid + scope.databases 物理库名交集（SQL WHERE 级，非后过滤）
```

## 3. 运行时接线（切换面）

| 运行时点 | 调用 | 拼接位置 |
|---|---|---|
| `recall_knowledge` 步 | `recall(问题+澄清答案, mode=business)` | `<business_knowledge>` prose 段 |
| plan_gate missing_concepts | `recall(concept, mode=physical)` 逐概念 | 反弹上下文段 |
| 知识地图 | wiki index 渲染（页面清单） | `<knowledge_map>` 段 |
| 澄清约束 | 规则锚点块文本 | `<business_rules>` 段 |

命中遥测（page_key/score/source/related_to）落 `query_run.agent_decision["wiki_hits"]`。

## 4. 开关与灰度

- `KNOWLEDGE_BACKEND: unit | wiki`，按数据源粒度灰度（per-DS allowlist）；
- 金标集回归（历史对话：成功用例真实用表 + 全部 SCHEMA_NOT_SUPPORTED 失败案例），
  **表召回@k / 值命中率 / 澄清质量 ≥ 旧系统才翻默认**；
- 回滚 = 改配置（旧系统冻结待命）。

## 5. 实现位置

- 原型：`backend/apps/knowledge/wiki/`（contract / chunker / graph / recall，进程内存储，零 DB 依赖）；
- 示例语料：`docs/wiki-knowledge/examples/`（ds 15 产融真实场景，含 159 病例页）；
- 生产化路径：进程内存储 → PG `wiki_page` 表 + 嵌入列（自家 embedding_fingerprint 家法）。
