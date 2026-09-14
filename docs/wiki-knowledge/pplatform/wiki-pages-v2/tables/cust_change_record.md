---
type: table
title: 客户变更记录
page_key: cust_change_record
domain: 企业变更与运营变更
status: draft
anchors: [cust_change_record]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---











cust_change_record 记录运营中台客户与产融企业之间的变更信息；变更过程中的影像不在事件回调里实时同步，而由规则 [[build_media_sync_condition]] 约束在审核通过后统一拉取。

## 需求背景
本期语义分析未提供需求文档主张，字段语义来自代码证据。

## 版本演进
v0 初版：字段语义来自本期证据；无 action=uncovered 的文档主张。

```ground:table
table: cust_change_record
database: lowcode_pplatform
desc: 客户变更记录
fields:
  - name: admin_auth
    type: string
    phys: varchar(512)
    desc: 企业管理授权
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: alter_mode
    type: string
    phys: varchar(10)
    desc: 变更方式
    dict: alter_mode
    topk: "1|2"
  - name: cust_company_type
    type: string
    phys: varchar(60)
    desc: 客户企业类型
    dict: cust_company_type
    topk: "CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER|FINANCE|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER|[\"CORE\"]"
  - name: cust_type
    type: string
    phys: varchar(512)
    desc: 客户类型
    dict: cust_type
    topk: "1|2|3|4"
  - name: electronic_auth_sign_status
    type: string
    phys: varchar(16)
    desc: 电子授权书签署状态，DB 实测 PENDING/SIGNED
    dict: cust_change_record__electronic_auth_sign_status
    topk: "PENDING|SIGNED"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: legal_auth
    type: string
    phys: varchar(512)
    desc: 法人代表授权
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: msg_send
    type: string
    phys: varchar(10)
    desc: 消息发送
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: need_cust_confirm
    type: string
    phys: varchar(512)
    desc: 是否需要客户确认
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: need_resign_auth
    type: string
    phys: varchar(1)
    desc: 是否需要重签授权书：Y-是，N-否。直推在识别变更项时写入，后续只读
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
  - name: alter_data
    type: string
    phys: varchar(1024)
    desc: 变更数据
  - name: alter_type
    type: string
    phys: varchar(526)
    desc: 变更类型
  - name: alter_type_id
    type: string
    phys: varchar(1024)
    desc: 变更项记录id
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "JHYL|JYYL|QA2tiepai2|base|common"
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 客户记录id
  - name: cust_name
    type: string
    phys: varchar(128)
    desc: 客户名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: oper_app_no
    type: string
    phys: varchar(128)
    desc: 运营中台流程编号
  - name: oper_channel
    type: string
    phys: varchar(50)
    desc: 运营中台变更渠道
    topk: "DIRECT_INIT|operation-pplatform-common-new|operation-pplatform-not-edit-new"
  - name: oper_cust_id
    type: number
    phys: bigint(22)
    desc: 运营中台客户id
  - name: oper_cust_info
    type: string
    phys: text
    desc: 运营中台客户信息
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: pp_cust_info
    type: string
    phys: text
    desc: 产融客户信息
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: status
    type: string
    phys: varchar(512)
    desc: 变更状态
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

## 关联表

- [[cust_change_cfg]]：cust_change_record.alter_type_id → cust_change_cfg.id（read-flow:CustSyncEventProcessor.java，confirmed）
- [[cust_company_info]]：cust_change_record.cust_id → cust_company_info.id（java-eq:OperCustFacade.java，suggested）
- [[cust_person_info]]：cust_change_record.code → cust_person_info.ref_cust_company_info（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_project_rel]]：cust_change_record.code → cust_project_rel.ref_cust_project_rel_cust_company_info（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_role_info]]：cust_change_record.code → cust_role_info.ref_cust_company_info（java-eq:CustSyncEventProcessor.java，suggested）
