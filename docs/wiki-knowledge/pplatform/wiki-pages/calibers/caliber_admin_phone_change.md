---
type: caliber
title: 管理员手机号变更项
page_key: caliber_admin_phone_change
belong: calibers
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustChangeApplication.getRedirectPage", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_change_cfg.item_code]
coverage_note: 变更配置
scope:
  databases: [lowcode_pplatform]
---

该口径识别变更配置中编码为 `UN0012` 或 `UN0013` 的变更项，即管理员手机号变更项，用于决定变更提交后的页面跳转逻辑。

## 需求背景

暂无特定需求声明。

```ground:caliber
name: "管理员手机号变更项"
predicate: "cust_change_cfg.item_code IN ('UN0012','UN0013')"
scope: "变更配置"
evidence: "code_path:CustChangeApplication.getRedirectPage"
```

## 版本演进

暂无。

相关：[[cust_change_cfg]]
