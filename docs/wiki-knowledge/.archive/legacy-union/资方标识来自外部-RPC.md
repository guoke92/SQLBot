---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:funding-party-rules@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 资方标识来自外部 RPC
page_key: 资方标识来自外部-RPC
domain: 资金方规则
field_targets:
- funding_rule_info.funding_party_mark
---
# 资方标识来自外部 RPC

funding_party_mark 经 RPC（QUERY_FUNDER_MARK）来自外部系统，非本库表关联。

```ground:rule
rule: rpc-external-anchor
field_targets:
- funding_rule_info.funding_party_mark
impact: query_constraint
content: funding_party_mark 经 RPC（QUERY_FUNDER_MARK）来自外部系统，非本库表关联。
scope: 资方维度统计的数据来源
```

## 关联
- [[funding_rule_info]]
