---
type: caliber
title: 口径：项目标签-暂停项目
page_key: project_tag_paused
domain: 租户项目
status: draft
aliases: [项目标签暂停项目, 暂停项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:convertProjectTagFromChinese
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_project]] 中标签为"暂停项目"的记录，取值由导入校验的可选值集合限定（另见 [[project_tag_production]]、[[project_tag_test]]）。

## 需求背景
语义分析未附带需求文档锚点；暂停项目用于标记业务上暂不推进的项目。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 项目标签暂停项目
predicate: "tenant_project.project_tag = '暂停项目'"
scope: tenant_project
evidence: "code:convertProjectTagFromChinese 校验可选值"
```