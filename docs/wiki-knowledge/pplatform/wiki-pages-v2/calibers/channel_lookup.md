---
type: caliber
title: 渠道查询
page_key: channel_lookup
domain: 准入接入
status: draft
aliases: [渠道口径, channel 查询, 按渠道取租户]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:getDbTenantCode"
contract_version: "0.1"
belong: calibers
---

「渠道查询」定义准入接入时如何由渠道定位租户：以 `cust_access_secret.channel = '渠道值'` 检索 [[tables/cust_access_secret]]，命中记录的 `db_tenant_code` 即为后续请求需要设置的租户上下文。

该口径是租户路由的前置步骤，其输出被 [[rules/channel_tenant_exists]] 继续用于校验租户配置是否可用。渠道术语本身见 [[concepts/channel]]，密钥术语见 [[concepts/access_secret]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；口径定义来自 `CustAccessApplication.getDbTenantCode` 的代码证据。

## 版本演进

- v0.1（本页）：首版口径，来源为 `getDbTenantCode`。

```ground:caliber
name: 渠道查询
predicate: "cust_access_secret.channel = '渠道值'"
scope: 根据渠道获取租户编码
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:getDbTenantCode"
```