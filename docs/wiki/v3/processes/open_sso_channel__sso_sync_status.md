---
type: process
title: SSO渠道同步状态
page_key: open_sso_channel__sso_sync_status
belong: processes
domain: remaining
status: draft
anchors: [open_sso_channel.sso_sync_status]
field_targets: [open_sso_channel.sso_sync_status]
sources: ['code_path:OpenSsoChannelSyncJobHandle.java:61', 'code_path:OpenSsoChannelSyncJobHandle.java:64',
  'code_path:OpenSsoChannelSyncJobHandle.java:69', 'code_path:OpenSsoChannelSyncJobHandle.java:65']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [open_sso_channel]
---

# SSO渠道同步状态

钉 open_sso_channel.sso_sync_status：PENDING → SYNCED / FAILED（OpenSsoSyncStatus，无中文 displayName）。
PENDING 在本列=待同步到 SSO，不是电子授权待签署，也不是审批待发起。


```ground:process
process: SSO渠道同步状态
field: open_sso_channel.sso_sync_status
entry: OpenSsoChannelSyncJobHandle
stages:
- stage: 待同步
  transitions:
  - from: ''
    event: 写入/重置同步
    to: PENDING
    evidence: code_path:OpenSsoChannelSyncJobHandle.java:61
- stage: 同步结果
  transitions:
  - from: PENDING
    event: 同步成功
    to: SYNCED
    evidence: code_path:OpenSsoChannelSyncJobHandle.java:64
  - from: FAILED
    event: 批量重试扫描
    to: PENDING
    evidence: code_path:OpenSsoChannelSyncJobHandle.java:69
  - from: PENDING
    event: 同步失败
    to: FAILED
    evidence: code_path:OpenSsoChannelSyncJobHandle.java:65
```

## 页面链接

- [[tables/open_sso_channel]]
- [[dicts/open_sso_channel__sso_sync_status]]
