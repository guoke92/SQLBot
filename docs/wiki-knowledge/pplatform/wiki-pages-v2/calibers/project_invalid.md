---
type: caliber
title: 口径：项目已失效
page_key: project_invalid
domain: 租户项目
status: draft
aliases: [项目已失效, 已失效项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectStatusEnum
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_project]] 中已失效的项目，对应 [[ProjectStatusEnum]] 的 2（常量名 INVLIAD 为代码原文拼写）。失效项目在上线审批终态通过后可重新生效，见 [[tenant_project_status]]。

## 需求背景
语义分析未附带需求文档锚点；项目失效采用状态标记而非删除，以支持重新生效与历史追溯。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 项目已失效
predicate: "tenant_project.project_status = '2'"
scope: tenant_project
evidence: "code:ProjectStatusEnum.INVLIAD"
```