---
type: concept
title: 资方标识（fundingPartyMark / fundingPartyCode）
page_key: funding_party_mark
domain: 资金规则与异常处理
status: draft
aliases:
  - 资金方标识
  - 对接方标识
  - fundingPartyMark
  - fundingPartyCode
  - fundingPartyId
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - db:funding_rule_info
  - db:funding_exception_resolution
maps_to: funding_rule_info.funding_party_mark
field_targets:
  - funding_rule_info.funding_party_mark
  - funding_rule_detail.funding_party_mark
adjudication: boundary
also_confused_with:
  - funding_exception_resolution.funding_party_code
contract_version: "0.1"
belong: concepts
field_targets: [funding_rule_info.funding_party_mark]
sources: ["enrich:wiki-admin"]
---

「资方标识」是同一业务主体在两个域中的两种列名表达：规则域落 funding_party_mark，异常域落 funding_party_code。二者同源于资方 RPC 的 fundingKey，但列名不同、表不同，**不可互换 join**，跨域取数必须经应用层翻译而非 SQL 关联。

## 需求背景

- 规则域的资方合法性由 ClientQueryFunderMarkService 校验，且产品被硬编码为 ACFLOW（[[rule_import_funding_party_hardcoded]]）。
- 异常域的对接方标识由 ClientQueryFunderCodeService 按 productCode 分组批量校验（[[exception_import_all_or_nothing]]）。
- 上游 Provider 分别以 fundingPartyMark（规则域，[[rule_provider_active_only]]）与 fundingPartyCode（异常域，[[exception_provider_contains_match]]）作为入口参数。

## 版本演进

v0 首次建立，别名集合与判定类型取自 term_bridges：判定为 boundary，边界即「规则域 funding_party_mark / 异常域 funding_party_code 同源不同列」。本页为概念页，锚点信息仅置于 frontmatter（maps_to / field_targets / adjudication / also_confused_with）。

相关：[[funding_rule_info]]
