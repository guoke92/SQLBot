---
type: dict
title: wechat_project_approval_apply.prd
page_key: wechat_project_approval_apply__prd
belong: dicts
status: draft
anchors:
- wechat_project_approval_apply.prd
sources:
- database_profile:wechat_project_approval_apply.prd
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- wechat_project_approval_apply
---
# wechat_project_approval_apply.prd

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `wechat_project_approval_apply.prd`，表页 [[tables/wechat_project_approval_apply]]。

## 取值

```ground:dict
dict: wechat_project_approval_apply__prd
fields:
- wechat_project_approval_apply.prd
values:
  N:
    trust: proposed
    label: 否
  Y:
    trust: proposed
    label: 是
triage: keep
```
