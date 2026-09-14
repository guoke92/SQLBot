---
type: rule
title: 异常解析导入-按产品分组RPC
page_key: exception_import_rpc_group_by_product
domain: funding
status: draft
aliases:
  - 对接方标识校验按产品分组
  - 分组RPC校验
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#collectFundingPartyCodeErrors"
contract_version: "0.1"
belong: rules
---

# 异常解析导入-按产品分组RPC

## 业务定位

校验导入行中的「对接方标识」是否存在时，**按 `productCode` 分组，每组只发一次 RPC**，禁止逐行循环调用。这是对远程调用次数的硬性约束：一次导入最多产生「产品种类数」次调用，而不是「行数」次，避免批量导入把资方服务打爆。

## 需求背景

无语义分析挂载的需求文档锚点。该方法名 `collectFundingPartyCodeErrors` 表明校验被拆成独立收集步骤，便于与其他阶段解耦。

## 版本演进

无 `action=uncovered` 的主张。

```ground:rule
rule: 异常解析导入-按产品分组RPC
content: "对接方标识校验按 productCode 分组，每组一次 RPC，禁止循环调用"
impact: "限制远程调用次数，避免性能问题"
field_targets:
  - funding_exception_resolution.funding_party_code
evidence: "code:ExceptionResolutionApplication#collectFundingPartyCodeErrors"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 概念：[[concepts/product_code]]、[[concepts/funding_party_code]]
- 规则：[[rules/exception_import_all_or_nothing]]