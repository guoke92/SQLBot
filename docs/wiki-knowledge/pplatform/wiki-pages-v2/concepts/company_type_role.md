---
type: concept
title: 企业角色 company_type
page_key: company_type_role
domain: 平台内部服务对接
status: draft
aliases:
  - 企业角色术语桥
  - company_type 字段族
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
maps_to:
  - cust_company_info.cust_company_type
field_targets:
  - cust_person_info.company_type
  - cust_project_rel.company_type
adjudication: >
  企业主表以 cust_company_info.cust_company_type 承载企业角色，且以 JSON 数组字符串
  存储多个角色；cust_person_info.company_type 与 cust_project_rel.company_type 是
  同一术语在关联表上的落点，取值需与主表角色集合保持一致。
also_confused_with:
  - cust_person_info.user_type
  - sys_cust_user_rel.cust_type
belong: concepts
---

「企业角色」是同一业务术语在多个表上的桥接点：主表 [[cust_company_info]] 用 `cust_company_type` 以 JSON 数组字符串保存企业当前承担的角色，人员表 [[cust_person_info]] 与关系表 [[cust_project_rel]] 分别在记录上标注 `company_type`。服务对接时，主表回答「这家企业是什么」，关联表回答「这条记录属于哪种角色语境」。

## 需求背景
企业可能同时具备多个角色，因此主表选择用 JSON 数组字符串承载；下游服务若按单值解析，会出现角色判断遗漏。关联表上的 `company_type` 需要能回落到主表的角色集合中，否则会出现不一致的角色标注。

## 版本演进
- v0.1（本页）：术语桥来自代码语义分析中三处同名字段的释义归纳。易混淆项：`cust_person_info.user_type`（人员用户类型）与 `sys_cust_user_rel.cust_type`（客户类型）属于不同维度。