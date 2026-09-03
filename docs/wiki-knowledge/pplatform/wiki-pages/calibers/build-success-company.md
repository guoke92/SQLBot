---
type: caliber
title: "认证成功企业"
page_key: build-success-company
domain: 集团与关联关系
status: published
aliases: []
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
field_targets: [cust_company_info.cust_build_status]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

认证成功企业口径判断企业是否完成认证，并作为发送集团关系待办和协议操作的前置条件。

## 需求背景

- 企业 `cust_build_status = 'BUILD_SUCCESS'` 时视为认证成功。

## 版本演进

- 暂无变更。

```ground:caliber
name: 认证成功企业
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS'
scope: 判断是否发送集团关系待办、是否可进行协议操作
evidence: code
```

相关：[[cust_company_info]] [[build-success]] [[auto-send-notice-on-build-success]]