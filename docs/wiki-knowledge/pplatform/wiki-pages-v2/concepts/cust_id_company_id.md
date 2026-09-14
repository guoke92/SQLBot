---
type: concept
title: custId / companyId
page_key: cust_id_company_id
domain: cust_org_permission
status: draft
aliases: [企业id, cust_company_info.id]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
  - code:CustSysOrgApplication.java
contract_version: "0.1"
maps_to: cust_company_info.id
field_targets: [cust_company_info.id, cust_person_info.ref_cust_company_info, sys_cust_org_user_permission.company_id]
adjudication: boundary
also_confused_with:
  - cust_company_info.code（ref_cust_company_info / custCode）
belong: concepts
sources: ["enrich:wiki-admin"]
---

custId/companyId 指 [[cust_company_info]].id 自增主键；refCustCompanyInfo 与 ref_cust_project_rel_cust_company_info 则是 code 业务编码。[[cust_person_info]] 同时保存 cust_company_id（主键）与 ref_cust_company_info（code），查询条件混用会出现看似「查不到数据」的问题，改条件时必须先确认用的是哪一轨。

## 需求背景
本页仅依据代码证据（DataPermissionApplication、CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

相关：[[sys_cust_org_user_permission]]
