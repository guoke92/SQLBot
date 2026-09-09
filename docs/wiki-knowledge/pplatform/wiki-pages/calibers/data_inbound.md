---
type: caliber
title: 数据入站口径
page_key: data_inbound
belong: calibers
domain: 租户迁移
status: published
aliases: [数据入站]
oid: 12
sources: [db]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：区分入站/出站数据同步量。

## 需求背景
需要统计 IN 方向的数据同步量。

## 版本演进
v0.1 基于 DB 字段谓词。

```ground:caliber
name: 数据入站口径
predicate: tenant_migarory_log.direction = 'IN'
scope: 区分入站/出站数据同步量
evidence: db
```

关联：[[tenant_migarory_log]]