---
type: caliber
title: 已同步状态判定-经办人
page_key: sync-status-operator
belong: calibers
domain: AMS联系人第三方对接
status: published
aliases: [经办人同步状态]
oid: 1
sources:
  - code
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

经办人同步状态判定口径：当企业用户列表中经办人的 operatorPushSystem 包含目标系统渠道，或来源为 AMS 时，视为已同步。

## 需求背景
查询企业用户列表时（queryUserList），前端需要展示经办人的同步状态，该口径定义了判定条件，较管理员少了“系统链路已通过”分支。

## 版本演进
初始版本基于 CustCompanyQueryApplication.queryUserList 提取。

```ground:caliber
name: 已同步状态判定-经办人
predicate: "CustPersonInfoDO.operatorPushSystem包含targetSysChannel OR source='AMS'"
scope: "查询企业用户列表时，经办人同步状态标记"
evidence: "code_path:CustCompanyQueryApplication.queryUserList"
```

[[cust_person_info_do]] [[sync_status_display]]