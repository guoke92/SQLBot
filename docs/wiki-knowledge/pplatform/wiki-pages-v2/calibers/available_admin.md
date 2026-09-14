---
type: caliber
title: 可用管理员
page_key: available_admin
domain: 客户中心
status: draft
aliases:
  - listCompanyManagerUserId
  - 有效管理员
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustPersonApplication.java:listCompanyManagerUserId
contract_version: "0.1"
belong: calibers
---

可用管理员口径用于管理员查询、通知与变更校验场景，只认 `user_type = 'accountAdmin'` 且启用标记为 Y 的联系人。关联 [[cust_person_info]]、术语 [[admin]] 与状态机 [[person_account_status]]。

```ground:caliber
name: 可用管理员
predicate: cust_person_info.user_type = 'accountAdmin' AND cust_person_info.enable = 'Y'
scope: 管理员查询、通知、变更校验
evidence: code_path:CustPersonApplication.java:listCompanyManagerUserId
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。