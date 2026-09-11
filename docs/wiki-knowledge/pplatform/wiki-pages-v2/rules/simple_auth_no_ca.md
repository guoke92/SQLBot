---
type: rule
title: 简易认证强制不开通电子签章 CA
page_key: rule.simple_auth_no_ca
domain: 数据权限与组织
status: draft
aliases: [简易认证 CA 校正, need_register_ca]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

当企业走简易认证（identify_style=SIMPLE，见 [[tables/cust_company_info]]）时，need_register_ca 会被强制校正为「不开通」，即便上游传入了开通意图也会被覆盖。该校正与简易认证支线的建档状态流转（AWAIT_CUST_CONFIRM → BUILD_SUCCESS，见 [[processes/cust_build_status_fsm]]）配套。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由字段语义「简易认证时被强制校正为不开通」得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: 简易认证 CA 校正
statement: 简易认证场景 need_register_ca 强制为不开通
condition: identify_style = SIMPLE
action: 覆盖 need_register_ca 为 N
evidence: code_path:cust_company_info.need_register_ca（简易认证时被强制校正为不开通）
```