---
type: process
title: 模拟立项/真实立项数据来源
page_key: project-data-source
domain: 项目报表/统计/上报
status: draft
aliases:
  - data_source
  - 模拟立项
  - 真实立项
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsDevImportApplication.java
contract_version: "0.1"
belong: processes
---

# 模拟立项/真实立项数据来源

`data_source` 描述 [[tables/wechat_project_approval_apply]] 中一条立项单据的产生方式：由企微同步而来的真实立项，或由后端手工/开发用导入产生的模拟立项。它决定编号形态（spNo 是否以 MN 开头）与数据可信度，详见 [[rules/manual-project-spno]]。

## 需求背景

为支持统计页在无真实企微审批数据时的演示与联调，系统允许手工新增模拟立项：字段与真实立项一致，但数据来源标记为 MANUAL，编号由后端按固定表达式生成，列表与导出按 spNo 前缀识别。真实立项保持 WECHAT 取值。「数据来源」这一中文词在项目台账侧另有 source 语义（产融/讯易链），两者的分域见 [[concepts/data-source]]。

## 版本演进

MANUAL 来源为演示/联调场景引入，其编号规则由 generateManualSpNo 固定表达式承载；开发用导入链路（buildManualEntityForInsert）可批量插入模拟立项空白编号行，说明模拟能力已从单条手工新增扩展到批量导入。

```ground:state_machine
name: "模拟立项/真实立项数据来源"
field: wechat_project_approval_apply.data_source
states:
  - value: "MANUAL"
    label: "模拟立项（spNo 以 MN 开头）"
    source: code_enum
  - value: "WECHAT"
    label: "真实立项"
    source: code_enum
transitions:
  - from: "无"
    event: "manualCreate / 开发用导入空白编号行"
    to: "MANUAL"
    evidence: "code_path:ProjectStatisticsApplication.java:manualCreate + ProjectStatisticsDevImportApplication.java:buildManualEntityForInsert"
```