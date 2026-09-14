---
type: concept
title: 数据来源 / source
page_key: data-source
domain: 项目报表/统计/上报
status: draft
aliases:
  - source
  - dataSource
  - transaction_platform
  - data_source
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportApplication.java
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
maps_to: "项目台账侧 source ∈ {产融, 讯易链}；项目立项统计侧 data_source ∈ {MANUAL, WECHAT}；两者语义不同，同名不同域"
also_confused_with:
  - "productCode（ACFLOW/RVSFACTOR_PC 等存放在 cust_project_rel.remark）"
adjudication: boundary
boundary: "项目台账 source 决定「读本地表 vs 调洞察平台」；项目立项统计 data_source 决定「是否企微同步生成的立项」。二者不可互换。"
belong: concepts
---

# 数据来源 / source

「数据来源」在本主题下是一个被两个域共用的词：项目台账域用它决定取数通道，立项统计域用它决定单据的产生方式。任何报表/统计/上报的字段说明中见到 source、dataSource、data_source、transaction_platform，必须先判断落在哪个域。

## 需求背景

- 项目台账域：以 transaction_platform 是否等于「产融平台」判定 source，产融走本地关联表，讯易链走洞察平台，判定与分流见 [[calibers/project-ledger-source]]。
- 立项统计域：以 data_source 区分 MANUAL（模拟立项，spNo 以 MN 开头）与 WECHAT（真实立项），见 [[processes/project-data-source]]、[[tables/wechat_project_approval_apply]]、[[rules/manual-project-spno]]。

两者共用「数据来源」这一中文表述，但一个描述「数据从哪个系统来」，另一个描述「单据由谁生成」，因此必须按表/页面域区分，不能合并为一个枚举。

## 版本演进

立项统计域的 data_source 是在模拟立项能力引入后出现的（MANUAL 值），项目台账域的 source 则是更早的渠道分流判定；两域长期并行，未做术语拆名。

配套歧义：productCode（ACFLOW/RVSFACTOR_PC/BEECREDIT 等）实际被写入 [[tables/cust_project_rel]] 的 remark 列，容易与「来源/产品」两词混淆。