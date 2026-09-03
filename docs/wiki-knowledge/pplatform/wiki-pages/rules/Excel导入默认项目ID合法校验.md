---
type: rule
title: "Excel导入默认项目ID合法校验"
page_key: "Excel导入默认项目ID合法校验"
domain: "租户配置与运营邮件"
status: published
aliases: ["Excel导入项目ID校验"]
oid: 1

sources: ["semantic_analysis", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [tenant_setting_config.default_project_id]
scope:
  databases: [lowcode_pplatform]
---

业务定位：导入 Excel 时，默认项目 ID 若存在，必须为数字且对应 tenant_project 存在，否则该行失败。

## 需求背景
BR-012 默认项目 ID 合法性校验（需求：必须为当前租户下已存在且 rule_status=A 的项目）。

## 版本演进
- 暂无。

```ground:rule
name: Excel导入默认项目ID合法校验
content: "导入行中 default_project_id 若存在，必须为数字且对应 tenant_project 存在，否则该行失败"
impact: 防止无效项目ID写入租户配置
field_targets:
  - tenant_setting_config.default_project_id
  - tenant_project.id
evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:importTenantOperationConfig"
```

```ground:reqdoc
claims:
  - claim: "BR-012 默认项目 ID 合法性校验（需求：必须为当前租户下已存在且 rule_status=A 的项目）"
    code_status: confirmed
    code_evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:importTenantOperationConfig + reqdoc:BR-012"
```

相关页面：[[tenant_setting_config]] [[tenant_project]] [[defaultProjectId]]