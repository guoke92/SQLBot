---
type: process
title: 一证四步提交状态
page_key: ca_certification_info__submit_status
belong: processes
domain: ca_fee
status: draft
anchors: [ca_certification_info.submit_status]
field_targets: [ca_certification_info.submit_status]
sources: ['code_path:CaCertificationInfoAppServiceImpl.java:178', 'code_path:CaCertificationInfoAppServiceImpl.java:495',
  'code_path:CaCertificationInfoAppServiceImpl.java:451']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_certification_info]
---

# 一证四步提交状态

新建 PENDING；提交签章中台后写 SUCCESS 或 FAIL。

```ground:process
process: 一证四步提交状态
field: ca_certification_info.submit_status
entry: POST /cust-web/ca
stages:
- stage: 采集
  transitions:
  - from: PENDING
    event: createOrGetByKey
    to: PENDING
    evidence: code_path:CaCertificationInfoAppServiceImpl.java:178
- stage: 提交
  transitions:
  - from: PENDING
    event: writeSubmitResult 成功
    to: SUCCESS
    evidence: code_path:CaCertificationInfoAppServiceImpl.java:495
  - from: PENDING
    event: writeSubmitResult 失败
    to: FAIL
    evidence: code_path:CaCertificationInfoAppServiceImpl.java:451
```

## 页面链接

- [[tables/ca_certification_info]]
- [[dicts/ca_certification_info__submit_status]]
