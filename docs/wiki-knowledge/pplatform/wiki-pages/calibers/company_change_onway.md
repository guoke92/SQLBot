---
type: caliber
title: 企业有在途变更业务
page_key: caliber_company_change_onway
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustChangeApplication.changeHasBusiOnWay", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.cust_status]
coverage_note: 企业
scope:
  databases: [lowcode_pplatform]
---

该口径通过企业主数据的 `cust_status = 'CHANGE'` 判断企业当前是否存在在途变更业务。这是从企业生命周期状态维度对变更活跃度的直接标识。

## 需求背景

暂无特定需求声明。

```ground:caliber
name: "企业有在途变更业务"
predicate: "cust_company_info.cust_status = 'CHANGE'"
scope: "企业"
evidence: "code_path:CustChangeApplication.changeHasBusiOnWay"
```

## 版本演进

暂无。

相关：[[cust_company_info]]
