---
type: caliber
title: 口径：项目待生效
page_key: project_to_be_effective
domain: 租户项目
status: draft
aliases: [项目待生效, 待生效项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectStatusEnum
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_project]] 中已创建但尚未生效的项目，对应 [[ProjectStatusEnum]] 的 0，流转见 [[tenant_project_status]]。

## 需求背景
语义分析未附带需求文档锚点；待生效项目需经生效动作或上线审批通过后才进入 [[project_effective]]。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 项目待生效
predicate: "tenant_project.project_status = '0'"
scope: tenant_project
evidence: "code:ProjectStatusEnum.TO_BE_EFFECTIVE"
```