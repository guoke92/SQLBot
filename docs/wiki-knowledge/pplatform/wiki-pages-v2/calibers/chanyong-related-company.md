---
type: caliber
title: 产融侧关联企业口径
page_key: caliber.chanyong-related-company
domain: 项目报表/统计/上报
status: draft
aliases:
  - 关联企业查询口径
  - getCompaniesByProjectId
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportApplication.java
contract_version: "0.1"
---

# 产融侧关联企业口径

项目台账查询关联企业时，当来源判定为产融（见 [[calibers/project-ledger-source]]），不再调用洞察平台，而是直接读本地 [[tables/cust_project_rel]]，并以项目 ID + 有效标识过滤，通过 `ref_cust_project_rel_cust_company_info` 回连 cust_company_info 取企业信息。

## 需求背景

关联企业列表需要与项目口径保持一致：产融来源的项目只认本地关联表，避免与讯易链/洞察平台的数据混流。角色维度在该路径下保持原值不做跨源转换（对比 [[calibers/company-type-cross-source-mapping]]）。

## 版本演进

本口径以 `enable = 'Y'` 作为有效过滤，说明逻辑删除已成为本表的默认过滤约定；未观察到该口径的历史版本差异。

```ground:caliber
name: "产融侧关联企业口径"
predicate: "cust_project_rel.enable = 'Y' AND cust_project_rel.project_id = :projectId"
scope: "项目台账→关联企业查询（source='产融' 时走本地表，不走洞察平台）"
evidence: "code_path:ProjectReportApplication.java:getCompaniesByProjectId"
```