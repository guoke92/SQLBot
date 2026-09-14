---
type: caliber
title: 全租户上下文口径
page_key: all_tenant_context
domain: 外部渠道与银行对接
status: draft
aliases:
  - 全租户上下文口径
  - dbTenantCode = all
  - MethDataThreadLocalConfig
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaController#companyArchive
  - code:AlipayAntArchiveController#channelArchive
  - code:CustAccessApplication#reg
  - code:CustAccessApplication#query
  - code:CustAccessApplication#batchQuery
  - code:CustAccessApplication#changeCompanyInfo
contract_version: "0.1"
belong: calibers
---

# 全租户上下文口径

## 业务定位

该口径规定：渠道入站与标准开放接口在处理前，把线程上下文租户置为 `"all"`（`MethDataThreadLocalConfig.setDbTenantCode("all")`），从而使跨租户检索/写入成为可能；`changeCompanyInfo` 则在 `finally` 中还原原租户。它约束的是"这次操作能看见哪些租户的数据"，而不是数据最终落在哪个租户。

## 需求背景

渠道方在入站时并不知道目标租户，且同一渠道可能服务多个租户，因此必须以全租户上下文执行查询与落库；真正的租户归属由 [[calibers/channel_tenant_mapping]] 从渠道密钥表解析后写入记录自身字段。两者是"检索可见范围"与"数据归属"的分工，不可混淆。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 全租户上下文口径
predicate: "dbTenantCode = 'all'"
scope: "MethDataThreadLocalConfig.setDbTenantCode(\"all\")，用于渠道入站与开放接口跨租户检索；changeCompanyInfo 在 finally 中还原原租户"
evidence: "code:TianmaController#companyArchive / AlipayAntArchiveController#channelArchive / CustAccessApplication#reg、#query、#batchQuery、#changeCompanyInfo"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/channel_tenant_mapping]]
- 规则：[[rules/nonstandard_inbound_all_tenant]]、[[rules/channel_archive_unified_entry]]
- 术语：[[concepts/channel]]