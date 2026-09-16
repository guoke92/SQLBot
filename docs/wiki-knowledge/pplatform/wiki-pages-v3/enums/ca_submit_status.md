---
type: enum
title: ca_submit_status
page_key: ca_submit_status
domain: CA证书认证
status: draft
aliases: [上送状态]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaSubmitStatusEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [ca_submit_status_flow]
---

# ca_submit_status

[[ca_certification_info]] 的 `submit_status`。`CaSubmitStatusEnum` 无 displayName，label 取枚举常量 Javadoc。流转见 [[ca_submit_status_flow]]。

不是企业 [[open_status]]（`ca_register_status`），也不是收费侧 [[ca_status]]。

```ground:enum
enum: ca_submit_status
fields: [ca_certification_info.submit_status]
values:
  "PENDING":
    label: "创建后未提交、或正在采集各 JSON 列"
  "SUCCESS":
    label: "cbsSubmitBizData 成功并已回写"
  "FAIL":
    label: "cbsSubmitBizData 失败 / 超时 / 业务校验未通过"
```
