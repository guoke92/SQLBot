---
type: concept
title: 企业角色（cust_type）
page_key: cust-type
domain: 企业集团关系
status: draft
aliases: [cust_type, 公司类型, companyType]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java
contract_version: "0.1"
maps_to: 'cust_group_rel.cust_type = JSON 数组字符串（如 ["SUPPLIER"]）'
field_targets:
  - cust_group_rel.cust_type
  - cust_company_info.cust_company_type
adjudication: boundary
also_confused_with:
  - DB 注释“多企业角色用逗号分隔”
  - CustCompanyInfoDO.cust_company_type
boundary: 库注释写逗号分隔，代码实际统一 JSONArray.toJSONString() 存取与 like '%"FINANCE"%' 精确匹配；多角色通过 addRoleToRoot 追加数组元素，不能按逗号切分解析。
sources: ["enrich:wiki-admin"]
belong: concepts
---

企业角色描述成员单位在集团中承担的身份（如 SUPPLIER、FINANCE），落库字段为 `cust_group_rel.cust_type`，实际以 JSON 数组字符串存储。所属表见 [[tables/cust_group_rel]]，相关唯一性校验见 [[rules/group-rel-uniqueness]]。

## 需求背景

同一成员单位可承担多个角色，代码通过 addRoleToRoot 向数组追加角色，并按 like 精确匹配单个角色做筛选；若按库注释的「逗号分隔」解析，将无法正确拆出角色集合。

## 版本演进

v0 契约按现状固化：存储形态已从注释描述的逗号分隔演进为 JSON 数组，库注释成为历史描述，以代码为准。

## 判定边界

库注释写逗号分隔，代码实际统一 JSONArray.toJSONString() 存取与 like '%"FINANCE"%' 精确匹配；多角色通过 addRoleToRoot 追加数组元素，不能按逗号切分解析。

相关：[[cust_group_rel]]
