---
type: rule
title: 客户建档供票产品前置校验
page_key: supply_ticket_precheck
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

# 客户建档供票产品前置校验

业务定位：在客户选择供票产品建档前，执行前置条件校验，避免误开产品。

## 需求背景

选择供票产品时，客户必须满足简易认证、已开通电子签章、总公司三个条件，否则抛出异常。该规则确保供票产品开通的限制条件得以执行。

## 版本演进

暂无。

```ground:rule
name: 客户建档供票产品前置校验
content: 选择供票产品时，必须为简易认证、已开通电子签章、总公司，否则抛异常
impact: 供票产品开通限制，避免误开
field_targets:
  - CustCompanyInfoDO.identifyStyle
  - CustCompanyInfoDO.needRegisterCa
  - CustCompanyInfoDO.headCompany
evidence: code_path:CustCompanyIfoEnchanceService.java:checkCustInfoBeforeSaveForDraft
```