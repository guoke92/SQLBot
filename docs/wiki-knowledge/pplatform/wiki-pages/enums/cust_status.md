---
type: enum
title: cust_status
page_key: cust_status
domain: 基线
status: draft
aliases: [新增, 注销, 生效]
oid: 1
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# cust_status

（权威枚举页：6 值，绑定方式 setter-evidence，主承载 cust_company_info.cust_status；db 实测分布。）

```ground:enum
enum: cust_status
fields: [cust_company_info.cust_status, cust_person_info.status, cust_role_info.status, cust_user_rel.type_status]
values:
  ADD:
    label: 未生效
  EFFECT:
    label: 已生效
  FREEZE:
    label: 冻结
  WRITEOFF:
    label: 已注销
  FAILURE:
    label: 失效
  CHANGE:
    label: 变更
```

## 表述差异

- ADD: 权威「未生效」；另有表述 ['新增']
- EFFECT: 权威「已生效」；另有表述 ['生效']
- WRITEOFF: 权威「已注销」；另有表述 ['注销']
