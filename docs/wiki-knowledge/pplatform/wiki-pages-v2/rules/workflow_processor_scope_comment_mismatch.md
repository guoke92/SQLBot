---
type: rule
title: "工作流执行器实际处理范围与注释不一致"
page_key: "rules/workflow_processor_scope_comment_mismatch"
domain: "customer-onboarding"
status: draft
aliases:
  - "注释与实现不一致"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustWorkflowAuditCommitProcessor.java:process"
contract_version: "0.1"
---

执行器注释写「仅处理拒绝，中间状态不处理」，但代码的实际守卫条件是「既非通过、也非拒绝才 return」，因此通过和拒绝都会进入处理逻辑。阅读与排障时应以代码为准，不要依据注释推断处理范围。相关入口规则见 [[rules/workflow_callback_routing]]。

## 需求背景

需求文档要求审核通过后企业状态变为已通过；该能力正是由本执行器实现，注释滞后于实现。

## 版本演进

- 该差异属于历史注释未同步，尚未见修复；若后续以「按注释重构」的方式收敛，处理范围可能变化，需回归验证 [[processes/company_build_status_machine]]。

```ground:rule
name: "工作流执行器实际处理范围与注释不一致"
content: "CustWorkflowAuditCommitProcessor 注释写『仅处拒绝，中间状态不处理』，但代码判断 rtfs != RtfState.PASS && rtfs != RtfState.REJECT 才 return，实际同时处理通过和拒绝。"
impact: "注释与实现存在差异，阅读时需以代码为准"
field_targets:
  - "cust_company_info.check_status"
evidence: "code_path:CustWorkflowAuditCommitProcessor.java:process"
```

相关：[[processes/workflow_check_status_machine]]、[[rules/workflow_callback_routing]]。