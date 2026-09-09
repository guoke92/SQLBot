---
type: rule
title: CA/BS开通后同步至业务系统
page_key: ca_bs_sync_after_open
belong: rules
domain: 租户迁移
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# CA/BS开通后同步至业务系统

业务定位：开通电子签章后，发送事件将签章状态同步至第三方业务系统。

## 需求背景

开通签章后，系统发送 `ACTIVE_CFCA_SIGN` 或 `ACTIVE_BS_SIGN` 事件，产品码按需包含 AMS，确保下游系统能够及时获取签章状态。

## 版本演进

暂无。

```ground:rule
name: CA/BS开通后同步至业务系统
content: 开通签章后发送 ACTIVE_CFCA_SIGN/ACTIVE_BS_SIGN 事件，产品码按需包含 AMS
impact: 签章状态同步到第三方业务系统
field_targets:
  - CustCompanyInfoDO.caRegisterStatus
  - CustCompanyInfoDO.bsRegisterStatus
evidence: code_path:CustCompanyInfoApplication.java:submitForSimpleAuth / CustCompanyIfoEnchanceService.java:setEventNode
```