---
type: caliber
title: 有效运营变更记录
page_key: valid_oper_change_record
domain: 企业变更与运营变更
status: draft
aliases: [运营人员变更记录口径, 运营变更 enable=Y]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:OperChangeRecordApplication.java
contract_version: "0.1"
belong: calibers
---

口径定义：按联系人查询运营人员变更历史（[[cust_oper_change_record]]）时固定 `enable='Y'`。该条件在代码中以字面量 `'Y'` 直写，未走 `EnableEnum`，与 [[valid_change_cfg]] 的写法不同。

## 需求背景

运营人员变更记录是对外展示的历史列表，需要过滤失效行；字面量写法属于实现差异，口径本身与「有效记录」一致。

## 版本演进

v0.1：首次固化该口径，并标注字面量直写的实现差异。

```ground:caliber
name: 有效运营变更记录
predicate: "cust_oper_change_record.enable = 'Y'"
scope: 运营人员变更记录查询（字面量 'Y' 直写）
evidence: "code_path:OperChangeRecordApplication.java#queryByPersonId"
```

相关页面：[[cust_oper_change_record]]、[[oper_change_query]]、[[valid_change_record]]、[[valid_change_cfg]]。