---
type: table
title: cust_change_record（客户变更记录表）
page_key: table.cust_change_record
domain: 平台内部服务对接
status: draft
aliases:
  - cust_change_record
  - 客户变更记录表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_change_record]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


客户信息变更流程的记录表，保存变更前后内容、操作渠道与状态，并在变更态下提供运营中台企业 id。

## 需求背景

当企业处于变更中（cust_status=CHANGE）时，换取 token 所需的运营中台企业 id 取自本表记录中的 custEnterpriseId 而非 [[tables/cust_role_info]]（见 [[rules/change_status_token_source]]）。有效记录的取用口径见 [[rules/cust_change_record_latest_effective]]。

## 版本演进

v0：首次成页。

```ground:table
table: cust_change_record
database: lowcode_pplatform
desc: 客户变更记录
fields:
  - name: alter_mode
    type: string
    desc: 变更方式
    dict: alter_mode
  - name: cust_type
    type: string
    desc: 客户类型
    dict: cust_type
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
  - name: admin_auth
    type: string
    desc: 企业管理授权
  - name: alter_data
    type: string
    desc: 变更数据
  - name: alter_type
    type: string
    desc: 变更类型
  - name: alter_type_id
    type: string
    desc: 变更项记录id
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: code
    type: string
    desc: 编码
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: cust_company_type
    type: string
    desc: 客户企业类型
  - name: cust_id
    type: number
    desc: 客户记录id
  - name: cust_name
    type: string
    desc: 客户名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: electronic_auth_sign_status
    type: string
    desc: 电子授权书签署状态，DB 实测 PENDING/SIGNED
  - name: enable
    type: string
    desc: enable
  - name: legal_auth
    type: string
    desc: 法人代表授权
  - name: msg_send
    type: string
    desc: 消息发送
  - name: name
    type: string
    desc: 名称
  - name: need_cust_confirm
    type: string
    desc: 是否需要客户确认
  - name: need_resign_auth
    type: string
    desc: 是否需要重签授权书：Y-是，N-否。直推在识别变更项时写入，后续只读
  - name: oper_app_no
    type: string
    desc: 运营中台流程编号
  - name: oper_channel
    type: string
    desc: 运营中台变更渠道
  - name: oper_cust_id
    type: number
    desc: 运营中台客户id
  - name: oper_cust_info
    type: string
    desc: 运营中台客户信息
  - name: organization_id
    type: string
    desc: 机构编号
  - name: pp_cust_info
    type: string
    desc: 产融客户信息
  - name: remark
    type: string
    desc: remark
  - name: status
    type: string
    desc: 变更状态
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
## 关联表

- [[cust_change_cfg]]：cust_change_record.alter_type_id → cust_change_cfg.id（read-flow:CustSyncEventProcessor.java，confirmed）
- [[cust_company_info]]：cust_change_record.cust_id → cust_company_info.id（java-eq:OperCustFacade.java，suggested）
- [[cust_person_info]]：cust_change_record.code → cust_person_info.ref_cust_company_info（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_project_rel]]：cust_change_record.code → cust_project_rel.ref_cust_project_rel_cust_company_info（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_role_info]]：cust_change_record.code → cust_role_info.ref_cust_company_info（java-eq:CustSyncEventProcessor.java，suggested）
