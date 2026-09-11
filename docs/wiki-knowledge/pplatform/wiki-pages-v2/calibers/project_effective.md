---
type: caliber
title: 租户项目有效口径
page_key: calibers/project_effective
domain: 租户项目
status: draft
aliases: [项目有效口径, project_status, enable='Y']
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
  - code:ProjectStatusEnum
contract_version: "0.1"
---

「项目是否有效」在本主题里由两个维度共同决定：[[tables/tenant_project]] 的 enable 表示逻辑删除（查询与导出普遍限定 enable='Y'），project_status 表示业务上的生效/失效。二者独立，判断一个项目能否被业务使用时需同时成立。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该口径支撑项目列表、导出与按产品同步等查询场景，见 [[rules/tenant_project_enable_filter]]。

## 版本演进
- 删除走 domainService.delete 而非物理删除，enable 承担历史数据过滤职责。
- project_status 的失效值拼写为 INVLIAD，见 [[processes/tenant_project_status]]。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 租户项目有效口径
fields:
  - table: tenant_project
    field: enable
    values: ["Y", "N"]
    definition: 逻辑删除/有效标记；代码查询与导出普遍限定 enable='Y'，删除操作调用 domainService.delete
    evidence: code
  - table: tenant_project
    field: project_status
    values: [EFFECTIVE, INVLIAD]
    definition: 项目状态；代码使用 ProjectStatusEnum.EFFECTIVE 与 ProjectStatusEnum.INVLIAD，分别表示已生效、已失效
    evidence: code
```