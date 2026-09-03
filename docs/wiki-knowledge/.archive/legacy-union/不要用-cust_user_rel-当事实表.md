---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:person-user@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 不要用 cust_user_rel 当事实表
page_key: 不要用-cust_user_rel-当事实表
domain: 企业建档
field_targets:
- cust_person_info.id
---
# 不要用 cust_user_rel 当事实表

画像仅 1 行，人员问数以 cust_person_info / cust_role_info 为准。

```ground:rule
rule: do-not-use-user-rel
field_targets:
- cust_person_info.id
impact: query_constraint
content: 画像仅 1 行，人员问数以 cust_person_info / cust_role_info 为准。
scope: 企业用户数
```

## 关联
- [[cust_person_info]]
