---
type: concept
title: 企业角色术语桥（cust_company_type / company_type / role_type / cust_type）
page_key: concept.company_role_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - 企业角色
  - cust_company_type
  - company_type
  - role_type
  - cust_type
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.cust_company_type]
  - semantic:field_semantics[cust_person_info.company_type]
  - semantic:field_semantics[cust_role_info.role_type]
  - semantic:field_semantics[cust_group_rel.cust_type]
  - semantic:field_semantics[cust_project_rel.company_type]
contract_version: "0.1"
maps_to:
  - term: cust_company_type
    target: cust_company_info.cust_company_type
    evidence: code
  - term: company_type
    target: cust_person_info.company_type
    evidence: code
  - term: role_type
    target: cust_role_info.role_type
    evidence: code
  - term: cust_type
    target: cust_group_rel.cust_type
    evidence: code
field_targets:
  - cust_company_info.cust_company_type
  - cust_person_info.company_type
  - cust_role_info.role_type
  - cust_group_rel.cust_type
  - cust_project_rel.company_type
---

「企业角色」在企业主表以 JSON 数组字符串存放，在关系表中拆成单值：联系人的 company_type 是数组中的一项，cust_role_info.role_type 一企业一角色一行，集团成员用 cust_type 表达，项目关联用 company_type 表达。

## 需求背景

同一角色概念在不同表以数组、单值、枚举名三种形态出现，跨表比对前需先做形态归一（数组展开 → 单值）。role_type 取值来自 CustCompanyTypeEnum.name()/dictKey，是这套术语的枚举基准。相关状态联动见 [[rules/role_status_follow_company]]。

## 版本演进

v0：首次成页；数组元素的具体取值范围在语义分析中仅以示例形式出现，未做穷举。