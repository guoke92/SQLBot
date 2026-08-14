# AI智能问数知识包 Schema 与统一导入规范 v1

## 1. 目标与边界

`KnowledgePackage 1.0` 是代码扫描、数据库分析、对话沉淀和人工编辑共同使用的唯一交换格式。它不是新的运行时知识表，也不替代术语、口径、表关系、查询示例和规则各自的治理模型。

```text
代码/文档/数据库/对话/人工
          ↓
 KnowledgePackage 1.0
          ↓ scan + preview
 ┌────────┼──────────┬──────────┬──────────┐
 术语     口径       字段关系    查询示例    规则
 同步     staging    candidate   验证后同步  staging
          ↓认证       ↓确认                   ↓认证
       运行时资产   运行时元数据             运行时资产
```

原始事实和来源证据保留在知识包中，供审核、追溯和后续加工使用，但不会直接进入向量召回，避免把未经归纳的实现细节当作业务知识。

## 2. 顶层结构

```yaml
schema_version: "1.0"
package_id: pplatform-enterprise-onboarding-v1
title: 企业建档知识
description: 从代码、设计文档与数据模型提取
generated_at: 2026-08-12T10:00:00+08:00
generator:
  name: sqlbot-knowledge-extractor
  version: "1"
defaults:
  datasource_id: null
  datasource_name: null
  assistant_id: null
sources: []
items: []
```

约束：

- `package_id` 表示一个可持续更新的知识集合，必须长期稳定。
- `item_id` 是包内稳定身份；再次导入相同 `package_id + item_id` 时更新由该包管理的术语和示例，而不是重复新增。
- 缺失于新版本的条目不会自动删除。删除、禁用和已确认关系变更继续走人工治理。
- `status` 仅允许 `draft/candidate/reviewed/verified/rejected`。
- `confidence` 范围为 0～1，只表达提取置信度，不能代替人工认证。
- `evidence_refs` 引用 `sources.source_id` 或外部可审计证据标识。

服务端的完整 JSON Schema 可通过 `GET /api/v1/knowledge/import/schema` 获取。

## 3. 六类条目

### 3.1 terminology：业务术语与字典解释

必填：`word`、`description`。可选 `aliases`、数据源/助手作用域和 `knowledge_meta`。

用途是把“建档、已建档、待客户认证”等自然语言映射为可理解的业务含义。若其描述包含字段映射，应使用业务名称并附字段名，例如“建档状态(cust_build_status)”，但术语本身不能冒充可执行过滤口径。

治理：`reviewed/verified` 可直接同步到术语表并向量化；其他状态仅在预检中标记待审核。

### 3.2 caliber：可执行业务口径

必填：`label`、`contract_fragment`。`contract_fragment` 必须是 IntentDefault v1 的合法片段：

```yaml
contract_fragment:
  version: 1
  intent_defaults:
    - dataset_subject: 企业
      kind: filter
      value:
        business_name: 有效企业
        operator: eq
        values: [Y]
```

不允许用自由文本条件、SQL 片段、物理表字段映射或旧 slot/QuerySpecification 表达可执行口径。导入预检会通过与运行时相同的 IntentDefault 解析器校验 output/group/filter/time/order 的类型。字段和关系映射属于 GroundingRule，不得混入业务默认口径。

治理：始终进入 `KnowledgeStaging`，认证后才可 Bind。

### 3.3 relation：字段关联候选

必填：`left`、`right`，均使用 `{table_name, field_name, database_name?}`；可选 `relation_kind`、`cardinality`、`evidence`。

治理：仅写入 `CANDIDATE`。不会覆盖 `CONFIRMED/REJECTED/DISABLED` 的审核结论，也不会调用关系画布的全量替换接口。

### 3.4 example：自然语言到查询计划示例

必填：`question`、`query`。`training_type` 为 `sql` 或 `rest`。

只有以下验证信息同时成立才可导入：

```yaml
verification:
  executed: true
  passed: true
  datasource_id: 8
  checked_at: 2026-08-12T10:00:00+08:00
  query_hash: ...
```

“由模型生成”“语法看起来正确”不等于验证通过。未执行示例保留在包内，预检标记 `review_required`。

### 3.5 rule：跨查询约束

必填：`label`、`content`。规则描述稳定且跨问题适用的约束，例如“推送成功不得解释为审核通过”，不保存一次查询的临时选择。

治理：进入 staging，人工认证后生效。

### 3.6 evidence：来源事实

必填：`subject`、`predicate`、`value`。用于保存“某回调更新某字段”“某表一行代表一次处理记录”等可追溯事实。

治理：`retained_only`，不会直接发布为运行时资产。事实需进一步归纳成 terminology/caliber/relation/example/rule 才能参与运行时召回。

## 4. 自动扫描与分类

扫描遵循“显式优先、形状推断兜底”：

1. 有 `kind` 时严格按 kind 解析；不支持的 kind 直接告警。
2. 无 kind 时按独占字段推断：
   - `word/term` → terminology；
   - `contract_fragment` 或 `label + requirements` → caliber；
   - `left + right` / `source_field + target_field` → relation；
   - `question + query/sql` → example；
   - `label + content/rule` → rule；
   - `subject + predicate + object/value` → evidence。
3. 无法唯一判断时不猜测，产生 scanner warning。
4. 旧审计目录可扫描 `asset-candidates.yaml`、`facts.jsonl`、`relations.jsonl` 和 `source-catalog.jsonl`；坏记录逐条跳过，不能导致其他有效条目丢失。
5. 兼容扫描只用于生成标准包；后续维护必须以 `knowledge-package.yaml/json` 为准，避免长期存在两套标准。

缺少 `item_id` 的兼容数据会依据规范化内容生成稳定哈希 ID。正式知识包仍应显式维护语义稳定的 ID。

## 5. 预检、导入与同步

### API

```http
POST /api/v1/knowledge/import/preview
POST /api/v1/knowledge/import/apply
```

请求：

```json
{
  "package": {"schema_version": "1.0", "package_id": "...", "items": []},
  "package_id": null,
  "default_datasource_id": 8,
  "include_kinds": ["terminology", "relation"]
}
```

选择多个文件或整个文件夹时，页面改用同一接口提交 `documents`：

```json
{
  "documents": [
    {"name": "facts.jsonl", "content": "..."},
    {"name": "asset-candidates.yaml", "content": "..."}
  ],
  "package_id": "pplatform-enterprise-onboarding-v1",
  "default_datasource_id": 8
}
```

`package` 与 `documents` 严格互斥。文件、文件集合和文件夹最终都进入同一个扫描器并生成一份 `KnowledgePackage`，不存在三套导入逻辑。

`package_id` 只用于提交旧列表/旧分组结构时补充稳定身份；标准包已自带 `package_id`，应保持为 `null`。
`package` 也可直接传 YAML/JSON 文本，页面文件上传和结构化 API 使用同一个服务端扫描器。

`preview` 返回每条知识的分类、标准化结果、字段解析结果、`ready/review_required/invalid/retained_only` 和原因。调用方必须先展示并确认预检，再调用 `apply`。

`apply` 首先把整包所有条目登记到知识包管理区，再把满足门禁的条目投影到运行时资产，并报告 `imported/updated/staged/candidate/skipped/rejected`。所以 `review_required`、`retained_only` 和单条 `invalid` 也不会丢失；它们可以在知识包详情中继续审核和修订。不同知识类型原本就有不同的事务和异步向量化边界，因此运行时投影采用逐条结果，不伪装成全包原子事务。

页面同时支持：

- 选择一个标准知识文件；
- 一次选择多个提取文件；
- 选择整个提取目录。浏览器只读取支持的 YAML/JSON/JSONL 文件，README 等说明文件不会被误分类。

同一 `package_id` 重导会生成新的登记 revision，并按稳定 `item_id` 更新；本次未出现的历史条目保留但标记为不在当前版本，不自动删除运行时资产。

### CLI

```bash
# 将旧提取目录规范化为唯一知识包
backend/venv/bin/python scripts/knowledge-package.py scan \
  docs/knowledge-extraction/pplatform-web/enterprise-onboarding-v1 \
  -o /tmp/knowledge-package.yaml

# 仅验证结构并统计分类
backend/venv/bin/python scripts/knowledge-package.py validate /tmp/knowledge-package.yaml

# 数据源字段解析和治理门禁预检
backend/venv/bin/python scripts/knowledge-package.py preview /tmp/knowledge-package.yaml \
  --base-url http://localhost:8000 --token "$SQLBOT_TOKEN" --datasource-id 8

# 人工审核预检报告后应用
backend/venv/bin/python scripts/knowledge-package.py apply /tmp/knowledge-package.yaml \
  --base-url http://localhost:8000 --token "$SQLBOT_TOKEN" --datasource-id 8 --yes
```

HTTP API 不接受服务器本地路径，避免越权读取文件。CLI 在操作者本地读取目录并提交标准包；页面在浏览器本地读取用户选择的目录，将受支持的结构化文件内容提交给统一扫描接口。服务端始终不读取任意客户端路径。

## 6. 提取质量要求

任何提取器都必须先产出证据，再产出资产候选，并满足：

- 业务术语解释能落到业务阶段、数据形态和边界，不写空泛百科描述；
- 口径包含粒度、指标/属性、过滤条件、时间口径和必要关系，不只给 SQL；
- 关系明确左右字段、方向、候选基数及证据，不从同名字段直接推定；
- 查询示例必须在目标数据源执行验证；
- 实现风险、代码缺陷和临时行为保留为 evidence，不自动升级成业务规则；
- 密码、密钥、个人敏感数据和整行样本不得进入知识包。

以上标准使代码扫描、数据库画像、对话沉淀和人工维护最终落到同一可视化、可审核、可同步的资产生命周期，而不是各自建立导入捷径。
