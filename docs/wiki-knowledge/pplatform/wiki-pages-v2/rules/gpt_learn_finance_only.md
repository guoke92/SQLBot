---
type: rule
title: GP学习/智能审核引流仅限金融机构用户
page_key: gpt_learn_finance_only
domain: 客户管理
status: draft
aliases: [仅金融机构可引流, validateFinanceUser]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:validateFinanceUser
  - code_path:GptLearnService.java:checkPosterStatus
contract_version: "0.1"
belong: rules
---

三个入口 `syncLoginInfo` / `checkPosterStatus` / `recordPosterClick` 都先执行 `validateFinanceUser`：`currentUser` 非空且企业角色必须等于 `CustCompanyTypeEnum.FINANCE.getDictKey()`，否则抛「仅金融机构用户可使用」；企业信息不存在抛「企业信息不存在」。判定位来自 [[tables/cust_company_info]] 的 `cust_company_type`，效果是 [[processes/gpt_learn_poster_log_lifecycle]] 中的 `INIT → NOT_SHOW`。

## 需求背景

引流卡片面向金融机构用户投放，因此把企业角色作为最前置的准入条件，非 FINANCE 企业连埋点都不会产生。`cust_company_type` 存的是 JSON 数组字符串（如 `["FINANCE"]`），比较走字典 key。

## 版本演进

- 当前观测：`gpt_learn_poster_log` 仅 252 行且租户单一，与该规则叠加后投放面很窄。

```ground:rule
name: GP学习/智能审核引流仅限金融机构用户
content: "syncLoginInfo / checkPosterStatus / recordPosterClick 入口均先执行 validateFinanceUser：currentUser 非空且 companyType 必须等于 CustCompanyTypeEnum.FINANCE.getDictKey()，否则抛「仅金融机构用户可使用」；企业信息不存在抛「企业信息不存在」"
impact: 非 FINANCE 企业用户调用引流接口直接失败，不产生埋点
field_targets:
  - cust_company_info.cust_company_type
evidence: "code_path:GptLearnService.java:validateFinanceUser + GptLearnService.java:checkPosterStatus"
```