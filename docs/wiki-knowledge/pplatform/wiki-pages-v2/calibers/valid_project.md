---
type: caliber
title: 口径：有效项目
page_key: valid_project
domain: 租户项目
status: draft
aliases: [有效项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:exportProjectInfo
  - code:updateProjectData
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_project]] 中未被逻辑删除的项目（`enable='Y'`）。导出与更新任务均以此为准，是 [[project_effective]] 之外的另一层过滤。

## 需求背景
语义分析未附带需求文档锚点；项目删除走逻辑删除，查询与导出必须显式带上有效标记。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 有效项目
predicate: "tenant_project.enable = 'Y'"
scope: tenant_project
evidence: "code:exportProjectInfo/updateProjectData 均按 enable='Y' 查询"
```