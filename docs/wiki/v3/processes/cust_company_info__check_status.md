---
type: process
title: 运营审核状态
page_key: cust_company_info__check_status
belong: processes
domain: cust
status: draft
anchors: [cust_company_info.check_status]
field_targets: [cust_company_info.check_status]
sources: ['code_path:CustCompanyInfoApplication.java:7350', 'code_path:CustSyncEventProcessor.java:2080',
  'code_path:CustSyncEventProcessor.java:2033', 'code_path:CustSyncEventProcessor.java:2064']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# 运营审核状态

钉 cust_company_info.check_status，码来自 OperApiConstants.CheckStatus。
与 cust_build_status 有映射（getCheckStatusByCustBuildStatus / getCustBuildStatus）但不是同一列。
库里偶发 EFFECT 不是本枚举成员，不要当审核通过。


```ground:process
process: 运营审核状态
field: cust_company_info.check_status
entry: CustSyncEventProcessor.updateCustBuildStatus
stages:
- stage: 发起变更
  transitions:
  - from: CUST_CHECK_PASS
    event: 企业自行变更
    to: CUST_CHECK_INIT
    evidence: code_path:CustCompanyInfoApplication.java:7350
- stage: 运营回写
  transitions:
  - from: CUST_CHECK_CHECKING
    event: 回调 check_status
    to: CUST_CHECK_PASS
    evidence: code_path:CustSyncEventProcessor.java:2080
  - from: CUST_CHECK_CHECKING
    event: 退回客户
    to: CUST_CHECK_BACKTOCUSTOM
    evidence: code_path:CustSyncEventProcessor.java:2033
  - from: CUST_CHECK_CHECKING
    event: 审核拒绝
    to: CUST_CHECK_REJECT
    evidence: code_path:CustSyncEventProcessor.java:2064
```

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__check_status]]
