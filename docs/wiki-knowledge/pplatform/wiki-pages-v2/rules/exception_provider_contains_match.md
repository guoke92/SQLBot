---
type: rule
title: 异常解析对上游只按关键字 contains 命中
page_key: exception_provider_contains_match
domain: 资金规则与异常处理
status: draft
aliases:
  - 异常解析 Provider 匹配规则
  - errorMessage contains
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyExceptionResolutionProviderImpl.java
  - db:funding_exception_resolution
contract_version: "0.1"
belong: rules
---

对外查询先按 fundingPartyCode + productCode + enable='Y' 批量取数，再在内存中做 errorMessage.contains(errorKeyword) 过滤；命中多条则全部返回。

## 需求背景

上游拿到的结果不带模糊度控制，关键字长度与大小写敏感（实际为大小写敏感 contains），上游需自行处理多命中。参数缺失或系统异常一律返回空列表、不抛错，属于「降级为无结果」的容错约定。调用入口参数即 [[funding_party_mark]] 在异常域的表达 funding_party_code。

## 版本演进

v0 首次建立。

```ground:rule
name: 异常解析对上游只按关键字 contains 命中
content: ProviderImpl 先按 fundingPartyCode + productCode + enable='Y' 批量查，再在内存中过滤 errorMessage.contains(errorKeyword)，可命中多条全部返回；参数缺失或系统异常一律返回空列表不抛错。
impact: 上游拿到的结果不带模糊度控制，关键字长度/大小写敏感（实际为大小写敏感 contains）
field_targets:
  - funding_exception_resolution.error_keyword
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.product_code
evidence: code_path:FundingPartyExceptionResolutionProviderImpl.java:doQuery/queryByFundingPartyId
```