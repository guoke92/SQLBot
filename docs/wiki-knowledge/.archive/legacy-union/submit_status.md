---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: CA报数状态
page_key: submit_status
domain: CA认证与服务费
aliases:
- CA认证状态
- 报数成功
- 报数失败
- 报数状态
- 签章中心提交状态
- 报数成功
- 报数失败
anchors:
- submit_status
---
# CA报数状态

ca_certification_info.submit_status 三值状态机：PENDING 采集未提交 → SUCCESS（cbsSubmitBizData 成功：DBaaS code∈{'0','200'} AND biz.status=SAVED 双条件）或 FAIL（可重试）。已 SUCCESS 短路不再上送；markFailed 对已 SUCCESS 行禁止置 FAIL。幂等键 (custId, dataDate, headCompanyData, PENDING)。

```ground:enum
enum: submit_status
fields:
- ca_certification_info.submit_status
values:
  PENDING:
    label: 采集/未提交
  SUCCESS:
    label: 报数成功
  FAIL:
    label: 报数失败（可重试）
```

## 关联
- [[ca_certification_info|ca_certification_info]]
