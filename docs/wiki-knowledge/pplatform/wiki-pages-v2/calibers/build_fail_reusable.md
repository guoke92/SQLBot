---
type: caliber
title: 建档失败可复用口径
page_key: build_fail_reusable
domain: 外部渠道与银行对接
status: draft
aliases:
  - 建档失败豁免
  - 失败件可重建
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.initCust
contract_version: "0.1"
belong: calibers
---

建档失败（BUILD_FAIL）的企业在查重时被豁免，允许同企业重建并复用旧 id/code。

## 需求背景
渠道建档失败多为资料或网络原因，直接占用信用代码会导致企业无法再次提交。因此「已建档」判定为 `count(cust_build_status != BUILD_FAIL) != 0`，失败件不再计为已建档；重建后状态回到 INIT，见 [[cust_build_status]]。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 建档失败可复用口径
predicate: "cust_company_info.cust_build_status = 'BUILD_FAIL'"
scope: "查重时豁免：已建档判定为 count(cust_build_status != BUILD_FAIL) != 0，失败件允许重建"
evidence: "code:CustAccessApplication.validateSetValue / initCust"
```