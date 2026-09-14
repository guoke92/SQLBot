---
type: caliber
title: 启用企业口径（cust_company_info.enable='Y'）
page_key: cust_company_enable
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [启用企业, 企业 enable='Y']
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:CustGeneralProductApplication.syncExistingPlatformOperatorToProducts 中 .eq(getEnable, BooleanEnum.Y.getDictKey())"
contract_version: "0.1"
belong: calibers
---

「启用企业」是存量运营方推送全量扫描时的企业筛选条件，取值为 `BooleanEnum.Y.getDictKey()`，语义等同 'Y'。与 [[cust_person_enable]] 一起构成「启用企业 + 启用联系人」的同步范围。

表结构见 [[cust_company_info]]。

## 需求背景
停用企业不应继续推送运营方，全量扫描需要先按启用状态过滤。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 启用企业
predicate: "cust_company_info.enable = 'Y'"
scope: "存量运营方推送全量扫描"
evidence: "code:CustGeneralProductApplication.syncExistingPlatformOperatorToProducts 中 .eq(getEnable, BooleanEnum.Y.getDictKey())"
```