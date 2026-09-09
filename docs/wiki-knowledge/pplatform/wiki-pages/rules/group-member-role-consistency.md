---
type: rule
title: 集团成员角色一致性
page_key: group-member-role-consistency
belong: rules
domain: 客户角色与数据权限组织
status: published
aliases:
  - checkRoleExcelData
oid: 1
sources:
  - code_path
contract_version: "0.1"
field_targets: [cust_company_info.cust_company_type, cust_group_rel.cust_type]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则保证集团树内企业角色统一，避免成员单位与父级角色不一致。

## 需求背景

来自 CustGroupRelApplication.checkRoleExcelData() 的集团导入校验逻辑。

## 版本演进

初始语义抽取版本，后续需补充集团成员角色变更同步策略。

```ground:rule
name: 集团成员角色一致性
content: 集团导入时，成员单位的企业角色必须与父级企业角色一致，否则报错
impact: 保证集团树内企业角色统一
field_targets:
  - cust_group_rel.cust_type
  - cust_company_info.cust_company_type
evidence: code_path:CustGroupRelApplication.java:checkRoleExcelData()
```

相关页面：[[cust_company_info]] [[enterprise-role]]

相关：[[cust_group_rel]]
