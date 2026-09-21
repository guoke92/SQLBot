---
type: process
title: 直推变更单
page_key: cust_change_record__oper_channel_direct
belong: processes
domain: cust
status: draft
anchors: [cust_change_record.oper_channel]
field_targets: [cust_change_record.oper_channel]
sources: ['code_path:ChannelChangeDirectRecordService.java:148']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_change_record]
---

# 直推变更单

前置 tenant_setting_config.access_mode=DIRECT_INIT。
落库 oper_channel=DIRECT_INIT；status 写 CheckStatus；need_resign 时 electronic_auth_sign_status=PENDING 并同步企业状态。
本过程钉 oper_channel，不要当成 access_mode 列。


```ground:process
process: 直推变更单
field: cust_change_record.oper_channel
entry: ChannelChangeDirectRecordService.insertAccepted
stages:
- stage: 收单
  transitions:
  - from: ''
    event: 直推变更受理（无需重签）
    to: DIRECT_INIT
    evidence: code_path:ChannelChangeDirectRecordService.java:148
  - from: ''
    event: 直推变更受理（需重签）
    to: DIRECT_INIT
    evidence: code_path:ChannelChangeDirectRecordService.java:148
  effects:
  - op: CUST_CHECK_PASS
    table: cust_change_record
    fields: [status]
  - op: Y + electronic_auth_sign_status=PENDING + status=CUST_CHECK_BACKTOCUSTOM
    table: cust_change_record
    fields: [need_resign_auth]
```

## 页面链接

- [[tables/cust_change_record]]
- [[dicts/cust_change_record__oper_channel]]
