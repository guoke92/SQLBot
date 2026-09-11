---
type: caliber
title: 项目台账 source 判定口径
page_key: caliber.project-ledger-source
domain: 项目报表/统计/上报
status: draft
aliases:
  - source 判定
  - 产融/讯易链分流
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportApplication.java
contract_version: "0.1"
---

# 项目台账 source 判定口径

项目台账的 source 由交易平台列直接判定：`transaction_platform = '产融平台'` 即为产融，否则归为讯易链。该判定决定详情、导出、关联企业查询是读本地表还是调洞察平台。

## 需求背景

产融与讯易链两套系统的企业、角色数据模型不同，因此必须在入口处分流：产融走本地关联表（见 [[calibers/chanyong-related-company]]），讯易链走洞察平台并需做角色与认证状态的跨源映射（见 [[calibers/company-type-cross-source-mapping]]、[[calibers/cust-build-status-xyc-mapping]]）。该词与立项统计侧的「数据来源」同名异义，见 [[concepts/data-source]]。

## 版本演进

以白名单式判定（等于产融平台则产融，否则讯易链）意味着新增交易平台会被默认归入讯易链，属需要关注的隐式默认；未观察到判定条件的其他版本。

```ground:caliber
name: "项目台账 source 判定口径"
predicate: "transaction_platform = '产融平台' → source='产融'；否则 source='讯易链'"
scope: "详情/导出/关联企业查询的本地表 vs 洞察平台分流"
evidence: "code_path:ProjectReportApplication.java:exportProjectReport（source 判定段）"
```