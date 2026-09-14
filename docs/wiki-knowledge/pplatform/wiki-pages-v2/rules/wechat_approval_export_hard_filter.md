---
type: rule
title: 企微审批导出硬过滤
page_key: wechat_approval_export_hard_filter
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:WechatProjectApprovalApplication.java:exportWechatApprovalInfo
contract_version: "0.1"
belong: rules
---

企微审批数据导出时被固化的过滤条件，属于不可被前端查询条件改写的硬约束。

```ground:rule
name: 企微审批导出硬过滤
content: 导出企微审批申请时，固定过滤 act_procinst_status=2 且 data_source=WECHAT，前端查询条件不能改写该过滤。
impact: 确保只导出已通过的企微同步记录。
field_targets:
  - wechat_project_approval_apply.act_procinst_status
  - wechat_project_approval_apply.data_source
evidence: code_path:WechatProjectApprovalApplication.java:exportWechatApprovalInfo
```

## 需求背景

与之对应的数据范围口径见 [[calibers/wechat_approval_export]]；两个过滤字段的取值含义见 [[processes/wechat_apply_approval_status]] 与 [[concepts/data_source]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。