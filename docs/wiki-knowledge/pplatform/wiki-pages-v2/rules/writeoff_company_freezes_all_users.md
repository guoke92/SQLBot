---
type: rule
title: 注销企业同时冻结所有用户
page_key: writeoff_company_freezes_all_users
domain: 企业建档与认证
status: draft
aliases:
  - 企业注销连带全部用户
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:custStatusOperator
contract_version: "0.1"
---

注销企业（`cust_status` 置为 `WRITEOFF`，见 [[customer_status_machine]]）时，系统先冻结该企业下的**所有用户**。与 [[freeze_company_freezes_admin]] 相比，注销的级联范围从“管理员”扩大到“全部用户”，说明注销是比冻结更强的终止性动作。

```ground:rule
name: 注销企业同时冻结所有用户
content: 注销企业时，先冻结该企业下所有用户。
impact: 所有用户无法登录。
field_targets:
  - cust_status
evidence: "code_path:CustCompanyInfoApplication.java:custStatusOperator"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。