---
type: rule
title: 统一信用代码重复校验
page_key: unified-credit-code-duplicate-check
belong: rules
domain: 企业建档与准入
status: published
aliases: [统一社会信用代码重复校验]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.certification_no, cust_company_info.db_tenant_code]
scope:
  databases: [lowcode_pplatform]
---

# 统一信用代码重复校验

本规则要求同一租户下统一信用代码不能重复存在（非失败状态）。重复建档时抛出异常或复用旧记录。

## 需求背景

统一社会信用代码是企业唯一标识之一。`CustAccessApplication.validateSetValue` 检查 `countBuildFail != 0` 则抛异常；查询按 `certification_no+db_tenant_code` 组合进行。

## 版本演进

证据来自代码路径 `CustAccessApplication.validateSetValue`。

```ground:rule
name: 统一信用代码重复校验
content: 同一租户下统一信用代码不能重复存在（非失败状态）
impact: 重复建档时抛出异常或复用旧记录
field_targets:
  - cust_company_info.certification_no
  - cust_company_info.db_tenant_code
evidence: "code_path:CustAccessApplication.validateSetValue 检查 countBuildFail !=0 则抛异常；query 中按 certification_no+db_tenant_code 查询"
```

相关表：[[cust_company_info]]
---REVIEW: rule | 统一信用代码重复校验---
需求文档主张“统一社会信用代码必填18位，格式符合国家标准”，代码中仅对身份证进行18位格式校验，未发现对企业信用代码的长度/格式校验。该主张在本次证据范围内未被覆盖，标记为待确认。
---END REVIEW---