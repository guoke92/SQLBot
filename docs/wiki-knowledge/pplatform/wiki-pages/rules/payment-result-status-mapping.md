---
type: rule
title: 申请结果查询状态映射
page_key: payment-result-status-mapping
domain: 企业银行账户与第三方银行
status: published
aliases: []
oid: 1
sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_account_info.auth_state]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

规则“申请结果查询状态映射”将银行查询返回的状态码映射为账户认证状态：`10`→`APPLY_10`、`20`→`APPLY_20`、`30`→`APPLY_30`。

## 需求背景

银行接口返回的状态码与系统内部状态不一致，需要映射。该规则在 `paymentResult` 方法中实现，保持状态同步。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 申请结果查询状态映射
content: 银行查询结果 status=10映射APPLY_10，status=20映射APPLY_20，status=30映射APPLY_30
impact: 同步账户认证状态
field_targets:
  - cust_account_info.auth_state
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:paymentResult"
```

[[cust-account-info-auth-state]] 状态机中的查询转换基于该规则。

相关：[[cust_account_info]]
