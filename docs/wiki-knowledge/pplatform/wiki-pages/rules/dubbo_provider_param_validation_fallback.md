---
type: rule
title: Dubbo Provider 参数校验与异常兜底
page_key: dubbo_provider_param_validation_fallback
domain: 资金方规则与异常解决
status: published
aliases:
  - Dubbo 参数校验兜底
oid: 1

sources:
  - code:FundingPartyExceptionResolutionProviderImpl.queryByFundingPartyId
  - code:FundingPartyRuleProviderImpl.queryFundingPartyRules
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则约束对外 Dubbo Provider 的参数校验和异常处理。对必填参数空值抛业务异常，但捕获后返回空列表或空结果，不向调用方抛出异常。系统异常记 ERROR 后同样返回空。

## 需求背景

保证下游可用性是 Dubbo 服务的重要目标。该规则确保即使参数缺失或系统异常，也不会影响调用方。

## 版本演进

本规则当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:rule
name: "Dubbo Provider 参数校验与异常兜底"
content: "对外 Dubbo Provider 对必填参数空值抛业务异常，但捕获后返回空列表或空结果，不向调用方抛出异常。系统异常记 ERROR 后同样返回空。"
impact: "保证下游可用性。"
field_targets: []
evidence: "code:FundingPartyExceptionResolutionProviderImpl.queryByFundingPartyId / FundingPartyRuleProviderImpl.queryFundingPartyRules"
```