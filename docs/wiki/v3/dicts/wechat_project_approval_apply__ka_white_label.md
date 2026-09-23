---
type: dict
title: wechat_project_approval_apply.ka_white_label
page_key: wechat_project_approval_apply__ka_white_label
belong: dicts
status: draft
anchors:
- wechat_project_approval_apply.ka_white_label
sources:
- database_profile:wechat_project_approval_apply.ka_white_label
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- wechat_project_approval_apply
---
# wechat_project_approval_apply.ka_white_label

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `wechat_project_approval_apply.ka_white_label`，表页 [[tables/wechat_project_approval_apply]]。

## 取值

```ground:dict
dict: wechat_project_approval_apply__ka_white_label
fields:
- wechat_project_approval_apply.ka_white_label
values:
  Y:
    trust: proposed
    label: 是
  N:
    trust: proposed
    label: 否
triage: keep
```
