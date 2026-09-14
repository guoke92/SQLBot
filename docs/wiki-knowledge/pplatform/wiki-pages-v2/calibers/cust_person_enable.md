---
type: caliber
title: 启用联系人口径（cust_person_info.enable='Y'）
page_key: cust_person_enable
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [启用联系人, 联系人 enable='Y']
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AssetOperatorSyncApplication.syncAssetOperator 中 .eq(CustPersonInfoDO::getEnable, \"Y\")"
contract_version: "0.1"
belong: calibers
---

「启用联系人」是资产审核运营人员同步时的企业联系人筛选条件：只同步 `enable='Y'` 的联系人。它是人员侧与 [[cust_company_enable]]（企业侧）配套使用的口径。

表结构见 [[cust_person_info]]，运营人员语义边界见 [[operator_id]]。

## 需求背景
离职或停用的联系人不应再被同步为运营对接人，同步前必须按启用状态过滤。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 启用联系人
predicate: "cust_person_info.enable = 'Y'"
scope: "资产审核运营人员同步时筛选企业下联系人"
evidence: "code:AssetOperatorSyncApplication.syncAssetOperator 中 .eq(CustPersonInfoDO::getEnable, \"Y\")"
```