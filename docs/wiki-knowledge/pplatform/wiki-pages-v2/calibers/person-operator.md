---
type: caliber
title: 经办人
page_key: caliber.person_operator
domain: 客户联系人管理
status: draft
aliases:
  - 经办人口径
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.insertOrUpdatePerson"
contract_version: "0.1"
---

经办人口径即按 [[tables/cust_person_info]] 的 `user_type = 'accountNormal'` 过滤，是业务办理与实名认证流程的主要对象。

## 需求背景

经办人是企业内实际使用业务功能的用户，新增/编辑经办人时系统会做手机号与证件号唯一性校验（[[rules/phone-uniqueness]]、[[rules/cert-no-uniqueness]]），并可能因来源不同默认置为建档成功（[[rules/new-person-default-build-success]]）。经办人常被口语称为「业务用户」，但不要与平台侧「运营人员」混用，见 [[concepts/handler]]。

```ground:caliber
caliber: 经办人
predicate: "cust_person_info.user_type = 'accountNormal'"
scope: 获取企业经办人
evidence: "code:CustPersonApplication.insertOrUpdatePerson"
```

## 版本演进

- v0：首次登记。

相关：[[tables/cust_person_info]]、[[concepts/handler]]、[[processes/person-realname-status]]、[[rules/phone-uniqueness]]。