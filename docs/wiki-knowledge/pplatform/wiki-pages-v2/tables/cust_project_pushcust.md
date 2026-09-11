---
type: table
title: 推送企业表（cust_project_pushcust）
page_key: table.cust_project_pushcust
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_pushcust
  - 推送企业表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:cust_project_pushcust
contract_version: "0.1"
---

# 推送企业表（cust_project_pushcust）

cust_project_pushcust 记录「推送企业」与其默认项目之间的跨系统跳转链路。它不承载报表指标，而是为项目台账/企业视图提供 SSO 侧的系统归属，使「推送企业的默认项目」能够从起始系统渠道跳转至目标系统渠道。相关概念歧义见 [[concepts/data-source]]。

## 需求背景

推送企业的默认项目需要在不同系统之间跳转：用户在起始系统的 SSO 渠道点击后，需要被引导到目标系统渠道。本表以「起始渠道 → 目标渠道」成对的字段承载该链路，因此在报表/台账侧只作为跳转参数来源，不参与统计口径计算（统计口径见 [[calibers/project-statistics-list-base]]）。

## 版本演进

语义分析未提供该表的历史值分布与迁移记录，字段值域仅由代码侧使用方式反推，暂无版本演进证据。

```ground:fields
table: cust_project_pushcust
fields:
  - name: "source_sso_channel / target_sso_channel"
    meaning: "SSO 起始系统渠道 → 跳转系统渠道，表征「推送企业的默认项目」的跨系统跳转链路"
    evidence: code
```