---
type: caliber
title: 客户认证成功
page_key: cust_cert_success
domain: 文件/附件/媒体
status: draft
aliases: [建档成功口径]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:updateCustBuildStatus"]
contract_version: "0.1"
belong: calibers
---
判定企业已完成认证/建档的口径，是 [[cust_build_status]] 状态机的终态之一。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 updateCustBuildStatus 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 客户认证成功
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS'
scope: 企业建档
evidence: code
```

关联：[[cust_company_info]]、[[CustBuildStatusEnum]]、[[cust_build_status]]。