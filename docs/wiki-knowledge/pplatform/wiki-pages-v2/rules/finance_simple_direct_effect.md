---
type: rule
title: 资金方简易认证直接生效
page_key: finance_simple_direct_effect
domain: 企业建档与认证
status: draft
aliases:
  - 资金方零审批建档
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:submitForSimpleAuth
contract_version: "0.1"
belong: rules
---

简易认证路径下的例外：当企业类型为 `FINANCE`（资金方）时，提交即置为 `BUILD_SUCCESS` 且生命周期置 `EFFECT`，不等待客户确认，形成零审批落库。

```ground:rule
name: 资金方简易认证直接生效
content: 简易认证且企业类型为 FINANCE 时，提交即置 BUILD_SUCCESS + cust_status=EFFECT，不待确认
impact: 资金方建档零审批落库
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.cust_status
  - cust_company_info.cust_company_type
evidence: code_path:CustCompanyInfoApplication.java:submitForSimpleAuth
```

## 需求背景

资金方企业由平台侧确认，无需再走客户确认环节（对比 [[concepts/cust_confirm_await]] 的 `AWAIT_CUST_CONFIRM` 分支）。企业类型以 `cust_company_type` 的 JSON 数组形式表达，见 [[tables/cust_company_info]]。

## 版本演进

v0 初稿：规则以 `submitForSimpleAuth` 的分支写值点固化。`cust_company_type` 中多角色并存时的判定顺序待复核。

关联：[[rules/simple_auth_no_ca]]、[[concepts/build_success]]、[[calibers/effect_company_scope]]。