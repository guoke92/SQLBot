---
type: caliber
title: 可发起变更申请
page_key: caliber_change_enable
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustChangeApplication.changeEnable", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.check_status]
coverage_note: 企业
scope:
  databases: [lowcode_pplatform]
---

该口径定义企业可发起新变更申请的条件：企业审核状态不能为 `CUST_CHECK_CHECKING`。它用于防止审核期间重复提交，是变更申请入口的前置校验。

## 需求背景

暂无特定需求声明。

```ground:caliber
name: "可发起变更申请"
predicate: "cust_company_info.check_status != 'CUST_CHECK_CHECKING'"
scope: "企业"
evidence: "code_path:CustChangeApplication.changeEnable"
```

## 版本演进

> (document_claim，未证实) 企业状态为已冻结或已注销时不允许变更。代码未见明确校验逻辑。

相关：[[cust_company_info]]
