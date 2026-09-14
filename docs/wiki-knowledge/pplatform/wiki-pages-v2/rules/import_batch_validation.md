---
type: rule
title: 导入整批校验
page_key: import_batch_validation
domain: 项目报表/统计/上报
status: draft
aliases:
  - 导入整批校验
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.validateAndApply
contract_version: "0.1"
belong: rules
---

项目台账导入与项目立项统计导入都采用整批事务式校验：只要任意一行校验失败，整批数据都不落库。这保证了导入结果的原子性，代价是用户必须修完所有错误行才能重新提交。

## 需求背景

需求文档未单列此规则；规则内容来自导入校验方法语义。

## 版本演进

v0 契约首版。影响面：导入操作。本规则无字段级目标（field_targets 为空），其约束体现在事务边界而非某个列上；与其他导入期规则（如[[rules/project_phase_linkage|项目阶段联动]]、[[rules/batch_change_plan_mgr_limit|批量变更方案经理限制]]）叠加生效。

```ground:rule
name: 导入整批校验
content: 项目台账导入和项目立项统计导入均整批校验，任一行错误则整批不落库
impact: 导入操作
field_targets: []
evidence: code_path:ProjectStatisticsApplication.validateAndApply
```