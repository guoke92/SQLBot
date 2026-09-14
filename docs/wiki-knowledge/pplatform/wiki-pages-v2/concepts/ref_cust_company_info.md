---
type: concept
title: 关联企业编码
page_key: ref_cust_company_info
domain: 平台内部服务对接
status: draft
aliases:
  - ref_cust_company_info 字段族
  - 关联企业编码约定
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
maps_to:
  - cust_company_info.code
field_targets:
  - cust_person_info.ref_cust_company_info
  - cust_project_rel.ref_cust_project_rel_cust_company_info
  - cust_role_info.ref_cust_company_info
  - cust_auth_application.ref_cust_company_info
adjudication: >
  各关联表上的 ref_cust_company_info 系列字段存放企业业务编码，指向
  cust_company_info.code；跨表关联以企业编码取值，而不是以企业主键 id 取值。
also_confused_with:
  - cust_role_info.platform_cust_id
  - cust_project_rel.project_id
belong: concepts
---

「关联企业编码」是平台内部服务对接中的一条字段命名约定：凡是需要指向企业主体的关联表，都使用 `ref_cust_company_info`（或在被外键命名规则改造后形如 `ref_cust_project_rel_cust_company_info`）这类字段存放**企业业务编码**，与 [[cust_company_info]] 的 `code` 对应。

这条约定使得多个服务可以在不了解对方表结构的情况下按同一取值联结——[[cust_person_info]] 用它把人员挂到企业，[[cust_project_rel]] 用它表达企业与项目的关系，[[cust_role_info]]、[[cust_auth_application]] 同样如此。相关页面：[[cust_company_info]]、[[cust_person_info]]、[[cust_project_rel]]。

## 需求背景
企业主键 `id` 是数据库内部标识，业务侧服务在接口与消息中流动的是企业编码。若部分表按主键关联、部分表按编码关联，内部服务对接时会出现「传了编码查不到」的错配，因此把关联取值统一到企业编码上是必要的契约约束。

## 版本演进
- v0.1（本页）：约定来自代码语义分析中各关联表字段释义的一致性归纳。容易混淆的标识：`cust_role_info.platform_cust_id`（平台客户ID）与 `cust_project_rel.project_id`（项目ID），它们与关联企业编码不是同一取值域。