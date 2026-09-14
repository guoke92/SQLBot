---
type: caliber
title: 口径：项目生产数据
page_key: project_production_data
domain: 租户项目
status: draft
aliases: [项目生产数据, 是否生产数据]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:exportProjectInfo
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_project]] 中属于生产数据的项目（`is_prd='Y'`）。导出时 Y 转"是"、N 转"否"；洞察平台导出另有 1/0 兼容逻辑。

## 需求背景
语义分析未附带需求文档锚点；项目数据需要区分生产与测试，避免测试项目进入生产统计。

## 版本演进
语义分析未记录该口径的版本演进；1/0 兼容逻辑提示历史写值口径不一致。

```ground:caliber
name: 项目生产数据
predicate: "tenant_project.is_prd = 'Y'"
scope: tenant_project
evidence: "code:导出判断 Y 为是，N 为否"
```