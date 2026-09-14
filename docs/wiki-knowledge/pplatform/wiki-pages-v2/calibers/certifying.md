---
type: caliber
title: 认证中
page_key: certifying
domain: 企业建档与认证
status: draft
aliases:
  - CUST_BUILDING 判断
oid: 1
scope:
  databases: []
sources:
  - code:CustBuildStatusConstant.CUST_BUILDING
contract_version: "0.1"
belong: calibers
---

“认证中”是认证状态 `cust_build_status = 'CUST_BUILDING'` 的记录集合（见 [[auth_status]]、[[enterprise_auth_status_machine]]）。处于该状态的企业已提交认证并进入审核环节，等待运营审核通过或退回。

该状态与运营审核状态机的“审核中”（[[operation_check_status_machine]] 的 `CUST_CHECK_CHECKING`）在业务时间上重合，但字段与判定口径不同，二者不可互相替代。

```ground:caliber
name: 认证中
predicate: cust_company_info.cust_build_status = 'CUST_BUILDING'
scope: 认证流程状态
evidence: "code_path:CustBuildStatusConstant.CUST_BUILDING"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立口径页。