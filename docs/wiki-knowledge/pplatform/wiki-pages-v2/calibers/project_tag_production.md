---
type: caliber
title: 口径：项目标签-生产项目
page_key: project_tag_production
domain: 租户项目
status: draft
aliases: [项目标签生产项目, 生产项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:convertProjectTagFromChinese
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_project]] 中标签为"生产项目"的记录，取值由导入校验的可选值集合限定（另见 [[project_tag_test]]、[[project_tag_paused]]）。

## 需求背景
语义分析未附带需求文档锚点；项目标签用于区分生产/测试/暂停项目，导入时需校验取值。

## 版本演进
语义分析未记录该口径的版本演进；标签落库形态（枚举码或中文）与字段语义描述不一致，已在 [[tenant_project]] 的 REVIEW 中记录。

```ground:caliber
name: 项目标签生产项目
predicate: "tenant_project.project_tag = '生产项目'"
scope: tenant_project
evidence: "code:convertProjectTagFromChinese 校验可选值"
```