---
type: caliber
title: 出向推数口径
page_key: outbound_push
domain: 租户迁移
status: draft
aliases: [推数口径, direction=OUT]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:MigratoryPointServiceImpl.java#pushByLog"
  - "db:tenant_migarory_log"
contract_version: "0.1"
belong: calibers
---

出向推数的判定口径：`direction='OUT'` 且 type 不含 `SYNC_VALIDATE`。数据量上入向 123405 条远大于出向 29764 条，因此不能用记录数判断迁移与同步的业务重要性。该口径是 [[failed_migratory_log]] 重试的前置条件。

```ground:caliber
name: 出向推数口径
predicate: "tenant_migarory_log.direction = 'OUT'"
scope: "pushByLog 只重推 OUT 方向、且 type 不含 SYNC_VALIDATE 的记录"
evidence: "code:MigratoryPointServiceImpl.java#pushByLog + db(IN:123405/OUT:29764)"
```

## 需求背景

推数失败需要能按请求号重放，但校验器类记录（`*_SYNC_VALIDATE`）只反映校验结果，不承载可重放的业务载荷，重放会污染业务系统，须排除在口径外。

## 版本演进

早期重推未区分方向与校验器，现通过 direction + type 双条件收窄；详见 [[同步]]。