---
type: table
title: cust_oper_change_record（运营人员变更记录）
page_key: cust_oper_change_record
domain: 企业变更与运营变更
status: draft
aliases: [运营变更流水, 操作运营变更记录]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_oper_change_record
  - code_path:OperChangeRecordApplication.java:queryByPersonId
  - code_path:OperChangeRecordApplication.java:CHANGE_TYPE_DESC
contract_version: "0.1"
---


`cust_oper_change_record` 记录企业联系人（经办人）所绑定运营人员的前后变更流水，是「谁把哪个联系人从哪个运营人员改到了哪个运营人员」的审计轨迹。它与 [[tables.cust_change_record]] 不是一回事，术语边界见 [[concepts.oper-change-record]]；记录按 `person_id`（企业联系人）组织，见 [[concepts.operator]]。变更类型的分类口径见 [[processes.oper-change-type]]，查询口径见 [[rules.oper-change-record-query]]。

## 需求背景

运营人员的变更来源多样：人工手动调整、批量分配、资产审核同步、企业变更回调触发的自动调整。因此本表以 `change_type` 区分来源、以 `change_reason` 保存可读原因、以 `source_system` 标注来源系统、以 `asset_id` 关联资产审核场景，从而支撑联系人详情页的变更历史展示。

## 版本演进

v0.1：首次登记，字段语义来自库表取值分布与 `OperChangeRecordApplication` 的查询与字典映射代码。

```ground:table
table: cust_oper_change_record
database: lowcode_pplatform
desc: 客户操作运营变更记录
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
  - name: after_operator_id
    type: string
    desc: 变更后运营人员ID
  - name: after_operator_name
    type: string
    desc: 变更后运营人员姓名
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: asset_id
    type: string
    desc: 资产id
  - name: asset_no
    type: string
    desc: 资产编号
  - name: before_operator_id
    type: string
    desc: 变更前运营人员ID
  - name: before_operator_name
    type: string
    desc: 变更前运营人员姓名
  - name: change_reason
    type: string
    desc: 变更原因
  - name: change_type
    type: string
    desc: 变更类型
  - name: code
    type: string
    desc: 编码
  - name: company_code
    type: string
    desc: 企业编号
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
  - name: person_id
    type: number
    desc: 企业联系人id
  - name: person_name
    type: string
    desc: 联系人姓名
  - name: remark
    type: string
    desc: remark
  - name: source_system
    type: string
    desc: 来源系统
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```