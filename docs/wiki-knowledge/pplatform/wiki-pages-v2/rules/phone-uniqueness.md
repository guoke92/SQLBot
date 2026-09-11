---
type: rule
title: 手机号唯一性
page_key: rule.phone_uniqueness
domain: 客户联系人管理
status: draft
aliases:
  - 手机号不可重复
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.checkBeforeSave"
contract_version: "0.1"
---

同一企业下手机号不能重复：新增或编辑联系人时，系统校验该手机号是否已被本企业其他联系人使用。

## 需求背景

手机号既用于登录，也用于邀请与实名认证（见 [[tables/cust_person_info]] 的 `phone` 语义），若同一企业下出现重复手机号，登录与认证都会产生歧义，因此在保存前统一拦截。

```ground:rule
rule: 手机号唯一性
content: 同一企业下手机号不能重复
impact: 新增或编辑联系人时校验手机号是否已被使用
field_targets:
  - cust_person_info.phone
  - cust_person_info.ref_cust_company_info
evidence: "code:CustPersonApplication.checkBeforeSave"
```

## 版本演进

- v0：首次登记。

相关：[[tables/cust_person_info]]、[[rules/cert-no-uniqueness]]、[[concepts/handler]]。