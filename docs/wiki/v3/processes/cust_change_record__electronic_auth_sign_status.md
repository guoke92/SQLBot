---
type: process
title: 电子授权书签署状态（建档/变更共用）
page_key: cust_change_record__electronic_auth_sign_status
belong: processes
domain: cust
status: draft
anchors: [cust_change_record.electronic_auth_sign_status]
field_targets: [cust_change_record.electronic_auth_sign_status]
sources: ['code_path:ChannelChangeDirectRecordService.java:152', 'code_path:OfflineElectronicAuthCompensationJobHandler.java:26',
  'code_path:OfflineElectronicAuthCompensationJobHandler.java:30', 'code_path:ChannelChangeDirectRecordService.java:93']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_change_record]
---

# 电子授权书签署状态（建档/变更共用）

钉 cust_change_record / cust_build_record.electronic_auth_sign_status，共用 ElectronicAuthSignStatus。
补偿任务扫描 PENDING/UPLOAD_FAILED；VOIDED 仅直推变更被新流水覆盖时写入，补偿不拾取。
PENDING 在本列=待签署，不是审批 wf_status.PENDING。


```ground:process
process: 电子授权书签署状态（建档/变更共用）
field: cust_change_record.electronic_auth_sign_status
entry: OfflineElectronicAuthCompensationJobHandler
stages:
- stage: 待签署
  transitions:
  - from: ''
    event: 直推需重签落库
    to: PENDING
    evidence: code_path:ChannelChangeDirectRecordService.java:152
- stage: 补偿签署
  transitions:
  - from: PENDING
    event: 补偿任务成功
    to: SIGNED
    evidence: code_path:OfflineElectronicAuthCompensationJobHandler.java:26
  - from: UPLOAD_FAILED
    event: 补偿任务重试上传
    to: SIGNED
    evidence: code_path:OfflineElectronicAuthCompensationJobHandler.java:26
  - from: PENDING
    event: 签章失败
    to: FAILED
    evidence: code_path:OfflineElectronicAuthCompensationJobHandler.java:30
  - from: PENDING
    event: 签章成功但影像上传失败
    to: UPLOAD_FAILED
    evidence: code_path:OfflineElectronicAuthCompensationJobHandler.java:30
- stage: 作废
  transitions:
  - from: PENDING
    event: 直推新流水覆盖在途变更
    to: VOIDED
    evidence: code_path:ChannelChangeDirectRecordService.java:93
```

## 页面链接

- [[tables/cust_change_record]]
- [[dicts/cust_change_record__electronic_auth_sign_status]]
