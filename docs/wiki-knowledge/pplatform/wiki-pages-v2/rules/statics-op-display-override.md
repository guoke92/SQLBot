---
type: rule
title: 展示用统计操作时间覆盖更新时间
page_key: rule/statics-op-display-override
domain: 微企链立项与项目审批
status: draft
aliases:
  - statics_op_time 展示覆盖
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

列表与详情展示的「更新时间/更新人」并非直接取 `update_time` / `update_user`，而是被 `statics_op_time` / `statics_op_user`（项目统计更新时间与更新用户）覆盖。因此界面上的更新时间反映的是统计操作，而不是记录行级变更。

阅读审计信息时须注意这一层覆盖，字段语义见 [[tables/wechat_project_approval_apply]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 展示用统计操作时间覆盖更新时间
subject: wechat_project_approval_apply.statics_op_time
evidence: code
source_meaning: 项目统计更新时间；列表/详情展示时覆盖 update_time
```