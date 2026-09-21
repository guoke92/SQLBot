---
type: process
title: 企业生效状态机
page_key: cust_company_info__cust_status
belong: processes
domain: cust
status: draft
anchors: [cust_company_info.cust_status]
field_targets: [cust_company_info.cust_status]
sources: ['code_path:CustCompanyInfoDao.java:58', 'code_path:CustSyncEventProcessor.java:1052',
  'code_path:CustCompanyInfoApplication.java:7348', 'code_path:CustSyncEventProcessor.java:1194',
  'code_path:CustCompanyInfoApplication.java:712', 'code_path:CustCompanyInfoApplication.java:678',
  'code_path:CustCompanyInfoApplication.java:723', 'code_path:CustCompanyInfoApplication.java:901']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info, cust_role_info, cust_company_lifecycle_info]
---

# 企业生效状态机

钉 cust_company_info.cust_status。与建档状态机是两条轨道。
BUILD_SUCCESS 不等于 EFFECT：列表「生效企业」必须两列同时满足。简易确认共写；运营建档回调先写建档成功再 effectCust。


```ground:process
process: 企业生效状态机
field: cust_company_info.cust_status
entry: confirmCustInfoForSimpleAuth
stages:
- stage: 生效
  transitions:
  - from: ADD
    event: 简易认证客户确认
    to: EFFECT
    evidence: code_path:CustCompanyInfoDao.java:58
  - from: ADD
    event: 运营建档回调 effectCust
    to: EFFECT
    guards: updateCustBuildStatus 返回 BUILD_SUCCESS
    evidence: code_path:CustSyncEventProcessor.java:1052
- stage: 变更
  transitions:
  - from: EFFECT
    event: 发起变更
    to: CHANGE
    evidence: code_path:CustCompanyInfoApplication.java:7348
  - from: CHANGE
    event: 变更审核通过
    to: EFFECT
    evidence: code_path:CustSyncEventProcessor.java:1194
- stage: 冻结
  trigger: freeze
  transitions:
  - from: EFFECT
    event: 冻结企业
    to: FREEZE
    guards: 当前 cust_status 须为 EFFECT 或 ADD
    evidence: code_path:CustCompanyInfoApplication.java:712
  - from: ADD
    event: 冻结企业
    to: FREEZE
    evidence: code_path:CustCompanyInfoApplication.java:678
  - from: FREEZE
    event: 解冻企业
    to: EFFECT
    evidence: code_path:CustCompanyInfoApplication.java:723
  effects:
  - op: 同步写成 FREEZE；已 WRITEOFF 的角色跳过
    table: cust_role_info
    fields: [status]
  - op: 列表冻结入口写成 FRZ 并落 reason/attach
    table: cust_company_lifecycle_info
    fields: [type]
  - op: 同步写成 EFFECT；已 WRITEOFF 的角色跳过
    table: cust_role_info
    fields: [status]
- stage: 注销
  trigger: diable
  transitions:
  - from: EFFECT
    event: 注销企业
    to: WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java:901
  effects:
  - op: 同步写成 WRITEOFF；已 WRITEOFF 的角色跳过
    table: cust_role_info
    fields: [status]
```

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_company_lifecycle_info]]
- [[tables/cust_role_info]]
- [[dicts/cust_company_info__cust_status]]
