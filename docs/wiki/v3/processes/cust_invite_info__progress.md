---
type: process
title: 邀请进度
page_key: cust_invite_info__progress
belong: processes
domain: cust
status: draft
anchors: [cust_invite_info.progress]
field_targets: [cust_invite_info.progress]
sources: ['code_path:CustCompanyIfoEnchanceService.java:1586', 'code_path:CustSyncEventProcessor.java:1128']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_invite_info]
---

# 邀请进度

钉 cust_invite_info.progress。邀请落库写成 INIT。
运营回调 updateInviteCustProcess 把 progress 写成被邀请企业当前 cust_build_status，匹配条件是 name+db_tenant_code，不是 invite_cust_id，也不是 EQUI_JOIN。


```ground:process
process: 邀请进度
field: cust_invite_info.progress
entry: CustCompanyIfoEnchanceService.inviteSave
stages:
- stage: 发出邀请
  transitions:
  - from: ''
    event: inviteSave
    to: INIT
    evidence: code_path:CustCompanyIfoEnchanceService.java:1586
- stage: 同步建档状态
  trigger: updateInviteCustProcess
  transitions:
  - from: INIT
    event: 回调按企业名称+租户回写 progress
    to: BUILD_SUCCESS
    evidence: code_path:CustSyncEventProcessor.java:1128
```

## 页面链接

- [[tables/cust_invite_info]]
- [[dicts/cust_invite_info__progress]]
