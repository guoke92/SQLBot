---
type: caliber
title: 认证通过企业
page_key: authenticated-company
belong: calibers
domain: 企业建档与准入
status: published
aliases: [已认证企业]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.cust_build_status, cust_company_info.enable]
scope:
  databases: [lowcode_pplatform]
---

# 认证通过企业

本口径识别已完成认证且有效的企业，通常作为业务准入、合同签订或交易开展的前提条件。判定依据 `cust_build_status = 'BUILD_SUCCESS'` 且 `enable = 'Y'`。

## 需求背景

认证通过是企业生命周期从 ADD 转入 EFFECT 的关键节点，由 [[enterprise-auth-status-machine]] 的“审核通过”事件驱动，并联动 [[customer-lifecycle-status-machine]] 更新 `cust_status=EFFECT`。

## 版本演进

口径证据来自数据库分布：`BUILD_SUCCESS` 占比 49362，`enable=Y` 占比 94167。当前谓词为两字段 AND 关系。

```ground:caliber
name: 认证通过企业
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.enable = 'Y'"
scope: 企业已完成认证且有效
evidence: "db_dist:BUILD_SUCCESS占比49362，enable=Y占比94167"
```

相关概念：[[auth-status]]；相关表：[[cust_company_info]]