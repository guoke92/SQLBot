---
type: process
title: 企业建档状态机
page_key: cust_company_info__cust_build_status
belong: processes
domain: cust
status: draft
anchors: [cust_company_info.cust_build_status]
field_targets: [cust_company_info.cust_build_status]
sources: ['code_path:CustCompanyInfoApplication.java:2028', 'code_path:CustCompanyInfoApplication.java:948',
  'code_path:CustCompanyInfoApplication.java:1963', 'code_path:CustCompanyInfoApplication.java:1967',
  'code_path:CustCompanyInfoApplication.java:1603', 'code_path:CustSyncEventProcessor.java:2048',
  'code_path:CustSyncEventProcessor.java:2050', 'code_path:CustSyncEventProcessor.java:2057',
  'code_path:CustSyncEventProcessor.java:2073', 'code_path:CustCompanyInfoApplication.java:7348',
  'code_path:CustSyncEventProcessor.java:1194', 'code_path:CustSyncEventProcessor.java:2075']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# 企业建档状态机

钉 cust_company_info.cust_build_status。邀请/自主提交按 identify_style 分叉；运营回调再写 check_status 并可能共写本列。
简易认证不走 CUST_BUILDING。变更轨把本列写成 CUST_CHANGE，与 cust_status.CHANGE、check_status.CUST_CHECK_INIT 共写。
不要把 identify_style / cust_build_type 编成流转。


```ground:process
process: 企业建档状态机
field: cust_company_info.cust_build_status
entry: POST /cust-web/custInfo/submitCust
stages:
- stage: 简易认证提交
  trigger: 运营提交简易建档
  transitions:
  - from: INIT
    event: simpleSubmit → submitForSimpleAuth
    to: AWAIT_CUST_CONFIRM
    guards: 非变更补录且当前不是 BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java:2028
- stage: 简易认证客户确认
  trigger: 客户确认企业信息
  transitions:
  - from: AWAIT_CUST_CONFIRM
    event: confirmCustInfoForSimpleAuth
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java:948
  effects:
  - op: 置为 EFFECT（与建档状态共写）
    table: cust_company_info
    fields: [cust_status]
- stage: 邀请/自主提交
  trigger: POST /cust-web/custInfo/submitCust
  transitions:
  - from: INIT
    event: submitCust identify_style=INVITE_AGW
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java:1963
  - from: INIT
    event: submitCust identify_style=INVITE|SELF
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:1967
  - from: BUILD_FAIL
    event: 邀请认证拒绝后再次 submitCust
    to: CUST_CONFIRM_AWAIT
    guards: identify_style=INVITE
    evidence: code_path:CustCompanyInfoApplication.java:1603
- stage: 运营建档回调
  trigger: CustSyncEventProcessor.checkHandler
  transitions:
  - from: CUST_BUILDING
    event: check_status=CUST_CHECK_BACKTOCUSTOM
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustSyncEventProcessor.java:2048
  - from: CUST_CONFIRM_AWAIT
    event: check_status=CUST_CHECK_CHECKING
    to: CUST_BUILDING
    evidence: code_path:CustSyncEventProcessor.java:2050
  - from: CUST_BUILDING
    event: check_status=CUST_CHECK_PASS
    to: BUILD_SUCCESS
    evidence: code_path:CustSyncEventProcessor.java:2057
  - from: CUST_BUILDING
    event: check_status=CUST_CHECK_REJECT 且 process=CHECK
    to: BUILD_FAIL
    evidence: code_path:CustSyncEventProcessor.java:2073
  effects:
  - op: 置为 CUST_CHECK_BACKTOCUSTOM
    table: cust_company_info
    fields: [check_status]
  - op: effectCust 仅在 after=BUILD_SUCCESS 时另写 EFFECT
    table: cust_company_info
    fields: [cust_status]
  - op: 置为 CUST_CHECK_PASS
    table: cust_company_info
    fields: [check_status]
- stage: 企业变更
  trigger: 发起变更 / 变更审核通过
  transitions:
  - from: BUILD_SUCCESS
    event: 企业自行变更
    to: CUST_CHANGE
    evidence: code_path:CustCompanyInfoApplication.java:7348
  - from: CUST_CHANGE
    event: 变更审核通过 check_status=CUST_CHECK_PASS
    to: BUILD_SUCCESS
    evidence: code_path:CustSyncEventProcessor.java:1194
  - from: CUST_CHANGE
    event: 变更审核拒绝 process=CHANGE
    to: BUILD_SUCCESS
    evidence: code_path:CustSyncEventProcessor.java:2075
  effects:
  - op: 置为 CHANGE
    table: cust_company_info
    fields: [cust_status]
  - op: 置为 CUST_CHECK_INIT
    table: cust_company_info
    fields: [check_status]
  - op: 置为 EFFECT
    table: cust_company_info
    fields: [cust_status]
  - op: 置为 CUST_CHECK_PASS
    table: cust_company_info
    fields: [check_status]
```

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__cust_build_status]]
