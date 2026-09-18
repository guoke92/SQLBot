---
type: dict
title: ca_certification_info.submit_status
page_key: ca_certification_info__submit_status
belong: dicts
status: draft
anchors: [ca_certification_info.submit_status]
sources: ['database_profile:ca_certification_info.submit_status', 'database_schema:ca_certification_info.submit_status',
  'code_path:CaSubmitStatusEnum.java:15', 'code_path:CaSubmitStatusEnum.java:12',
  'code_path:CaSubmitStatusEnum.java:18']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_certification_info]
---

# ca_certification_info.submit_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `ca_certification_info.submit_status`，表页 [[tables/ca_certification_info]]。

## 取值

```ground:dict
dict: ca_certification_info__submit_status
fields: [ca_certification_info.submit_status]
values:
  SUCCESS: {trust: confirmed, label: cbsSubmitBizData 成功并已回写 request_id / submit_time,
    evidence: 'code_path:CaSubmitStatusEnum.java:15'}
  PENDING: {trust: confirmed, label: 创建后未提交、或正在采集各 JSON 列, evidence: 'code_path:CaSubmitStatusEnum.java:12'}
  FAIL: {trust: confirmed, label: cbsSubmitBizData 失败 / 超时 / 业务校验未通过, evidence: 'code_path:CaSubmitStatusEnum.java:18'}
triage: keep
```
