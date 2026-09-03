---
type: rule
title: "运营配置更新字段空串转NULL"
page_key: "运营配置更新字段空串转NULL"
domain: "租户配置与运营邮件"
status: published
aliases: ["blankToNull规则"]
oid: 1

sources: ["semantic_analysis", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [tenant_setting_config.op_update_time, tenant_setting_config.op_update_user, tenant_setting_config.operator_email, tenant_setting_config.operator_name, tenant_setting_config.send_email]
scope:
  databases: [lowcode_pplatform]
---

业务定位：更新运营配置时，字符串字段空串转 NULL，并保留原更新人/时间到 op_update_user/op_update_time。

## 需求背景
无特定需求声明。

## 版本演进
- 暂无。

```ground:rule
name: 运营配置更新字段空串转NULL
content: "updateOperationConfigById 对字符串字段采用 blankToNull，空串按 NULL 写入；不修改标准更新人/更新时间，将原更新人/时间写入 op_update_user/op_update_time"
impact: 保证运营字段的空值语义统一，保留审计信息
field_targets:
  - tenant_setting_config.operator_email
  - tenant_setting_config.operator_name
  - tenant_setting_config.send_email
  - tenant_setting_config.op_update_user
  - tenant_setting_config.op_update_time
evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:updateOperationConfigById"
```

相关页面：[[tenant_setting_config]]