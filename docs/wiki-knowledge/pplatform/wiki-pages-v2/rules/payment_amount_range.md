---
type: rule
title: 打款验证金额区间
page_key: payment_amount_range
domain: 企业银行账户
status: draft
aliases:
  - 验证金额校验
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: rules
---

# 打款验证金额区间

验证金额须 >0 且 <1（0.01~0.99 元），控制器换算为“分”后传给银行。

## 需求背景

小额打款验证要求金额足够小，避免企业误当成正常回款；单位换算发生在控制器层，接口文档与页面提示需与之一致。

## 版本演进

- 入参以元为单位、出参以分为单位，跨层单位不一致是排查打款金额不符的常见来源。

```ground:rule
name: 打款验证金额区间
content: 验证金额须 >0 且 <1（0.01~0.99），控制器换算为分后传银行
impact: 入参校验
field_targets:
  - cust_account_info.trans_id
evidence: code_path:CustAccountInfoController.java:checkAmount
```