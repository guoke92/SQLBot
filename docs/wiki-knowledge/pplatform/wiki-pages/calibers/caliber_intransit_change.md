---
type: caliber
title: 在途变更流程
page_key: caliber_intransit_change
belong: calibers
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustChangeApplication.changeRebuild", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_change_record.enable, cust_change_record.status]
coverage_note: 变更记录
scope:
  databases: [lowcode_pplatform]
---

该口径用于识别企业当前是否存在未完成的变更流程。通过排除终态（已通过/已驳回）并同时要求 `enable = 'Y'` 来定义在途状态，是流程重建与并发控制的基础判断。

## 需求背景

暂无特定需求声明。

```ground:caliber
name: "在途变更流程"
predicate: "cust_change_record.status NOT IN ('CUST_CHECK_PASS','CUST_CHECK_REJECT') AND cust_change_record.enable = 'Y'"
scope: "变更记录"
evidence: "code_path:CustChangeApplication.changeRebuild"
```

## 版本演进

暂无。

相关：[[cust_change_record]]
