---
type: rule
title: 跳过实名认证限制
page_key: skip-realname-limit
domain: 客户联系人管理
status: draft
aliases:
  - 免实名适用范围
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonController.skipRealNameAuth"
contract_version: "0.1"
belong: rules
---

仅当租户主标识为 HBLT，或企业角色为核心企业/项目公司时，经办人可跳过实名认证。

## 需求背景

需求文档主张「跳过实名认证仅限特定角色」（code_path:CustPersonController.java:skipRealNameAuth + reqdoc:跳过实名认证仅限特定角色），代码按租户标识与企业角色双重条件放行：满足条件时置 `skip_auth_flag = 'Y'`（口径见 [[calibers/realname-skip]]），否则经办人须走 [[processes/person-realname-status]] 的认证流程。企业角色取自 `cust_company_info.company_type`，本表通过 `company_type` 冗余。

```ground:rule
rule: 跳过实名认证限制
content: 仅当租户主标识为HBLT，或企业角色为核心企业/项目公司时，经办人可跳过实名认证
impact: 控制哪些经办人可以跳过实名认证
field_targets:
  - cust_person_info.skip_auth_flag
  - cust_company_info.company_type
evidence: "code:CustPersonController.skipRealNameAuth + code_path:CustPersonController.java:skipRealNameAuth + reqdoc:跳过实名认证仅限特定角色"
```

## 版本演进

- v0：首次登记。

相关：[[calibers/realname-skip]]、[[processes/person-realname-status]]、[[tables/cust_person_info]]。