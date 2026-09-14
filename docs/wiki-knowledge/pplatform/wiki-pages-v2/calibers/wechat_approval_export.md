---
type: caliber
title: 企微审批导出硬过滤
page_key: wechat_approval_export
domain: 微企链立项与项目审批
status: draft
aliases:
  - 企微审批导出范围
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:WechatProjectApprovalApplication.java:exportWechatApprovalInfo
contract_version: "0.1"
belong: calibers
---

导出企微审批申请信息的固定数据范围：只导出已通过且来源为企微同步的记录。该过滤由后端硬编码，前端查询条件无法改写，用于把「审批中的申请」和「手工模拟立项」排除在导出结果之外。

```ground:caliber
name: 企微审批导出硬过滤
predicate: wechat_project_approval_apply.act_procinst_status = '2' AND wechat_project_approval_apply.data_source = 'WECHAT'
scope: 导出企微审批申请信息
evidence: code_path:WechatProjectApprovalApplication.java:exportWechatApprovalInfo
```

## 需求背景

对应的固化规则见 [[rules/wechat_approval_export_hard_filter]]。口径依赖的两个字段取值见 [[processes/wechat_apply_approval_status]] 与 [[concepts/data_source]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。