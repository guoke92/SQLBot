---
type: caliber
title: 正在审核中的变更记录
page_key: caliber_checking_change
belong: calibers
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustChangeApplication.changeRebuild", "db_dist", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_change_record.status]
coverage_note: 变更记录
scope:
  databases: [lowcode_pplatform]
---

该口径精确定义状态为 `CUST_CHECK_CHECKING` 的变更记录，用于筛选当前正在审核中的变更申请，便于运营中台审批处理与状态展示。

## 需求背景

暂无特定需求声明。

```ground:caliber
name: "正在审核中的变更记录"
predicate: "cust_change_record.status = 'CUST_CHECK_CHECKING'"
scope: "变更记录"
evidence: "code_path:CustChangeApplication.changeRebuild + db_dist"
```

## 版本演进

暂无。

相关：[[cust_change_record]]
