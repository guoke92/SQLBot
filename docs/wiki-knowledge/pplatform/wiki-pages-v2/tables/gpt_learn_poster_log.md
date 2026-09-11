---
type: table
title: gpt_learn_poster_log（智能审核引流卡片弹出/点击日志）
page_key: tables/gpt_learn_poster_log
domain: GP学习
status: draft
aliases:
  - 引流卡片日志
  - 智能审核引流卡片记录
  - gptlearn 弹出记录
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:gpt_learn_poster_log
  - code:GptLearnService.java
contract_version: "0.1"
---


# gpt_learn_poster_log（智能审核引流卡片弹出/点击日志）

本表是「[[concepts/gptlearn]]」（代码与接口层统一写作 gptlearn、前端与业务口称智能审核引流／GP 学习）的埋点载体。它记录引流卡片对某个企业下的某个用户「是否弹出过」「是否被点击过」两类事实：`popup_time` 由 `checkPosterStatus` 创建弹出记录时写入，`click_time` 由 `recordPosterClick` 记录点击时写入。表同时冗余了企业与用户的名称字段（`company_id`/`company_name`、`user_id`/`user_name`），使投放侧可以在不联表的情况下统计曝光与点击。

该表也是「[[calibers/gptlearn_poster_count_limit]]」的计数依据——弹出次数上限按 `user_id` + `company_id` 聚合本表记录来判定，因此本表的写入时机（而不是卡片实际渲染）决定了限流口径。

表内带有 `db_tenant_code`（数据租户标识）与 `app_tenant_code`（逻辑租户标识）两级租户字段，以及 `enable` 逻辑有效标识（DB 实测均为 Y），与本域其它表保持一致的租户隔离形态。

## 需求背景

本分析未提供针对该表的需求文档（reqdoc_claims）证据，页面内容全部以 DB 字段语义与 `GptLearnService` 代码证据为准。需要业务侧补充：卡片投放的目标人群定义、弹出上限的运营预期值（对应 `gptLearnProperties.maxPosterCount`）以及允许投放的租户白名单（对应 `gptLearnProperties.posterAllowedTenant`）来源。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。该表在当前分析中未被标注为 document_claim（未证实）内容。

```ground:table
table: gpt_learn_poster_log
database: lowcode_pplatform
desc: 智能审核引流卡片埋点记录
fields:
  - name: id
    type: number
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: click_time
    type: temporal
    desc: 卡片点击时间
  - name: code
    type: string
    desc: 编码
  - name: company_id
    type: number
    desc: 企业ID
  - name: company_name
    type: string
    desc: 企业名称
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: popup_time
    type: temporal
    desc: 卡片弹出时间
  - name: remark
    type: string
    desc: remark
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
  - name: user_id
    type: number
    desc: 用户ID
  - name: user_name
    type: string
    desc: 用户名
```

相关页面：[[tables/cust_company_info]]、[[calibers/gptlearn_finance_user]]、[[calibers/gptlearn_tenant_whitelist]]、[[calibers/gptlearn_poster_count_limit]]、[[processes/cust_company_info_cust_build_status]]。