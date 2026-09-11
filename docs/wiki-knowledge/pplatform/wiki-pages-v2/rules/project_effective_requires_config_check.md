---
type: rule
title: 项目生效前的配置校验
page_key: rules/project_effective_requires_config_check
domain: 租户项目
status: draft
aliases: [config_json 校验, BEECREDIT 生效校验]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
contract_version: "0.1"
---

该规则规定 [[tables/tenant_project]] 的 config_json 在生效链路中的作用：BEECREDIT 类项目在生效前需解析并校验配置状态，ACFLOW/RVSFACTOR 类项目则在生效时用其完成开户或查询业务系统配置。它使「生效」成为带前置校验的动作，见 [[processes/tenant_project_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则保证项目生效时下游业务系统所需的配置已经可用。

## 版本演进
同一列对不同产品线承担「校验」与「开户/查询」两类用途，是产品线扩展后复用同一列的结果；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 项目生效前的配置校验
table: tenant_project
fields: [config_json]
statement: BEECREDIT 生效前解析校验配置状态，ACFLOW/RVSFACTOR 生效时用于开户/查询业务系统配置
evidence: code
```