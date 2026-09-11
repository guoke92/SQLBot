---
type: caliber
title: 有效企业管理员口径
page_key: valid-enterprise-admin
belong: calibers
domain: 客户角色与数据权限组织
status: published
aliases:
  - isEnterpriseAdmin
oid: 1
sources:
  - code_path
contract_version: "0.1"
field_targets: [cust_person_info.company_type, cust_person_info.enable, cust_person_info.ref_cust_company_info, cust_person_info.user_type]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该口径描述判定某用户是否为企业下指定角色类型的启用管理员。

## 需求背景

用于数据权限保存等管理操作前的管理员身份校验。

## 版本演进

初始语义抽取版本，后续需补充管理员变更与多角色扩展处理。

```ground:caliber
name: 有效企业管理员
predicate: cust_person_info.user_type = 'accountAdmin' AND cust_person_info.enable = 'Y' AND cust_person_info.ref_cust_company_info = {companyCode} AND cust_person_info.company_type = {companyType}
scope: 判定某用户是否为企业下指定角色类型的启用管理员
evidence: code_path:DataPermissionApplication.java:isEnterpriseAdmin()
```

相关页面：[[联系人_客户人员]] [[admin]] [[data-permission-save-admin-required]] [[user_type]]

相关：[[cust_person_info]]
