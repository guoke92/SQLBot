---
type: rule
title: 产品扩展配置来源 Nacos
page_key: product_ext_config_from_nacos
domain: 平台产品配置
status: draft
aliases: [getProductExtConfig, app-list.yml, clientConfig]
oid: 1
scope:
  databases: [platform]
sources:
  - code:PlatformProductApplication.java#getProductExtConfig
  - code:NacosFacade.java#listProductApp
contract_version: "0.1"
belong: rules
---

`getProductExtConfig` / `getProductConfig` 读取 Nacos `app-list.yml` 中的 `extConfig` / `clientConfig`（经 `nacosFacade.listProductApp()`），产品扩展与页面配置查询不落库。[[cust_config_mapping]] 只服务 `getConfig` / `listConfig` 的 `type+innerCode+outerChannel` 查询，两者来源不同，不可混用。

## 需求背景

需求文档 BR-003 主张扩展配置按 productCode+key+expectedValue 三元组查询 `cust_config_mapping`，代码证据证伪该主张，详见 [[cust_config_mapping]]。

## 版本演进

- BR-003 首次契约化即标记为 refuted，本规则固化「Nacos 为准」的实现事实。

```ground:rule
name: 产品扩展配置来源 Nacos
content: "getProductExtConfig/getProductConfig 读取 app-list.yml 的 extConfig/clientConfig，而非 cust_config_mapping 表"
impact: 产品扩展/页面配置查询不落库
field_targets:
  - platform_product.product_code
evidence: "code_path:PlatformProductApplication.java#getProductExtConfig;NacosFacade.java#listProductApp"
```

关联：[[cust_config_mapping]]、[[platform_product]]、[[config_mapping_filter_key]]