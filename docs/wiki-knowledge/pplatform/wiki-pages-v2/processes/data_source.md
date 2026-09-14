---
type: process
title: 数据来源状态机
page_key: data_source
domain: 项目报表/统计/上报
status: draft
aliases:
  - 数据来源
  - data_source
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:DATA_SOURCE_MANUAL
  - code_path:ProjectStatisticsApplication.java:dataSourceToChinese
contract_version: "0.1"
belong: processes
---

data_source 区分 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]] 中的记录是企微审批回流的真实数据，还是页面手工制造的模拟数据。它是[[concepts/simulated_project|模拟立项]]与[[concepts/real_project|真实立项]]两个术语的分界字段，也是统计口径中判断数据可信度的入口。

## 需求背景

需求文档未单独描述该状态机；两个值点及其中文映射均由代码常量与转换方法确认。

## 版本演进

v0 契约首版。MANUAL 记录通常与模拟单号前缀（MN）配套出现，WECHAT 记录来自企微审批。该字段非流程型状态，无迁移边。

```ground:process
name: 数据来源
field: wechat_project_approval_apply.data_source
states:
  - value: MANUAL
    label: 模拟立项
    source: code_const
  - value: WECHAT
    label: 真实立项
    source: code_const
transitions: []
evidence: code_path:ProjectStatisticsApplication.java:dataSourceToChinese
```