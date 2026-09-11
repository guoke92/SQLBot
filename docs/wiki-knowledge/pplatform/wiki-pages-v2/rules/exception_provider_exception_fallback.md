---
type: rule
title: 异常解析对外查询-异常兜底
page_key: rules/exception_provider_exception_fallback
domain: funding
status: draft
aliases:
  - 对外接口异常兜底
  - 返回空列表不抛异常
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundingPartyExceptionResolutionProviderImpl#queryByFundingPartyId"
contract_version: "0.1"
---

# 异常解析对外查询-异常兜底

## 业务定位

对外查询入口 `queryByFundingPartyId` 对**参数校验失败**与**系统异常**一视同仁：记日志后返回空列表，绝不向 Dubbo 上游抛异常。这是可用性优先的取舍——异常解析是辅助性能力，宁可返回「没找到」也不能让主流程因它失败。代价是上游无法区分「无匹配配置」与「查询出错」，需要靠日志排查。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:rule
rule: 异常解析对外查询-异常兜底
content: "参数校验失败或系统异常均记日志并返回空列表，不向 Dubbo 上游抛异常"
impact: "保证对外接口稳定"
field_targets: []
evidence: "code:FundingPartyExceptionResolutionProviderImpl#queryByFundingPartyId"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_provider_keyword_contains]]