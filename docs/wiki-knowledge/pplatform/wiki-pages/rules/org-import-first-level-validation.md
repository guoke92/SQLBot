---
type: rule
title: 组织导入一级组织校验
page_key: org-import-first-level-validation
belong: rules
domain: 客户角色与数据权限组织
status: published
aliases:
  - checkExcelData
oid: 1
sources:
  - code_path
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则防止组织导入破坏根组织或产生孤儿节点。

## 需求背景

来自 CustSysOrgApplication.checkExcelData() 的导入数据校验逻辑。

## 版本演进

初始语义抽取版本，后续需补充导入模板规范与错误处理。

```ground:rule
name: 组织导入一级组织校验
content: 组织导入时，Excel 中一级组织（parentOrgName 为 '/'）必须存在且唯一，且一级组织名称必须与系统企业名称一致；父组织名称必须在导入数据中存在，组织名称不能重复
impact: 防止组织导入破坏根组织或产生孤儿节点
field_targets:
  - sys_cust_org.org_name
  - sys_cust_org_rel.parent_org_id
evidence: code_path:CustSysOrgApplication.java:checkExcelData()
```

相关页面：[[sys_cust_org]] [[sys_cust_org_rel]]