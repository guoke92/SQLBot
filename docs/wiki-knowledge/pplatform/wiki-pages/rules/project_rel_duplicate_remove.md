---
type: rule
title: 项目关系重复移除后重插
page_key: project_rel_duplicate_remove
domain: 租户迁移
status: published
aliases: []
oid: 26
sources: [code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：避免迁移时项目关系重复。

## 需求背景
迁移时项目关系需唯一。

## 版本演进
v0.1 基于代码证据。

```ground:rule
name: 项目关系重复移除后重插
content: setCustProjectRel 查同 projectId+cust公司code+db_tenant_code 的已有 cust_project_rel，先 removeBatchByIds 再保存新关系
impact: 避免迁移时项目关系重复
field_targets: [cust_project_rel]
evidence: "code_path:PlatFormMigratoryApplication.java:setCustProjectRel"
```

关联：[[project_must_exist]]