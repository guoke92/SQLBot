---
type: concept
title: 产融
page_key: chanrong
domain: 项目报表/统计/上报
status: draft
aliases:
  - 产融
  - 产融平台
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectReportApplication.getCompaniesByProjectId
  - code_path:ProjectReportApplication.exportProjectReport
contract_version: "0.1"
maps_to: cust_project_rel
field_targets:
  - cust_project_rel.project_id
adjudication: boundary
also_confused_with:
  - 讯易链
belong: concepts
---

「产融」在本主题中首先是一个数据来源标识，而不是泛指金融业务：它的落库位置是本地的 [[tables/cust_project_rel|cust_project_rel]] 及其关联的项目主体。做企业清单、对接人、联系人统计时，凡标注来源为产融的数据都应从本地表取，走 [[calibers/project_ledger_company_query|产融项目台账企业查询口径]]。

## 需求背景

需求文档中「产融平台」与「产融」交替出现，本页判定二者为同义（synonym 侧的同义词由 aliases 承载），但「产融」与「讯易链」之间是边界（adjudication=boundary），不可互换。

## 版本演进

v0 契约首版。边界说明：产融走本地表 cust_project_rel，讯易链走洞察平台/wec_project_cust_operation_rel；导出时的来源文案由 [[calibers/project_ledger_export_source|项目台账导出企业source判定]] 从 tenant_project.channel 反推。易混项：讯易链。