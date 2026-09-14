---
type: caliber
title: 产融项目台账企业查询口径
page_key: project_ledger_company_query
domain: 项目报表/统计/上报
status: draft
aliases:
  - 产融项目台账企业查询口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectReportApplication.getCompaniesByProjectId
contract_version: "0.1"
belong: calibers
---

查询某个项目下挂的关联企业时的标准口径：以 project_id 定位 [[tables/cust_project_rel|cust_project_rel]]，并要求 enable='Y'（逻辑有效）。enable 的过滤不可省略，否则会带出被逻辑删除的历史关联企业，污染企业数量与联系人信息。

## 需求背景

需求文档主张 cust_project_rel 存储项目与企业关联关系及运营对接人信息，该口径正是其取数落地方式。

## 版本演进

v0 契约首版。口径只覆盖 [[concepts/chanrong|产融]]侧数据；讯易链侧走洞察平台/wec_project_cust_operation_rel，两者不可混用，边界见 [[concepts/chanrong]]。

```ground:caliber
name: 产融项目台账企业查询口径
predicate: "cust_project_rel.project_id = ? AND cust_project_rel.enable = 'Y'"
scope: 产融项目下的关联企业
evidence: code_path:ProjectReportApplication.getCompaniesByProjectId
```