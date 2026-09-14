---
type: rule
title: 项目导入字段长度限制
page_key: import_length_limits
domain: 租户项目
status: draft
aliases: [导入长度限制, bussiness_project_relation 50, invite_customer_service_words 500]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
contract_version: "0.1"
belong: rules
---

该规则规定 [[tables/tenant_project]] 导入时两个长文本字段的上限：运营项目归属不超过 50，邀请信息-客服话术不超过 500。超出时导入应被拒绝。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则与同表的对接人转换规则一起构成导入校验集合，见 [[concepts/op_contact]]。

## 版本演进
长度上限仅在导入侧校验，库端约束未知；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 项目导入长度限制
table: tenant_project
fields: [bussiness_project_relation, invite_customer_service_words]
statement: 运营项目归属导入长度限制不超过 50；邀请信息-客服话术导入时长度限制不超过 500
evidence: code
```