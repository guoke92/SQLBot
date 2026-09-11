---
type: table
title: 立项审批申请表（wechat_project_approval_apply）
page_key: table.wechat_project_approval_apply
domain: 项目报表/统计/上报
status: draft
aliases:
  - wechat_project_approval_apply
  - 企微立项审批申请表
  - 项目立项统计表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsDevImportApplication.java
  - code:ProjectStatisticsRemindApplication.java
contract_version: "0.1"
---

# 立项审批申请表（wechat_project_approval_apply）

wechat_project_approval_apply 是「项目立项统计」主题的事实表，承载企微审批同步而来的立项单据，并叠加统计侧维护的展示列与人工可编辑列。项目阶段流转见 [[processes/project-phase]]，审批状态见 [[processes/project-approval-status]]，数据来源见 [[processes/project-data-source]]，列表基础口径见 [[calibers/project-statistics-list-base]]，审批通过口径见 [[calibers/project-ledger-approved]]。

## 需求背景

立项统计页需要按「金融科技业务 + SaaS/SaaS+本地化」范围展示、导出、下拉字典与提醒（见 [[calibers/project-statistics-list-base]]、[[calibers/missing-solution-manager-remind]]），并支持人工编辑方案经理、首笔落地时间等字段。为此本表既保留审批同步字段（sp_type、system_delivery、act_procinst_status、project_phase 等），又扩展出统计侧冗余列（statics_op_time/statics_op_user），并要求方案经理姓名与企微 userId 冗余列联动维护（见 [[rules/manager-wechat-identity-validation]]）、前方案经理前置合并（见 [[rules/old-solution-manager-merge]]）。字段变更需落历史，见 [[tables/wechat_project_approval_apply_field_history]] 与 [[rules/edit-whitelist-and-field-history]]。

## 版本演进

- `project_phase` 历史上存在 `TERMINATION` 取值，读取时归一为 `HANG`；「立项阶段」仅作为展示态，不入库。
- `data_source` 引入 `MANUAL` 以承载模拟立项（spNo 以 MN 开头），与企微同步的真实立项并存，编号规则见 [[rules/manual-project-spno]]。
- `first_settlement_time` 的编辑语义为例外：非空覆盖、null 清空，不遵循其他字符串列的 null 跳过约定；该列变更会触发阶段联动（见 [[rules/first-settlement-to-operation-phase]]）。
- 本期仅放开 `custom_field_statistics_one` 作为编辑独占列，说明自定义字段能力处于逐列开放阶段。

```ground:fields
table: wechat_project_approval_apply
fields:
  - name: sp_type
    meaning: "审批类型；统计页固定过滤 金融科技业务"
    evidence: code
  - name: system_delivery
    meaning: "系统交付类型（统计范围：SaaS / Saas+本地化）"
    evidence: code
  - name: act_procinst_status
    meaning: "企微审批流程状态：1=审批中，2=审批通过"
    evidence: code
  - name: project_type
    meaning: "项目类型：MAIN=主项目 / SUB=子项目"
    evidence: code
  - name: project_phase
    meaning: "项目阶段：IMPLEMENTATION=实施阶段 / OPERATION=持续运营 / HANG=挂起；历史值 TERMINATION 归一为 HANG；立项阶段仅作展示态不入库"
    evidence: code
  - name: ka_white_label
    meaning: "KA 是否贴牌：Y=是 / N=否"
    evidence: code
  - name: data_source
    meaning: "数据来源：MANUAL=模拟立项（spNo 以 MN 开头） / WECHAT=真实立项"
    evidence: code
  - name: product_type_arr
    meaning: '产品类型编码 JSON 数组，如 ["1","9"]；配套 product_type 存中文逗号串（冗余展示列）'
    evidence: code
  - name: solution_manager
    meaning: "方案经理姓名（多人以逗号分隔 CSV）；仅在 solution_manager_wxid 联动维护时同步写入"
    evidence: code
  - name: solution_manager_wxid
    meaning: '方案经理企微 userId 冗余列（JSON 数组字符串 ["id1","id2"]），用于按 wxid 精确过滤'
    evidence: code
  - name: old_solution_manager
    meaning: "前方案经理，姓名 CSV；变更方案经理时由 mergeOldSolutionManager 前置合并旧值"
    evidence: code
  - name: "statics_op_time / statics_op_user"
    meaning: "统计侧最新操作时间/操作人（列表展示用 updateTime/updateUser 取自该两列覆盖）"
    evidence: code
  - name: first_settlement_time
    meaning: "首笔落地时间；编辑语义例外——非空覆盖/null 清空（不遵循其他字符串列的 null 跳过约定）"
    evidence: code
  - name: custom_field_statistics_one
    meaning: "自定义字段一；本期唯一放开的编辑独占列"
    evidence: code
```