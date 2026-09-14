---
type: caliber
title: 已实名认证
page_key: realname-passed
domain: 客户联系人管理
status: draft
aliases:
  - 实名通过
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonController.getVerifyResult"
contract_version: "0.1"
belong: calibers
---

已实名认证口径把自动认证通过与人工认证通过合并视为「通过」，即 [[tables/cust_person_info]] 的 `phone_realname_status in ('AUTOMATIC_AUTHENTICATION_PASSED','MANUAL_AUTHENTICATION_PASSED')`。

## 需求背景

对业务而言自动与人工只是达成路径不同，结果一致，因此判断是否放行时采用合并口径；区分路径的场景应回到 [[processes/person-realname-status]] 看具体状态值。

```ground:caliber
caliber: 已实名认证
predicate: "cust_person_info.phone_realname_status in ('AUTOMATIC_AUTHENTICATION_PASSED','MANUAL_AUTHENTICATION_PASSED')"
scope: 判断实名认证通过
evidence: "code:CustPersonController.getVerifyResult"
```

## 版本演进

- v0：首次登记。

相关：[[processes/person-realname-status]]、[[calibers/realname-pending]]、[[tables/cust_person_info]]。