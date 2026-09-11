---
type: rule
title: 每企业每角色类型仅一名管理员
page_key: one-admin-per-company-role-type
belong: rules
domain: 客户角色与数据权限组织
status: published
aliases:
  - checkBeforeSave
oid: 1
sources:
  - code_path
contract_version: "0.1"
field_targets: [cust_person_info.company_type, cust_person_info.enable, cust_person_info.ref_cust_company_info, cust_person_info.user_type]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则保证企业+角色维度管理员唯一性。

## 需求背景

来自 CustPersonApplication.checkBeforeSave() 的保存前校验逻辑。

## 版本演进

初始语义抽取版本，后续需补充管理员变更时的交接流程。

```ground:rule
name: 每企业每角色类型仅一名管理员
content: 保存/更新经办人或变更管理员时，校验同企业同 companyType 且 enable=Y 且 user_type='accountAdmin' 的记录唯一，若已存在其他管理员则抛异常
impact: 保证企业+角色维度管理员唯一
field_targets:
  - cust_person_info.user_type
  - cust_person_info.company_type
  - cust_person_info.ref_cust_company_info
  - cust_person_info.enable
evidence: code_path:CustPersonApplication.java:checkBeforeSave()
```

相关页面：[[联系人_客户人员]] [[admin]]

相关：[[cust_person_info]]
