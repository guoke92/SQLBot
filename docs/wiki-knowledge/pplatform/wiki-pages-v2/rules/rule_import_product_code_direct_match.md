---
type: rule
title: 资方规则导入-产品校验直接比对productCode
page_key: rules/rule_import_product_code_direct_match
domain: funding
status: draft
aliases:
  - 规则导入产品校验
  - 无名称转换的产品校验
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#collectFundRuleProductCodeErrors"
contract_version: "0.1"
---

# 资方规则导入-产品校验直接比对productCode

## 业务定位

资方规则导入时，`productCode` 直接与 `ProductCodeEnum` 枚举比对，**没有名称转换**。这与异常解析导入的口径不同——后者会先用 `platformProduct.listPlatformProduct` 把产品名称映射为 code，因此异常解析模板的「产品code」列实际可以填产品名称，而**规则导入模板的产品列必须填产品 code**。两者的差异详见 [[concepts/product_code]]。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。两条导入链路口径不一致，是本主题下最容易导致运营填错的边界。

```ground:rule
rule: 资方规则导入-产品校验直接比对productCode
content: "规则导入 productCode 直接与 ProductCodeEnum 枚举比对（无名称转换），与异常解析导入的名称映射口径不同"
impact: "规则导入模板产品列必须填产品code"
field_targets:
  - funding_rule_info.product_code
evidence: "code:FundRuleInfoApplication#collectFundRuleProductCodeErrors"
```

## 关联

- 概念：[[concepts/product_code]]
- 表：[[tables/funding_rule_info]]