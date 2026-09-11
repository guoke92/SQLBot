---
type: caliber
title: 企业最新成功上送记录
page_key: caliber/latest_success_submit
domain: 微信生态/小程序/扫脸
status: draft
aliases: [最新成功上送, 基准行]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# 企业最新成功上送记录

取企业最近一条成功上送并启用的 [[ca_certification_info]] 行作为基准：cust_id 匹配、submit_status=SUCCESS、enable=Y，按 submit_time、id 倒序取第一条。

## 需求背景

复用最新成功上送的报文作为业务基准（assembleLatestSuccessBizRequest / submitLatestSuccessBizRequest）。

## 版本演进

v0.1 记录基准行谓词。

```ground:caliber
name: 企业最新成功上送记录
predicate: "ca_certification_info.cust_id = ? AND submit_status = 'SUCCESS' AND enable = 'Y' ORDER BY submit_time DESC, id DESC LIMIT 1"
scope: "assembleLatestSuccessBizRequest / submitLatestSuccessBizRequest 取基准行。"
evidence: code_path:CaCertificationInfoAppServiceImpl.java#findLatestSuccessRow
```

相关：[[ca_certification_info]]、[[ca_submit_state_machine]]、[[ca_idempotent_row]]。