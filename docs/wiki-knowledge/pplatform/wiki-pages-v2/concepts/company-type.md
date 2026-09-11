---
type: concept
title: 客户角色 / 企业角色（companyType）
page_key: concept.company-type
domain: 项目报表/统计/上报
status: draft
aliases:
  - companyType
  - company_type
  - companyTypeZh
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportController.java
  - db:cust_project_rel
  - db:cust_project_code_record
contract_version: "0.1"
maps_to: "cust_project_rel.company_type（单值）：CORE/FINANCE/SUPPLIER/DEALER/PROJECT_COMPANY/CORE_MANAGER/CORPORATION_COMPANY/PLATFORM_OPERATOR_COMPANY；跨源映射：产融 CORE↔讯易链 ce，产融 FINANCE↔讯易链 cpt"
also_confused_with:
  - "cust_project_code_record.company_type（JSON 数组，多角色集合）"
adjudication: boundary
boundary: "关联表为单角色（弹窗「客户角色」单选项）；录入码记录表为受限多角色集合；转换只允许 CORE/FINANCE 两值参与跨源映射，其它角色在报表查询中退化为不筛选（置 'a'）。"
sources: ["enrich:wiki-admin"]
---

# 客户角色 / 企业角色（companyType）

companyType / company_type 在本主题中出现三种形态，混用会导致取数错误：关联表的单值角色、录入码记录表的多值角色集合、以及讯易链侧的短码（ce/cpt）。

## 需求背景

项目台账的关联企业弹窗中，客户角色为单选项，因此 [[tables/cust_project_rel]] 以单值存放；企业项目码录入时企业可能同时具备多个角色，因此 [[tables/cust_project_code_record]] 以 JSON 数组保存提交时的角色集合。报表查询侧需要按来源做角色编码转换，只对 CORE/FINANCE 建立了映射，其余角色退化为不筛选，转换口径见 [[calibers/company-type-cross-source-mapping]]。

关联表还存在拼写变体 PLATFORM_OPREATOR_COMPANY（疑似历史脏数据），比较与展示时需容错。

## 版本演进

角色枚举随业务扩展（新增 PROJECT_COMPANY、CORE_MANAGER、CORPORATION_COMPANY、PLATFORM_OPERATOR_COMPANY 等），但跨源映射仍只覆盖 CORE/FINANCE 两值；录入码记录表的多值形态与关联表的单值形态长期并存，未见统一模型。

相关：[[cust_project_rel]]
