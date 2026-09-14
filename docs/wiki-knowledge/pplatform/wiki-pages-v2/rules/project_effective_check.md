---
type: rule
title: 进入产品项目生效校验
page_key: project_effective_check
domain: 平台产品配置
status: draft
aliases: [multiple_project_flag, 关联项目校验]
oid: 1
scope:
  databases: [platform]
sources:
  - code:PlatformProductApplication.java#gotoProductSupplierFirstRelatedProject
  - code:projectRelProductRangeAdapter.listProject
contract_version: "0.1"
belong: rules
---

(document_claim，未证实)

当 [[platform_product]] 的 `multiple_project_flag='Y'` 且产品为 [[general_product]] 时，进入产品前必须校验企业关联项目生效（`projectRelProductRangeAdapter.listProject`），否则返回「暂无操作权限」。

## 需求背景

该规则与多企业角色校验（[[cust_role_combine_antifraud]]）共同构成进入产品的前置闸口；平台运营方被豁免，见 [[platform_operator_exemption]]。

## 版本演进

- 需求文档 2.2「租户项目生命周期 effective/invalid/change/delete 与 SyncTenantProjectJobHandle 下游同步」在证据中未展开，`TenantProjectApplication` 仅被 codemap 提及，属未证实主张，暂记于本页。

```ground:rule
name: 进入产品项目生效校验
content: "platform_product.multiple_project_flag=Y 且产品为通用类型时，需企业关联项目生效(projectRelProductRangeAdapter.listProject)，否则返回 暂无操作权限"
impact: 未关联生效项目禁止进入产品
field_targets:
  - platform_product.multiple_project_flag
  - tenant_project.project_status
evidence: "code_path:PlatformProductApplication.java#gotoProductSupplierFirstRelatedProject"
```

关联：[[platform_product]]、[[general_product]]、[[platform_operator_exemption]]