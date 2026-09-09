---
type: rule
title: 企业名称唯一校验（天马渠道）
page_key: company-name-unique-tianma
belong: rules
domain: 企业建档与准入
status: published
aliases: [企业名称唯一校验]
oid: 1

sources: ["db", "code", "reqdoc", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.db_tenant_code, cust_company_info.name]
scope:
  databases: [lowcode_pplatform]
---

# 企业名称唯一校验（天马渠道）

本规则要求同一租户下企业名称不能重复（非失败状态），重复名称抛出 `REG_EXIST_EXCEPTION`。

## 需求背景

需求文档明确“企业名称同一租户下唯一”，代码证据为 `CustAccessApplication.validateSetValueOfTianma` 按 `name+db_tenant_code` 查询。统一信用代码重复检查见 [[unified-credit-code-duplicate-check]]。

## 版本演进

证据来自代码路径 `CustAccessApplication.validateSetValueOfTianma`，并与需求文档主张锚定。

```ground:rule
name: 企业名称唯一校验（天马渠道）
content: 同一租户下企业名称不能重复（非失败状态）
impact: 重复名称抛出 REG_EXIST_EXCEPTION
field_targets:
  - cust_company_info.name
  - cust_company_info.db_tenant_code
evidence: "code_path:CustAccessApplication.validateSetValueOfTianma + reqdoc:企业名称同一租户下唯一"
```

相关表：[[cust_company_info]]；相关规则：[[unified-credit-code-duplicate-check]]