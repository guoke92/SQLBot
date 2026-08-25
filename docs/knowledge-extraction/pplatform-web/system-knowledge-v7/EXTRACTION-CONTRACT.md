# v6 全系统知识包提取契约（子代理必读）

你是 SQLBot 知识提取 agent。为 pplatform-web 系统提取【一个业务域】的知识单元，产出 KnowledgePackageV2 单元 YAML，遵循 v3.1 契约（concept 锚定 / 最小字段声明 / 单一语义 / 证据可追溯）。

## 1. 输入与输出
- 源码仓库：/Users/fanjunwei/IdeaProjects/pplatform-web（commit ee434954e）
- 输出文件：/Users/fanjunwei/Projects/SQLBot/docs/knowledge-extraction/pplatform-web/system-knowledge-v6/units/<你的domain>.yaml（用 write 工具写）
- 返回：JSON {unit_id, sources: [...], evidence: [...], tables_covered: [...], scan: {valid, blocking, advisory}}

## 2. 提取方法（按顺序）
1. 用 extract 脚本拿机械基线：extract-catalog（表/字段/注释）、extract-enums（枚举字典）、extract-relationships（静态关系），输出到 /tmp。
2. 读业务域核心代码（Controller/Service/Facade/Mapper XML/枚举/DO），提取读写流转、状态机、口径、指标、规则、关系。每条事实附 文件:行号 证据。
3. 按业务场景组装单元（一个域一个 unit，不要拆成多个）。
4. 自检：写一个临时自包含包（manifest 内联你的 sources/evidence + 你的 unit），跑 scan --strict，修到 0 blocking 为止。

## 3. 单元 YAML 结构（KnowledgeUnitEntry）
```yaml
unit_id: <domain-id>
revision: 1
title: <中文标题>
aliases: [口语别名]
domain: <业务域>
applicability: <适用问数场景；不适用什么>
description: <一句话>
content:
  concepts: []      # 每个必须有 field_targets
  processes: []     # data_effects + next_stages
  datasets: []      # 最小字段声明
  relationships: [] # left/right {dataset, field} + evidence_refs
  calibers: []      # field_targets + contract_fragment
  metrics: []       # field/grain
  domain_rules: []  # applicability + query_impact + field_targets（三者非空）
  verified_query_patterns: []  # query + intended_specification.caliber_id + verification.status=PENDING_VALIDATION
evidence_refs: [...]  # 单元级证据
assumptions: []
conflicts: []
confidence: 0.9
```

## 4. 硬性规则（违反即返工）
1. concept 必须 field_targets：状态类→承载其 dictionary 的字段（字典跨两个字段时两个都写，键值一致）；实体类（概念即一张表）→表 id/业务键。
2. 最小字段声明：只声明被 concept 锚定 / process data_effects / relationship 端点 / caliber/rule/metric 引用的字段。纯物理字段留在 catalog，不进包。
3. 单一语义：跨单元共享表（cust_company_info、tenant_project、platform_product 等）字段 payload 与建档单元的权威声明一致（见 v5 units/enterprise-onboarding.yaml 对照）。同一物理字段跨单元 name/data_type/dictionary 逐字一致。
4. 关系：content.relationships 的 left/right 用 dataset_id（本单元内）；跨单元关系不写进单元，返回给主 agent 统一放 relationships.yaml。relationship_type 只有 EQUI_JOIN（真 FK 连接）或 SHARED_KEY（共享键，非 JOIN）。
5. 证据：每条 evidence_refs 指向你返回的 evidence_id；每条 evidence 附 文件:行号 locator + 可验证 claim。不要伪造 executed/passed。
6. 状态值以库为准：字典展示名与口语可不同（如 BUILD_SUCCESS 展示为 认证成功，口语为 建档成功），键必须是物理值。
7. 噪声排除：租户字段（db_tenant_code/app_tenant_code/organization_id）、审计字段（create_by/create_time/deleted/remark）、流程样板（act_procinst_*）不作为关系/概念，但可作为规则谓词字段。

## 5. 自检步骤（写完后必做）
在 /Users/fanjunwei/Projects/SQLBot 下建临时包：/tmp/v6_selfcheck_<domain>/knowledge-package.yaml（内联你的 sources/evidence + knowledge_units: [你的unit]），然后：
  backend/venv/bin/python scripts/knowledge-package.py scan --strict /tmp/v6_selfcheck_<domain>
修到：valid=true 且 blocking=0 且 advisory 尽量少（FIELD_DECLARATION_ORPHAN 必须=0）。
再跑：backend/venv/bin/python scripts/knowledge-package.py decompose /tmp/v6_selfcheck_<domain>
检查：concept_of > 0、merge_conflicts=0、stub_nodes 尽量少。

## 6. 返回格式（最终消息输出 JSON）
{
  "unit_id": "<domain-id>",
  "sources": [{"source_id": "...", "kind": "source_code|database_catalog", "locator": "仓库内路径", "repository_revision": "ee434954e"}],
  "evidence": [{"evidence_id": "...", "source_id": "...", "evidence_kind": "code_path|database_schema|query_usage", "locator": "文件#方法 或 文件:行号", "claim": "...", "confidence": 0.9}],
  "tables_covered": ["物理表名"],
  "scan": {"valid": true, "blocking": 0, "advisory": 0}
}

## 7. 参考范例
- 建档单元（已达标）：/Users/fanjunwei/Projects/SQLBot/docs/knowledge-extraction/pplatform-web/system-knowledge-v5/units/enterprise-onboarding.yaml —— 严格按它的结构、证据粒度、字段声明风格来。
- 详细方法论：/Users/fanjunwei/Projects/SQLBot/.cursor/skills/knowledge-extraction/reference.md