---
type: rule
title: 非标入站强制全租户上下文
page_key: rules/nonstandard_inbound_all_tenant
domain: 外部渠道与银行对接
status: draft
aliases:
  - setDbTenantCode("all")
  - 非标入站全租户
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaController#companyArchive
  - code:AlipayAntArchiveController#channelArchive
  - code:CustAccessApplication#changeCompanyInfo
contract_version: "0.1"
---

# 非标入站强制全租户上下文

## 业务定位

`TianmaController` 与 `AlipayAntArchiveController` 在处理前调用 `MetaDataThreadLocalConfig.setDbTenantCode("all")`，使跨租户建档/查询可行；标准接口 `reg` / `query` / `batchQuery` 同样置 `all`，而 `changeCompanyInfo` 使用 `try/finally` 还原原租户。

## 需求背景

渠道方入站时并不携带目标租户信息，且同一渠道可能服务多个租户，因此必须在全租户可见的上下文中完成检索与落库。需要特别注意的是：全租户上下文只解决"看得见哪些租户"，数据最终归属仍由渠道密钥表解析（见 [[calibers/channel_tenant_mapping]]），并写入企业记录自身的 `db_tenant_code`。

## 影响与约束

渠道数据不落在单一租户上下文，因此后续操作涉及的租户必须由企业记录自身的 `db_tenant_code` 决定，而不能依赖线程上下文。对变更类接口，必须保证上下文的还原（`changeCompanyInfo` 的 `finally` 分支），否则会污染同一线程的后续请求。

## 版本演进

- v0.1（本页首版）：规则来自代码语义分析，尚无需求文档或变更单佐证。

```ground:rule
name: 非标入站强制全租户上下文
content: "TianmaController 与 AlipayAntArchiveController 在处理前调用 MetaDataThreadLocalConfig.setDbTenantCode(\"all\")，使跨租户建档/查询可行；标准接口 reg/query/batchQuery 同样置 all，changeCompanyInfo 使用 try/finally 还原原租户"
impact: 渠道数据不落在单一租户上下文，需由企业记录自身 db_tenant_code 决定后续操作租户
field_targets:
  - cust_company_info.db_tenant_code
evidence: "code:TianmaController#companyArchive, AlipayAntArchiveController#channelArchive, CustAccessApplication#changeCompanyInfo（finally 还原）"
```

## 关联页面

- 口径：[[calibers/all_tenant_context]]、[[calibers/channel_tenant_mapping]]、[[calibers/batch_query_limit]]
- 规则：[[rules/channel_archive_unified_entry]]
- 概念：[[concepts/channel]]
- 载体表：[[tables/cust_company_info]]