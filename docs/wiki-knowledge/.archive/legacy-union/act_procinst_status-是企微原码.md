---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:wechat-project-initiation@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: act_procinst_status 是企微原码
page_key: act_procinst_status-是企微原码
domain: 项目审批
field_targets:
- wechat_project_approval_apply.act_procinst_status
---
# act_procinst_status 是企微原码

act_procinst_status 存企微 sp_status 原始码值（1/2/3/4/6/7），不是中文。 "审批通过"=act_procinst_status='2'（EXPORT_REQUIRED_ACT_PROCINST_STATUS 常量）。

```ground:rule
rule: sp-status-meaning
field_targets:
- wechat_project_approval_apply.act_procinst_status
impact: query_constraint
content: act_procinst_status 存企微 sp_status 原始码值（1/2/3/4/6/7），不是中文。 "审批通过"=act_procinst_status='2'（EXPORT_REQUIRED_ACT_PROCINST_STATUS
  常量）。
scope: 按立项状态过滤/统计
```

## 关联
- [[wechat_project_approval_apply]]
