---
type: rule
title: 引流卡片仅白名单租户可弹
page_key: poster_allowed_tenant
domain: 客户管理
status: draft
aliases: [租户灰度, isPosterAllowedTenant]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:checkPosterStatus
  - db:gpt_learn_poster_log.db_tenant_code
contract_version: "0.1"
belong: rules
---

`isPosterAllowedTenant(companyInfo.getDbTenantCode())` 为 false 时 `checkPosterStatus` 直接返回 `notShow`。租户取自 [[tables/cust_company_info]]，落点字段是 [[tables/gpt_learn_poster_log]] 的 `db_tenant_code`（见 [[enums/gpt_learn_poster_log_db_tenant_code]]）。

## 需求背景

引流卡片按数据租户灰度投放。DB 实测埋点仅落在 `beehive-scf.qhhrly.cn` 一个租户值上，与该白名单机制吻合。

## 版本演进

- 当前观测：`db_tenant_code` 唯一值 `beehive-scf.qhhrly.cn`，白名单范围目前极窄。

```ground:rule
name: 引流卡片仅白名单租户可弹
content: isPosterAllowedTenant(companyInfo.getDbTenantCode()) 为 false 时直接 notShow
impact: 按 db_tenant_code 灰度投放引流卡片；DB 实测埋点仅落在 beehive-scf.qhhrly.cn
field_targets:
  - gpt_learn_poster_log.db_tenant_code
evidence: "code_path:GptLearnService.java:checkPosterStatus + db:gpt_learn_poster_log.db_tenant_code"
```