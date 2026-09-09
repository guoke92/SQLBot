---
type: caliber
title: 支付宝清分配置查询默认产品码
page_key: alipay_clearing_config_default_product_code
belong: calibers
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该口径定义了支付宝清分配置查询中当产品编码为空时的默认值处理规则。默认值 ACFLOW 用于保证查询路由可执行，避免因缺少参数而中断流程。

## 需求背景

产品编码为空是查询场景常见情况，默认值确保系统健壮性。

## 版本演进

初始版本，暂无变更。

```ground:caliber
name: 支付宝清分配置查询默认产品码
predicate: ProjectAlipayClearingConfigApplication.productCode IS BLANK -> 'ACFLOW'
scope: ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured 及 ClientProjectAlipayClearingConfigSyncService.getAppId
evidence: code_path:ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured,ClientProjectAlipayClearingConfigSyncService.getAppId
```

[[tables/ProjectAlipayClearingConfigQryDTO]] [[rules/同步调用点 productAppId 构建]]