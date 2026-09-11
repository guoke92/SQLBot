---
type: caliber
title: AMS 待办按联系人 id 查询
page_key: caliber/AMS待办按联系人id查询
domain: 通知/验证码/短链
status: draft
aliases: [productAppId=AMS, getPersonId, 待办 userId 口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustNoticeService.java
contract_version: "0.1"
---

AMS 场景下待办查询的主键不是登录用户 id，而是联系人（cust_person_info）的 id，由 getPersonId 取得。这个口径差异是跨系统待办对账时最容易出错的地方。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: AMS 待办按联系人 id 查询
predicate: productAppId = 'AMS' → userId = cust_person_info.id（getPersonId）
scope: CustNoticeService#pageTodo / CustNoticeController#getProductNoticeCount
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustNoticeService.java#pageTodo
```

## 关联

[[calibers/未完成待办]] · [[calibers/产融本库待办]]