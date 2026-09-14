---
type: caliber
title: 渠道映射租户示例天马
page_key: channel_tenant_tianma
domain: 准入接入与接入密钥
status: draft
aliases:
  - 天马租户
  - tianma 渠道租户
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.validateSetValue
  - db:cust_access_secret
contract_version: "0.1"
belong: calibers
---

# 渠道映射租户示例天马

## 业务定位

该口径给出「渠道 → 落库租户」映射的一个实例：天马渠道的 [[concepts/db_tenant_code|数据租户标识]] 为 `tianma.beehive-scf.qhhrly.cn`。开放 API 校验通过渠道定位到该租户后，后续建档数据落入对应租户。

## 需求背景

接入渠道与数据租户是多对一关系，映射由 [[tables/cust_access_secret|cust_access_secret]] 承载，不能由请求方自带租户参数决定。

## 版本演进

天马渠道另有专属校验分支（`validateSetValueOfTianma`），包含重复校验排除已注销（[[calibers/tianma_duplicate_exclude_writeoff|天马重复校验排除已注销]]），说明该渠道存在差异化的接入策略。

```ground:caliber
name: 渠道映射租户示例天马
predicate: "cust_access_secret.db_tenant_code = 'tianma.beehive-scf.qhhrly.cn'"
scope: 天马渠道接入租户
evidence: "db:db_tenant_code值分布; code:CustAccessApplication.validateSetValue"
```