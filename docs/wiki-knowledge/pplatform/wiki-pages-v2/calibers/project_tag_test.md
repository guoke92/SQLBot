---
type: caliber
title: 口径：项目标签-测试项目
page_key: project_tag_test
domain: 租户项目
status: draft
aliases: [项目标签测试项目, 测试项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:convertProjectTagFromChinese
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_project]] 中标签为"测试项目"的记录，取值由导入校验的可选值集合限定（另见 [[project_tag_production]]、[[project_tag_paused]]）。

## 需求背景
语义分析未附带需求文档锚点；测试项目需与生产数据（[[project_production_data]]）区分。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 项目标签测试项目
predicate: "tenant_project.project_tag = '测试项目'"
scope: tenant_project
evidence: "code:convertProjectTagFromChinese 校验可选值"
```