---
type: rule
title: 认证成功置客户生效
page_key: auth_success_sets_customer_effective
domain: 企业建档与认证
status: draft
aliases:
  - 认证成功联动生效
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
contract_version: "0.1"
---

当企业认证状态变更为 `BUILD_SUCCESS` 时，系统同步将客户状态 `cust_status` 置为 `EFFECT`。这条规则是两个状态机（[[enterprise_auth_status_machine]] 与 [[customer_status_machine]]）之间唯一的联动点，也是企业进入“生效企业”口径（[[effective_company]]）的必要环节。

该规则意味着：客户状态的“生效”不是独立操作的结果，而是认证成功的结果；反向地，认证失败或退回不会改变客户状态。

```ground:rule
name: 认证成功置客户生效
content: 当企业认证状态变更为 BUILD_SUCCESS 时，同步将客户状态 cust_status 置为 EFFECT。
impact: 企业正式生效，可开展业务。
field_targets:
  - cust_build_status
  - cust_status
evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。