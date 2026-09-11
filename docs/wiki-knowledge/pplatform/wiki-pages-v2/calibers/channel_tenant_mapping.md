---
type: caliber
title: 渠道-租户映射口径
page_key: calibers/channel_tenant_mapping
domain: 外部渠道与银行对接
status: draft
aliases:
  - 渠道-租户映射口径
  - cust_access_secret
  - 渠道不存在
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#validateSetValue
  - code:CustAccessApplication#getDbTenantCode
  - code:CustAccessApplication#validateChangeChannelAndTenant
contract_version: "0.1"
---

# 渠道-租户映射口径

## 业务定位

该口径规定：外部渠道入站的企业数据必须落在哪个租户，不由请求参数决定，而是由渠道密钥表反查决定——以 `cust_access_secret.channel = ? AND enable = 'Y'` 查到映射行，取其 `db_tenant_code` 作为本次写入/查询的租户。查不到则抛『渠道不存在』。建档、查询、变更三条路径均使用该口径。

## 需求背景

渠道（天马、支付宝蚂蚁）与租户之间是多对一/一对多的关系，渠道方不应也无法自行指定租户；把租户归属收敛到渠道密钥表，可以让平台侧通过配置开关渠道数据去向，避免渠道伪造租户。相关写入字段见 [[tables/cust_company_info]] 的 `db_tenant_code`。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 渠道-租户映射口径
predicate: "cust_access_secret.channel = ? AND cust_access_secret.enable = 'Y' → db_tenant_code"
scope: 渠道入站建档、查询、变更均以渠道密钥表反查租户；查不到抛『渠道不存在』
evidence: "code:CustAccessApplication#validateSetValue / #getDbTenantCode / #validateChangeChannelAndTenant"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 术语：[[concepts/channel]]
- 相关口径：[[calibers/all_tenant_context]]、[[calibers/standard_api_registered]]
- 规则：[[rules/tianma_channel_key]]、[[rules/channel_archive_unified_entry]]