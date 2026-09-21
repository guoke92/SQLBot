---
type: dict
title: cust_sftp.port
page_key: cust_sftp__port
belong: dicts
status: draft
anchors: [cust_sftp.port]
sources: ['database_profile:cust_sftp.port']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_sftp]
---

# cust_sftp.port

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_sftp.port`，表页 [[tables/cust_sftp]]。

## 取值

```ground:dict
dict: cust_sftp__port
fields: [cust_sftp.port]
values:
  '22': {trust: proposed}
triage: hold
needs_review: true
```
