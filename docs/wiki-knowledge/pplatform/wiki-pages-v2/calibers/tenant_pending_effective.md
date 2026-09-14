---
type: caliber
title: 待生效租户口径（status='N'）
page_key: tenant_pending_effective
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [待生效租户, status='N']
oid: 1
scope:
  databases: [unknown]
sources:
  - "db:tenant_setting_config.status N=240"
contract_version: "0.1"
belong: calibers
---

「待生效租户」指尚未通过 `effective()` 校验、状态仍为 N 的租户，迁移租户大部分落在此集合中。导出时该状态（含空值）统一展示为『待生效』，因此展示口径比 `status='N'` 略宽。

状态迁移过程见 [[tenant_status_effective]]；对比口径见 [[tenant_effective]]。

## 需求背景
存量迁移租户与新开租户都需要一个可识别的未完成态，便于运营在列表中识别并推进配置。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；空状态是否计入本口径待复核（见 REVIEW）。

```ground:caliber
name: 待生效租户
predicate: "tenant_setting_config.status = 'N'"
scope: "未通过 effective 校验的租户（含全部迁移租户）"
evidence: "db:status N=240"
```