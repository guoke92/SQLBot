---
type: caliber
title: 有效变更记录
page_key: valid_change_record
domain: 企业变更与运营变更
status: draft
aliases: [变更记录有效口径, enable=Y 记录]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: calibers
---

口径定义：读取或判定变更记录（[[cust_change_record]]）时只认 `enable = 'Y'` 的行，用于变更记录读取与跳转判定。

## 需求背景

变更记录存在作废/失效场景，入口跳转与展示必须基于有效记录，否则会把已失效的在途流程当成真实在途。

## 版本演进

v0.1：首次固化该口径。

```ground:caliber
name: 有效变更记录
predicate: "cust_change_record.enable = 'Y'"
scope: 变更记录读取/跳转判定
evidence: "code_path:CustChangeApplication.java#getRedirectPage"
```

相关页面：[[cust_change_record]]、[[valid_change_cfg]]、[[valid_oper_change_record]]、[[admin_mobile_redirect]]。