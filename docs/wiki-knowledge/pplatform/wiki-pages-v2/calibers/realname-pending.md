---
type: caliber
title: 待实名认证
page_key: caliber.realname_pending
domain: 客户联系人管理
status: draft
aliases:
  - 未认证
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonController.getVerifyResult"
contract_version: "0.1"
---

待实名认证口径为 [[tables/cust_person_info]] 的 `phone_realname_status = 'TO_BE_VERIFIED'`。

## 需求背景

该口径用于判断经办人是否需要弹出实名认证引导，是前端流程分支的直接依据；状态流转见 [[processes/person-realname-status]]。

```ground:caliber
caliber: 待实名认证
predicate: "cust_person_info.phone_realname_status = 'TO_BE_VERIFIED'"
scope: 判断经办人是否需要弹出实名认证
evidence: "code:CustPersonController.getVerifyResult"
```

## 版本演进

- v0：首次登记。

相关：[[processes/person-realname-status]]、[[calibers/realname-passed]]、[[rules/skip-realname-limit]]。