---
type: dict
title: ca_certification_info.data_source
page_key: ca_certification_info__data_source
belong: dicts
status: draft
anchors: [ca_certification_info.data_source]
sources: ['database_profile:ca_certification_info.data_source']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [ca_certification_info]
---

# ca_certification_info.data_source

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `ca_certification_info.data_source`，表页 [[tables/ca_certification_info]]。

## 取值

```ground:dict
dict: ca_certification_info__data_source
fields: [ca_certification_info.data_source]
values:
  FBP_PORTAL: {trust: proposed}
  OPERATION_PLATFORM: {trust: proposed}
  CHANNEL_OPENAPI: {trust: proposed}
triage: hold
needs_review: true
```
