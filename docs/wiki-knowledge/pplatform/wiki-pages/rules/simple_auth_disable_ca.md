---
type: rule
title: 简易认证禁止开通CA
page_key: simple_auth_disable_ca
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

# 简易认证禁止开通CA

业务定位：在简易认证提交时，强制校正电子签章开通标记为关闭，避免简易建档开通电子签章。

## 需求背景

若提交时 `needRegisterCa=Y`，系统强制校正为不开放（`needRegisterCa=N`），并同步调整 `caRegisterStatus` 与 `bsRegisterStatus` 后落库，防止简易认证场景误开签章。

## 版本演进

暂无。

```ground:rule
name: 简易认证禁止开通CA
content: 简易认证提交时若 needRegisterCa=Y，强制校正为不开放（needRegisterCa=N，caRegisterStatus/bsRegisterStatus 对应调整）并落库
impact: 避免简易建档开通电子签章
field_targets:
  - CustCompanyInfoDO.needRegisterCa
  - CustCompanyInfoDO.caRegisterStatus
  - CustCompanyInfoDO.bsRegisterStatus
evidence: code_path:CustCompanyInfoApplication.java:submitForSimpleAuth
```