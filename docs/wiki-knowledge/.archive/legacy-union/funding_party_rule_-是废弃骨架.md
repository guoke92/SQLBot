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
title: funding_party_rule_* 是废弃骨架
page_key: funding_party_rule_-是废弃骨架
domain: 资金方规则
field_targets:
- funding_rule_info.funding_party_mark
---
# funding_party_rule_* 是废弃骨架

funding_party_rule_cfg/detail/front 三表仅有低代码生成的 DO/Mapper 空壳， 全仓库无业务调用方、docs 无 DDL——是 GROUP-0002 设计迭代残留，实现已演进为 funding_rule_*。Dubbo 接口 Javadoc 引用它们属文档误导。

```ground:rule
rule: dead-skeleton-tables
field_targets:
- funding_rule_info.funding_party_mark
impact: query_constraint
content: funding_party_rule_cfg/detail/front 三表仅有低代码生成的 DO/Mapper 空壳， 全仓库无业务调用方、docs
  无 DDL——是 GROUP-0002 设计迭代残留，实现已演进为 funding_rule_*。Dubbo 接口 Javadoc 引用它们属文档误导。
scope: 资金方规则数据查找
```

## 关联
- [[funding_rule_info]]
