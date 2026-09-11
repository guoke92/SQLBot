---
type: rule
title: 工作流启动失败降级停留在待发起
page_key: rule/workflow-start-failure-degrade
domain: 微企链立项与项目审批
status: draft
aliases:
  - 启动异常仅记 ERROR
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#startWorkflowAndUpdateStatus
contract_version: "0.1"
---

业务落库与工作流引擎启动是两步：先落库（此时状态为待发起），再启动工作流并把状态改为审批中。若引擎启动抛异常，系统只记 ERROR 日志并保持待发起，不阻塞业务代码，也不回滚业务落库——结果就是一条「看起来提交成功但流程没走起来」的单据。

对应的自环transition见 [[processes/project-approval-workflow-status]]；`initiate_time` 只在启动成功时写入，可作为判断是否真的启动过的旁证。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 工作流启动失败降级停留在待发起
subject: tenant_project_approval.wf_status
evidence: code
source_meaning: 上线审批工作流状态（PENDING/RUNNING/FINISHED/TERMINATED；DB 另有 REVOKED）
```