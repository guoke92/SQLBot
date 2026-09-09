---
type: rule
title: Excel导入运营配置规则
page_key: excel-import-operation-config-rule
belong: rules
domain: tenant-config-operation-email
status: published
aliases: [Excel导入运营配置规则, importTenantOperationConfigByFile]
oid: 1
sources: [code, reqdoc]
contract_version: "0.1"
field_targets: [tenant_setting_config.default_project_id, tenant_setting_config.project_code_required]
scope:
  databases: [lowcode_pplatform]
---

该规则描述通过 Excel 导入更新租户运营配置的流程，包括按行更新项目码是否必填与默认项目 ID，校验项目标识存在性等。

## 需求背景

运营侧需要批量更新租户的项目码必填与默认项目配置，通过 Excel 导入可提高效率。导入过程需保证项目标识存在、默认项目 ID 存在等约束。

## 版本演进

- 初版（v0.1）：基于 `TenantAppliactionService.importTenantOperationConfigByFile` 实现。
- BR-011 差异：代码中项目标识存在性校验实际通过 `tenantDomainService.getFirstByTenantFlgEn` 在 `tenant_setting_config` 中查询，而非 by `tenant_project`。
- BR-012 差异：默认项目 ID 仅校验了存在性（`tenantProjectService.getById`），未校验属于当前租户或 `rule_status=A`。

```ground:rule
name: Excel导入运营配置规则
content: "解析Excel，按行更新项目码是否必填、默认项目ID；项目标识不存在则报错；默认项目ID仅当当前值为null且ID存在时更新"
impact: 更新tenant_setting_config.project_code_required和default_project_id
field_targets:
  - tenant_setting_config.project_code_required
  - tenant_setting_config.default_project_id
evidence: "code_path:TenantAppliactionService.importTenantOperationConfigByFile"
```

---REVIEW: rule | Excel导入运营配置规则---
BR-010 主张“表头必须按顺序包含特定列，列名错位则整体失败”未能证实：代码使用 `EasyExcel.read` 直接映射，未显式校验表头顺序。建议与业务确认是否需要增加表头顺序校验。
---END REVIEW---

[[tenant_setting_config]] [[tenant_project]] [[tenant_flg_en]]