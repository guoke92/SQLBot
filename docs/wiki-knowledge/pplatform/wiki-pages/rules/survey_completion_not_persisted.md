---
type: rule
title: "问卷完成态不落库"
page_key: "survey_completion_not_persisted"
domain: "customer_survey"
status: published
aliases: ["问卷完成态不落库"]
oid: 16
sources: ["code"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 问卷完成态不落库

**业务定位**：问卷完成状态依赖外部问卷星实时查询，不本地存储。

## 需求背景

问卷是否完成每次通过问卷星 OpenAPI 实时查询，不入库；`syncAndResolve` 返回的答卷状态仅用于展示，无本地状态可校验，依赖外部接口。

## 版本演进

- v0.1 初稿，基于代码证据。

```ground:rule
name: "问卷完成态不落库"
content: "问卷是否完成每次通过问卷星 OpenAPI 实时查询，不入库；syncAndResolve 返回的答卷状态仅用于展示"
impact: "无本地状态可校验，依赖外部接口"
field_targets: []
evidence: "code_path:WenjuanDisplayService.java:syncAndResolve"
```

[[wenjuan_home_display_scenario]] [[wenjuan_activity]]