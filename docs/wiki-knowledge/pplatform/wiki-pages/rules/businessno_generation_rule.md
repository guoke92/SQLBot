---
type: rule
title: businessNo 生成规则
page_key: rule/businessno_generation_rule
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则定义 FBP 业务号 businessNo 的生成逻辑：优先使用入参 businessNo，若为空则生成 UUID。

## 需求背景

FBP 调用需要业务号来标识业务上下文，缺少时自动生成确保流程继续。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: businessNo 生成规则
content: BaseClientSyncService.getBusinessNo 优先取入参 v.businessNo，若空则生成 UUID
impact: 保证 FBP 业务号存在
field_targets: ["businessNo"]
evidence: code_path:BaseClientSyncService.getBusinessNo
```

[[fbp_protocol]]