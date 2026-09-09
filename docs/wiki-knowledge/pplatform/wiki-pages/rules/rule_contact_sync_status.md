---
type: rule
title: 联系人同步状态判定
page_key: rule_contact_sync_status
belong: rules
domain: customer
status: published
aliases: []
oid: 1
sources: ["enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_person_info.operator_push_system, cust_person_info.source]
scope:
  databases: [lowcode_pplatform]
---

该规则定义企业管理页中联系人的已同步/未同步判定逻辑。

## 需求背景

管理员：`operator_push_system` 非空且包含目标渠道，或来源为AMS，视为已同步；否则未同步。经办人仅 `operator_push_system` 包含目标渠道或AMS来源视为已同步。该规则用于列表展示已同步/未同步状态。

## 版本演进

规则来自代码路径 `CustCompanyQueryApplication.queryUserList`，与口径「已同步业务系统联系人」一致。

```ground:rule
name: 联系人同步状态判定
content: "管理员：operator_push_system非空且包含目标渠道，或来源为AMS，视为已同步；否则未同步。经办人仅operator_push_system包含目标渠道或AMS来源视为已同步"
impact: 用于列表展示已同步/未同步
field_targets:
  - "cust_person_info.operator_push_system"
  - "cust_person_info.source"
evidence: "code_path:CustCompanyQueryApplication.queryUserList"
```

相关：[[cust_person_info]]
