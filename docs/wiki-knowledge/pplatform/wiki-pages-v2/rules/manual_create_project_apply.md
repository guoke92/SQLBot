---
type: rule
title: 模拟立项规则
page_key: manual_create_project_apply
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:ProjectStatisticsApplication.java:manualCreate
contract_version: "0.1"
belong: rules
---

手工创建（模拟）立项数据时的编号生成、来源标记与责任人赋值规则。

```ground:rule
name: 模拟立项规则
content: 模拟立项 spNo 由后端生成（MN-yyyyMMdd-XXXX），dataSource 强制 MANUAL，方案经理固定为当前登录用户，写 MANUAL_CREATE 字段历史。
impact: 支持手工创建测试或补录立项数据。
field_targets:
  - wechat_project_approval_apply.sp_no
  - wechat_project_approval_apply.data_source
  - wechat_project_approval_apply.solution_manager
evidence: code_path:ProjectStatisticsApplication.java:manualCreate
```

## 需求背景

模拟立项产生的记录不会被企微审批导出命中，因为它不满足导出硬过滤中的来源条件，见 [[calibers/wechat_approval_export]] 与 [[concepts/data_source]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。