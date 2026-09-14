---
type: rule
title: 身份证号唯一性
page_key: cert-no-uniqueness
domain: 客户联系人管理
status: draft
aliases:
  - 证件号不可重复
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.checkBeforeSave"
contract_version: "0.1"
belong: rules
---

同一企业下身份证号不能重复：新增或编辑联系人时，系统校验证件号码是否已被本企业其他联系人使用。

## 需求背景

证件号是实名认证的核验依据（`certification_type` 默认 `CRET_ID`，见 [[tables/cust_person_info]]），同一企业内重复会破坏实名主体唯一性，因此在保存前与手机号唯一性一并校验。

```ground:rule
rule: 身份证号唯一性
content: 同一企业下身份证号不能重复
impact: 新增或编辑联系人时校验证件号码是否已被使用
field_targets:
  - cust_person_info.certification_no
  - cust_person_info.ref_cust_company_info
evidence: "code:CustPersonApplication.checkBeforeSave"
```

## 版本演进

- v0：首次登记。

相关：[[tables/cust_person_info]]、[[rules/phone-uniqueness]]、[[processes/person-realname-status]]。