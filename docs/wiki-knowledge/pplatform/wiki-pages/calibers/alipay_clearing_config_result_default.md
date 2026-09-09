---
type: caliber
title: 支付宝清分配置结果缺省值
page_key: alipay_clearing_config_result_default
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

该口径定义支付宝清分配置查询响应组装时的缺省值处理：configured 为 NULL 时返回 FALSE，companyId 为 NULL 时回退为请求 companyId。确保响应具备明确业务含义。

## 需求背景

响应字段可能因下游缺失而为空，缺省值避免调用方处理空值。

## 版本演进

初始版本，暂无变更。

```ground:caliber
name: 支付宝清分配置结果缺省值
predicate: ProjectAlipayClearingConfigRespDTO.configured IS NULL -> FALSE；companyId IS NULL -> 请求 companyId
scope: ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured 响应组装
evidence: code_path:ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured
```

[[tables/ProjectAlipayClearingConfigRespDTO]] [[is_alipay_clearing_configured]]