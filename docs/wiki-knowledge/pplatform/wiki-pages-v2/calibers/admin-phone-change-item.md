---
type: caliber
title: 管理员手机号变更项
page_key: admin-phone-change-item
domain: 企业变更与运营变更
status: draft
aliases: [UN0012, UN0013, 管理员手机号变更]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:getRedirectPage
contract_version: "0.1"
belong: calibers
---

「管理员手机号变更项」是跳转页判定的识别口径：变更项编码落在 `UN0012`/`UN0013`（`CustUpdateItemCodeConstants`）即视为管理员手机号变更。变更单与配置的关联方式见 [[concepts.item-code]]，判定后的跳转逻辑见 [[rules.admin-phone-change-redirect]]。

## 需求背景

管理员手机号变更会改变登录主体与新管理员的可见内容，因此需要单独识别该变更项并走不同的落地页；识别依据是稳定的业务编码而非数据库主键，以兼容配置表主键漂移。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.getRedirectPage`。

```ground:caliber
name: 管理员手机号变更项
predicate: "cust_change_cfg.item_code IN ('UN0012','UN0013')"
scope: 变更单跳转页判定
evidence: code_path:CustChangeApplication.java:getRedirectPage（CustUpdateItemCodeConstants.UN0012/UN0013）
```