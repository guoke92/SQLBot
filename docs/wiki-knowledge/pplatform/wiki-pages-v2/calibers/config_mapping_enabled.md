---
type: caliber
title: 配置映射启用
page_key: config_mapping_enabled
domain: 平台产品配置
status: draft
aliases: [cust_config_mapping.enable=Y]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「配置映射启用」是 `getConfig` / `listConfig` 查询 [[cust_config_mapping]] 时的启用过滤口径，`enable = 'Y'`。

## 需求背景

企业角色到平台产品编码的映射查询依赖该过滤（[[company_type]]、[[config_mapping_filter_key]]）；产品扩展配置不落本表，见 [[product_ext_config_from_nacos]]。

## 版本演进

- 初版口径，无历史变更。

```ground:caliber
name: 配置映射启用
predicate: "cust_config_mapping.enable = 'Y'"
scope: getConfig/listConfig 查询
evidence: code
```

关联：[[cust_config_mapping]]、[[config_mapping_filter_key]]、[[product_ext_config_from_nacos]]