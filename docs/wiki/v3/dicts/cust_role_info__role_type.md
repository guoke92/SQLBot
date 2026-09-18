---
type: dict
title: cust_role_info.role_type
page_key: cust_role_info__role_type
belong: dicts
status: draft
anchors: [cust_role_info.role_type]
sources: ['database_profile:cust_role_info.role_type', 'database_schema:cust_role_info.role_type',
  'code_path:CustCompanyTypeEnum.java:15', 'code_path:CustCompanyTypeEnum.java:18',
  'code_path:CustCompanyTypeEnum.java:20', 'code_path:CustCompanyTypeEnum.java:17',
  'code_path:CustCompanyTypeEnum.java:27', 'code_path:CustCompanyTypeEnum.java:21',
  'code_path:CustCompanyTypeEnum.java:16', 'code_path:CustCompanyTypeEnum.java:19',
  'code_path:CustCompanyTypeEnum.java:25', 'code_path:CustCompanyTypeEnum.java:23',
  'code_path:CustCompanyTypeEnum.java:22', 'code_path:CustCompanyTypeEnum.java:24',
  'code_path:CustCompanyTypeEnum.java:26']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_role_info]
---

# cust_role_info.role_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_role_info.role_type`，表页 [[tables/cust_role_info]]。

## 取值

```ground:dict
dict: cust_role_info__role_type
fields: [cust_role_info.role_type]
values:
  SUPPLIER: {trust: confirmed, label: 供应商, evidence: 'code_path:CustCompanyTypeEnum.java:15'}
  CORE: {trust: confirmed, label: 核心企业, evidence: 'code_path:CustCompanyTypeEnum.java:18'}
  FINANCE: {trust: confirmed, label: 金融机构, evidence: 'code_path:CustCompanyTypeEnum.java:20'}
  PROJECT_COMPANY: {trust: confirmed, label: 项目公司, evidence: 'code_path:CustCompanyTypeEnum.java:17'}
  CORPORATION_COMPANY: {trust: confirmed, label: 集团公司, evidence: 'code_path:CustCompanyTypeEnum.java:27'}
  PLATFORM_OPERATOR_COMPANY: {trust: confirmed, label: 平台运营方, evidence: 'code_path:CustCompanyTypeEnum.java:21'}
  DEALER: {trust: confirmed, label: 经销商, evidence: 'code_path:CustCompanyTypeEnum.java:16'}
  CORE_MANAGER: {trust: confirmed, label: 核心企业管理机构, evidence: 'code_path:CustCompanyTypeEnum.java:19'}
  FACTOR_COMPANY: {trust: confirmed, label: 保理买卖方, evidence: 'code_path:CustCompanyTypeEnum.java:25'}
  '"SUPPLIER"': {trust: proposed}
  '"CORE"': {trust: proposed}
  CORE_ADMIN: {trust: proposed}
  CORE_SUB: {trust: confirmed, label: 核心企业子公司, evidence: 'code_path:CustCompanyTypeEnum.java:23'}
  CORE_FUNCTIONAL_DEPARTMENT: {trust: confirmed, label: 核心企业职能部门, evidence: 'code_path:CustCompanyTypeEnum.java:22'}
  CORE_BRANCH: {trust: confirmed, label: 核心企业分公司, evidence: 'code_path:CustCompanyTypeEnum.java:24'}
  PLATFORM_COMPANY: {trust: confirmed, label: 平台方, evidence: 'code_path:CustCompanyTypeEnum.java:26'}
triage: keep
```
