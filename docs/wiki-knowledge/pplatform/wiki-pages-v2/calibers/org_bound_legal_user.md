---
type: caliber
title: 二级组织绑定合法用户
page_key: caliber.org_bound_legal_user
domain: 数据权限与组织
status: draft
aliases: [二级组织绑定合法用户]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

本口径在语义分析原文中被截断，predicate 只到 "cust_person_info.user_id = ? AND cust_person_" 为止，scope 与 evidence 也未能取到。从谓词前缀可判定它是「某一用户 + 某联系人侧条件」的联合条件，用于二级组织绑定时校验用户合法性，与 [[tables/cust_person_info]]、[[tables/sys_cust_org_user_permission]] 相关；但完整的第二个条件与适用链路无法从现有证据确定，本页暂不作为可执行口径使用。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本口径的语义分析条目本身不完整，需求背景待补。

## 版本演进

v0：仅登记截断原文，等待语义分析补全后重写。

```ground:caliber
name: 二级组织绑定合法用户
predicate: "cust_person_info.user_id = ? AND cust_person_"
scope: （语义分析原文在此截断，未给出）
evidence: （语义分析原文在此截断，未给出）
```