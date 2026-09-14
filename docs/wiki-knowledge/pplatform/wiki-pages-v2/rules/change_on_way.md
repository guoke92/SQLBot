---
type: rule
title: 变更在途判定
page_key: change_on_way
domain: 企业变更与运营变更
status: draft
aliases: [changeHasBusiOnWay, 变更在途]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: rules
---

规则内容：`cust_company_info.cust_status='CHANGE'` 即视为该企业存在变更在途业务（`changeHasBusiOnWay` 返回 true），用于控制变更入口与页面跳转。口径定义见 [[company_in_change]]。

## 需求背景

企业级「变更中」标记让入口无需扫描变更记录即可判断在途，保证重复发起与跳转判定的一致性。

## 版本演进

v0.1：首次固化。

```ground:rule
name: 变更在途判定
content: "cust_company_info.cust_status='CHANGE' 即视为存在变更在途业务（changeHasBusiOnWay 返回 true）"
impact: 控制变更入口与页面跳转
field_targets:
  - cust_company_info.cust_status
evidence: "code_path:CustChangeApplication.java#changeHasBusiOnWay(CustStatusEnum.CHANGE.name())"
```

相关页面：[[company_in_change]]、[[cust_company_info]]、[[cust_company_info_cust_status]]、[[change_rebuild]]。