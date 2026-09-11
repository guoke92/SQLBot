---
type: rule
title: 拦截场景规则
page_key: rules/intercept_scene_rule
domain: CA证书收费
status: draft
aliases: [block_scene_list 规则, doCheckFeePayment]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeePaymentCheckApplication.java:doCheckFeePayment
contract_version: "0.1"
---

# 拦截场景规则

## 业务定位

**需缴费且需要拦截时，只有当前请求的 `interceptScene` 命中项目配置的 `block_scene_list` 才真正拦截；否则放行**。

这条规则把"企业欠费"与"此刻是否阻断业务"解耦：欠费企业可以照常使用未被列入拦截场景的功能。项目侧的配置载体见[[tables/ca_fee_project_config]]。

排查"为什么欠费却没被拦"时，应先确认该项目 `block_scene_list` 是否包含当前场景，再确认[[rules/chargeable_company_role_rule|收费对象规则]]与[[rules/multi_project_exemption_rule|多项目豁免规则]]的结论。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

决定业务节点是否被阻断。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 拦截场景规则
content: 需缴费时，仅当项目配置的 block_scene_list 包含当前请求的 interceptScene 才拦截；否则放行。
impact: 决定业务节点是否被阻断。
field_targets: [ca_fee_project_config.block_scene_list]
evidence: "code_path:CaFeePaymentCheckApplication.java:doCheckFeePayment"
```