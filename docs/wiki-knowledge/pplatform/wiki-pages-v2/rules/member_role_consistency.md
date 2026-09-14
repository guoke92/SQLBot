---
type: rule
title: 成员单位角色一致性
page_key: member_role_consistency
domain: 集团关系
status: draft
aliases:
  - 导入角色一致性校验
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: rules
---

# 成员单位角色一致性

导入时，同一上级下所有成员单位的企业角色必须一致，且与已存在的上级企业角色一致。

## 需求背景

角色不一致会导致集团树内的权限/产品范围推导出错，因此导入阶段即拦截。角色字段与全局角色的区别见 [[enterprise_role]]。

## 版本演进

- 该校验仅在导入链路（`checkRoleExcelData`）生效，页面单个新增路径由不同校验覆盖，需注意两条入口的规则不完全对称。

```ground:rule
name: 成员单位角色一致性
content: 导入时同一上级下所有成员单位的企业角色必须一致，且与已存在上级企业角色一致
impact: 导入校验
field_targets:
  - cust_group_rel.cust_type
evidence: code_path:CustGroupRelApplication.java:checkRoleExcelData
```