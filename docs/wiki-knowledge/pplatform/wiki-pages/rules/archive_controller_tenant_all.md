---
type: rule
title: 建档控制器设置租户为 all
page_key: archive_controller_tenant_all
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

该规则要求建档控制器在调用服务前将当前线程的 dbTenantCode 设置为 "all"，实现跨租户处理。

## 需求背景

支付宝蚂蚁建档请求需要跨租户查询或写入数据，因此绕过单一租户隔离。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 建档控制器设置租户为 all
content: AlipayAntArchiveController.channelArchive 在调用服务前执行 MetaDataThreadLocalConfig.setDbTenantCode("all")
impact: 该请求跨租户处理，不按单一租户隔离
field_targets: ["dbTenantCode"]
evidence: code_path:AlipayAntArchiveController.channelArchive
```

[[channel_archive]]