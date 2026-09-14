---
type: caliber
title: 口径：上线审批中
page_key: approval_running
domain: 租户项目
status: draft
aliases: [上线审批中]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectBusinessConfigApplication
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_project_approval]] 中处于审批中的记录，取值为 RUNNING（见 [[project_approval_wf_status]]）。业务配置处理只处理该口径的数据。

## 需求背景
语义分析未附带需求文档锚点；只有审批中的项目才需要同步处理业务配置。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 上线审批中
predicate: "tenant_project_approval.wf_status = 'RUNNING'"
scope: tenant_project_approval
evidence: "code:ProjectBusinessConfigApplication 只处理 RUNNING"
```