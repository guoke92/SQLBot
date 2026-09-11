---
type: caliber
title: 跳过实名认证
page_key: caliber.realname_skip
domain: 客户联系人管理
status: draft
aliases:
  - 免实名
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonController.skipRealNameAuth"
contract_version: "0.1"
---

跳过实名认证口径为 [[tables/cust_person_info]] 的 `skip_auth_flag = 'Y'`，标识该联系人被允许豁免实名认证。

## 需求背景

该标记不是联系人自行可选的，而是在满足特定租户或企业角色条件时由系统置位，限制条件见 [[rules/skip-realname-limit]]。

```ground:caliber
caliber: 跳过实名认证
predicate: "cust_person_info.skip_auth_flag = 'Y'"
scope: 允许跳过实名认证的经办人
evidence: "code:CustPersonController.skipRealNameAuth"
```

## 版本演进

- v0：首次登记。

相关：[[rules/skip-realname-limit]]、[[processes/person-realname-status]]、[[tables/cust_person_info]]。