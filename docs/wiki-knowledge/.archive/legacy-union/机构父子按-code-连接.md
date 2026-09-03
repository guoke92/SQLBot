---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:org-manage@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 机构父子按 code 连接
page_key: 机构父子按-code-连接
domain: org
field_targets:
- org_manage.parent_code
---
# 机构父子按 code 连接

parent_code 关联父机构 code，不是 id。

```ground:rule
rule: org-parent-by-code
field_targets:
- org_manage.parent_code
impact: query_constraint
content: parent_code 关联父机构 code，不是 id。
scope: 机构层级
```

## 关联
- [[org_manage]]
