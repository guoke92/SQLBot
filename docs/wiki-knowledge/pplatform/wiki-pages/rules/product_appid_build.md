---
type: rule
title: 同步调用点 productAppId 构建
page_key: product_appid_build
belong: rules
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则定义同步调用点时 productAppId 的构建方式：使用 qyDto.productCode（默认 ACFLOW）作为列表元素。

## 需求背景

确定下游应用路由，保证请求能够到达正确应用服务。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 同步调用点 productAppId 构建
content: ClientProjectAlipayClearingConfigSyncService.getAppId 使用 qyDto.productCode（默认 ACFLOW）作为 productAppId 列表元素
impact: 确定下游应用路由
field_targets: ["productCode", "productAppId"]
evidence: code_path:ClientProjectAlipayClearingConfigSyncService.getAppId
```

[[productCode]] [[alipay_clearing_config_default_product_code]]