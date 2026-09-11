---
type: caliber
title: 集团有效成员
page_key: caliber.effective_group_member
domain: 数据权限与组织
status: draft
aliases: [集团有效成员, EFFECTIVE 成员]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「集团有效成员」以 [[tables/cust_group_rel]].status = 'EFFECTIVE' 为唯一条件，用于子公司平铺列表过滤。状态到达 EFFECTIVE 的路径见 [[processes/cust_group_rel_status_fsm]]；未生效记录（INEFFECTIVE）不应出现在平铺结果中。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（CustGroupRelApplication#listSubCust）成文。

```ground:caliber
name: 集团有效成员
predicate: "cust_group_rel.status = 'EFFECTIVE'"
scope: 子公司平铺列表 listSubCust 过滤
evidence: code_path:CustGroupRelApplication.java#listSubCust
```