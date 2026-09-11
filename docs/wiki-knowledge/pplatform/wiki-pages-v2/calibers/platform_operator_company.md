---
type: caliber
title: 运营方企业
page_key: caliber.platform_operator_company
domain: 数据权限与组织
status: draft
aliases: [运营方企业, PLATFORM_OPERATOR_COMPANY]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「运营方企业」口径要求 [[tables/cust_company_info]].cust_company_type 这个 JSON 数组字符串中包含 PLATFORM_OPERATOR_COMPANY，且企业处于启用状态。由于 cust_company_type 是数组字符串（可多角色，见 [[concepts/company_role_type]]），判定时是「包含」而非「等于」。

同一租户可能存在多个运营方，实际取用时通常还需叠加 [[calibers/real_operator]] 过滤测试数据。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（CustGroupRelApplication）成文。

```ground:caliber
name: 运营方企业
predicate: "cust_company_info.cust_company_type 包含 'PLATFORM_OPERATOR_COMPANY' AND cust_company_info.enable = 'Y'"
scope: 租户运营方查询
evidence: code_path:CustGroupRelApplication.java#queryTenantOperatorCompany
```