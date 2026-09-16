---
type: process
title: 企业产品开通状态机
page_key: cust_product_active_flow
domain: 自动审核与工作流审核
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets:
  - cust_auth_application.open_status
---

提交建档进入 OPENING，开通完成 OPENED。

```ground:process
name: 企业产品开通状态机
field: cust_auth_application.open_status
states:
  - value: NOT_OPENED
    label: 未开通
    source: code_enum
  - value: OPENING
    label: 开通中
    source: code_enum
  - value: OPENED
    label: 已开通
    source: code_enum
transitions:
  - from: NOT_OPENED
    event: 提交开通
    to: OPENING
    evidence: "code_path:SubmitCustInfoEnhanceService.java:148"
  - from: OPENING
    event: 开通完成
    to: OPENED
    evidence: "code_path:CustProductDomainService.java:1096"
```
