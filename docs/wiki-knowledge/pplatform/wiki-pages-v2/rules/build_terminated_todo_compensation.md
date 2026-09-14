---
type: rule
title: 未拉起中台流程时的待办补偿
page_key: build_terminated_todo_compensation
domain: 外部渠道与银行对接
status: draft
aliases:
  - 终止建档待办关单
  - NOTICE_TASK_INVITE_AUTH_CUST_INPUT
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.completeBuildTerminatedWithoutOperTodos
contract_version: "0.1"
belong: rules
---

终止建档且 hasOperFlow=false 时，按 identify_style 映射待办场景主动关单，保证待办一致性。

## 需求背景
映射关系为 INVITE→NOTICE_TASK_INVITE_AUTH_CUST_INPUT、INVITE_AGW→NOTICE_TASK_INVITE_AUTH_SYS_INPUT、其余→NOTICE_COMPANY_BUILD_AUTH。identify_style 取值见 [[cust_company_info]]，终止后的状态走向见 [[cust_build_status]] 与 [[cust_check_status]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 未拉起中台流程时的待办补偿
content: 终止建档且 hasOperFlow=false 时按 identify_style 映射待办场景（INVITE→NOTICE_TASK_INVITE_AUTH_CUST_INPUT，INVITE_AGW→NOTICE_TASK_INVITE_AUTH_SYS_INPUT，其余→NOTICE_COMPANY_BUILD_AUTH）主动关单
impact: 渠道建档终止后的待办一致性
field_targets:
  - cust_company_info.identify_style
evidence: "code:CustAccessApplication.completeBuildTerminatedWithoutOperTodos"
```