---
type: process
title: 联系人激活状态
page_key: cust_person_info__status
belong: processes
domain: cust
status: draft
anchors: [cust_person_info.status]
field_targets: [cust_person_info.status]
sources: ['code_path:CustPersonApplication.java:402', 'code_path:CustPersonApplication.java:852',
  'code_path:CustPersonApplication.java:841']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_person_info]
---

# 联系人激活状态

钉 cust_person_info.status。企业冻结/注销不走本列。
管理员变更是冻旧建新：旧行 enable=N 且 status=FREEZE，新行 status=EFFECT。
Java 枚举名 admin 入库是 accountAdmin。


```ground:process
process: 联系人激活状态
field: cust_person_info.status
entry: CustPersonApplication.ifNessaryFrzAdm
stages:
- stage: 新建
  transitions:
  - from: ''
    event: 从法人生成管理员
    to: ADD
    evidence: code_path:CustPersonApplication.java:402
  - from: ADD
    event: 管理员变更新建联系人
    to: EFFECT
    evidence: code_path:CustPersonApplication.java:852
- stage: 冻旧建新
  trigger: 管理员/经办人变更
  transitions:
  - from: EFFECT
    event: 冻结旧管理员或经办人
    to: FREEZE
    evidence: code_path:CustPersonApplication.java:841
  effects:
  - op: 置为 N（与 status 共写）
    table: cust_person_info
    fields: [enable]
```

## 页面链接

- [[tables/cust_person_info]]
- [[dicts/cust_person_info__status]]
