---
type: rule
title: 支付宝清分配置查询企业ID必填
page_key: alipay_clearing_config_company_id_required
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

该规则约束支付宝清分配置查询时企业 ID 为必填项。缺少时抛出业务异常，阻断查询流程。

## 需求背景

企业 ID 是查询的核心定位参数，缺失会导致无法确定查询目标，因此必须强制校验。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 支付宝清分配置查询企业ID必填
content: 在 ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured 中，若 companyId 为 null，抛出 BaseException("企业ID不能为空")
impact: 阻断查询，返回业务异常
field_targets: ["companyId"]
evidence: code_path:ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured
```

[[tables/ProjectAlipayClearingConfigQryDTO]] [[company_id]]