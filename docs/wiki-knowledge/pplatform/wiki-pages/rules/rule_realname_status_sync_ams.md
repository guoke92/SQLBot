---
type: rule
title: 实名认证状态同步AMS
page_key: rule_realname_status_sync_ams
belong: rules
domain: customer
status: published
aliases: []
oid: 1
sources: ["enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_person_info.phone_realname_status]
scope:
  databases: [lowcode_pplatform]
---

该规则规定当运营人员后台实名认证通过后，需将状态同步至AMS侧，确保一致。

## 需求背景

`updateVerifyNameStatus` 设置 `phone_realname_status=MANUAL_AUTHENTICATION_PASSED` 后调用 `clientOperatorStatusSyncService.put`，失败抛出 `BaseException`，确保AMS侧经办人实名状态与产融一致。

## 版本演进

规则来自代码路径 `CustPersonApplication.updateVerifyNameStatus`，无文档声明冲突。

```ground:rule
name: 实名认证状态同步AMS
content: "updateVerifyNameStatus设置phone_realname_status=MANUAL_AUTHENTICATION_PASSED后调用clientOperatorStatusSyncService.put，失败抛出BaseException"
impact: 确保AMS侧经办人实名状态与产融一致
field_targets:
  - "cust_person_info.phone_realname_status"
evidence: "code_path:CustPersonApplication.updateVerifyNameStatus"
```

相关：[[cust_person_info]]
