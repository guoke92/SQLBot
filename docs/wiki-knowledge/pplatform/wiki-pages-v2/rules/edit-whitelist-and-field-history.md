---
type: rule
title: 编辑白名单与字段历史保护
page_key: edit-whitelist-and-field-history
domain: 项目报表/统计/上报
status: draft
aliases:
  - 白名单编辑
  - 同步保护字段
  - writeChangedColumns
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
belong: rules
---

# 编辑白名单与字段历史保护

立项统计的编辑保存并非整行覆写：只有白名单列参与 diff 比较与写库，并同步落一条字段历史；被人工写过的「同步保护字段」在企微同步写库前会被跳过。

## 需求背景

立项单据部分字段来自企微同步，部分是统计侧人工维护。若同步 Job 直接覆写整行，会冲掉人工修改；若编辑保存直接整行更新，又会制造大量无意义变化。因此采用双向约束：编辑侧限定白名单 + 差异写库，同步侧过滤保护字段。字段历史来源枚举见 [[tables/wechat_project_approval_apply_field_history]]，涉及的表为 [[tables/wechat_project_approval_apply]]。

## 版本演进

历史来源目前覆盖 EDIT/BATCH/MANUAL_CREATE/IMPORT 四类，说明批量变更、模拟立项与导入链路已陆续纳入同一审计机制；保护字段集以「已被人工写入」为动态判定，属后期补强的防覆盖设计。

```ground:rule
name: "编辑白名单与字段历史保护"
content: "编辑保存只对 EDITABLE_JAVA_FIELDS 白名单中的列做 diff 写库，并写入 wechat_project_approval_field_history（source=EDIT/BATCH/MANUAL_CREATE/IMPORT）；已被人工写入的「同步保护字段集」对应列，企微同步 Job 在写库前需过滤跳过。"
impact: "保护人工修改不被企微同步覆盖；未命中差异的列不落库不写历史"
field_targets:
  - "wechat_project_approval_apply.*（白名单列）"
  - "wechat_project_approval_field_history.*"
evidence: "code_path:ProjectStatisticsApplication.java:update + writeChangedColumns"
```