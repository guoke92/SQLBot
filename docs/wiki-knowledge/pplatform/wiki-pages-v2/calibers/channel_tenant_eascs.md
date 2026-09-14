---
type: caliber
title: 渠道映射租户示例怡亚通
page_key: channel_tenant_eascs
domain: 准入接入与接入密钥
status: draft
aliases:
  - 怡亚通租户
  - eascs 渠道租户
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.setEsassAuthFlag
  - db:cust_access_secret
contract_version: "0.1"
belong: calibers
---

# 渠道映射租户示例怡亚通

## 业务定位

该口径给出「渠道 → 落库租户」映射的另一个实例：怡亚通渠道的 [[concepts/db_tenant_code|数据租户标识]] 为 `eascs.beehive-scf.qhhrly.cn`。

## 需求背景

与天马同为接入方示例，用于说明同一张 [[tables/cust_access_secret|cust_access_secret]] 上不同渠道映射到不同数据租户，且可有渠道专属的鉴权开关处理（`setEsassAuthFlag`）。

## 版本演进

怡亚通渠道存在独立的鉴权标记处理逻辑（`setEsassAuthFlag`），属渠道差异化分支。

```ground:caliber
name: 渠道映射租户示例怡亚通
predicate: "cust_access_secret.db_tenant_code = 'eascs.beehive-scf.qhhrly.cn'"
scope: 怡亚通渠道接入租户
evidence: "db:db_tenant_code值分布; code:CustAccessApplication.setEsassAuthFlag"
```