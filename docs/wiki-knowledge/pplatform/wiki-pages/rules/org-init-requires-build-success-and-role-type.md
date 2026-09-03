---
type: rule
title: 组织初始化要求建档成功且需角色类型
page_key: org-init-requires-build-success-and-role-type
domain: 客户角色与数据权限组织
status: published
aliases:
  - initRootOrg
oid: 1
sources:
  - code_path
contract_version: "0.1"
field_targets: [cust_company_info.cust_build_status, cust_role_info.enable, cust_role_info.role_type]
scope:
  databases: [lowcode_pplatform]
---

该规则保证组织初始化只对已认证且明确角色的企业生效。

## 需求背景

来自 CustSysOrgApplication.initRootOrg()/initRootOrgBatchOneCompany() 的初始化校验逻辑。

## 版本演进

初始语义抽取版本，后续需补充角色类型为空时的处理策略。

```ground:rule
name: 组织初始化要求建档成功且需角色类型
content: 初始化根组织前校验企业 cust_build_status=BUILD_SUCCESS，且 companyType 不能为空；批量初始化时按每个启用角色的 roleType 分别初始化
impact: 保证组织架构只对已认证且明确角色的企业生效
field_targets:
  - cust_company_info.cust_build_status
  - cust_role_info.role_type
  - cust_role_info.enable
evidence: code_path:CustSysOrgApplication.java:initRootOrg()/initRootOrgBatchOneCompany()
```

相关页面：[[cust_company_info]] [[cust_role_info]] [[customer-role-status]]