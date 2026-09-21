---
type: dict
title: wechat_project_approval_apply.product_type
page_key: wechat_project_approval_apply__product_type
belong: dicts
status: draft
anchors: [wechat_project_approval_apply.product_type]
sources: ['database_profile:wechat_project_approval_apply.product_type']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [wechat_project_approval_apply]
---

# wechat_project_approval_apply.product_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `wechat_project_approval_apply.product_type`，表页 [[tables/wechat_project_approval_apply]]。

## 取值

```ground:dict
dict: wechat_project_approval_apply__product_type
fields: [wechat_project_approval_apply.product_type]
values:
  凭证-直保: {trust: proposed}
  凭证-直保,凭证-再保: {trust: proposed}
  供应链票据: {trust: proposed}
  供应链ABS/ABN: {trust: proposed}
  凭证-直保,凭证-再保,凭证-质押: {trust: proposed}
  凭证-质押: {trust: proposed}
  凭证-再保: {trust: proposed}
  供应链ABS: {trust: proposed}
  本地化: {trust: proposed}
  凭证-直保,凭证-质押: {trust: proposed}
  线上保理-再保: {trust: proposed}
  凭证-直保,凭证-再保,凭证-质押,线上保理-直保,线上保理-再保,跨境保理,线上保理-质押,供应链票据,国内信用证,订单融资,经销商融资,其他（具体在项目描述中说明）: {
    trust: proposed}
  凭证-直保,凭证-再保,凭证-质押,线上保理-直保,线上保理-再保,经销商融资: {trust: proposed}
  SaaS+本地化: {trust: proposed}
  订单融资,经销商融资: {trust: proposed}
  跨境保理: {trust: proposed}
  线上保理-质押: {trust: proposed}
  凭证-直保,凭证-再保,订单融资: {trust: proposed}
  凭证-直保,凭证-再保,凭证-质押,线上保理-直保,线上保理-质押,线上保理-再保,跨境保理,供应链票据,国内信用证,订单融资,经销商融资,其他（具体在项目描述中说明）: {
    trust: proposed}
  凭证-再保,凭证-直保: {trust: proposed}
  线上保理-直保: {trust: proposed}
  应收账款ABS/ABN: {trust: proposed}
  其他（具体在项目描述中说明）,经销商融资,国内信用证: {trust: proposed}
  供应链非标: {trust: proposed}
  订单融资: {trust: proposed}
  经销商融资: {trust: proposed}
triage: keep
```
