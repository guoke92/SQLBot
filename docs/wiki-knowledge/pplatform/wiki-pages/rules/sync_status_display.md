---
type: rule
title: 同步状态展示规则
page_key: rules/sync-status-display
domain: AMS联系人第三方对接
status: published
aliases: [同步状态规则]
oid: 1
sources:
  - code
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

queryUserList 中管理员/经办人同步状态展示规则：若 operatorPushSystem 包含目标系统渠道或来源为 AMS 则视为已同步，否则需检查系统链路或标记未同步。

## 需求背景
前端企业用户列表需要展示联系人是否已同步到 AMS 等目标系统，该规则定义判定逻辑。

## 版本演进
初始版本基于 CustCompanyQueryApplication.queryUserList 提取。

```ground:rule
name: 同步状态展示规则
content: "queryUserList中管理员/经办人同步状态：若operatorPushSystem包含目标系统渠道或来源为AMS则视为已同步，否则需检查系统链路或标记未同步"
impact: "影响前端联系人列表同步状态展示"
field_targets: ["CustPersonInfoDO.operatorPushSystem", "CustPersonInfoDO.source"]
evidence: "code_path:CustCompanyQueryApplication.queryUserList"
```

[[cust_person_info_do]] [[sync_status_admin]] [[sync_status_operator]]