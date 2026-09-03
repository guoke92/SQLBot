---
type: table
title: 客户变更记录
page_key: cust_change_record
domain: 基线
status: draft
anchors: [cust_change_record]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户变更记录

（基线页：37 字段，行数估计 5189。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_change_record
database: lowcode_pplatform
desc: 客户变更记录
inactive: false
fields:
  - name: alter_mode
    type: string
    phys: varchar(10)
    desc: 变更方式
    dict: alter_mode
    topk: 1|2
  - name: cust_type
    type: string
    phys: varchar(512)
    desc: 客户类型
    dict: cust_type
    topk: 1|2|3|4
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
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
  - name: admin_auth
    type: string
    phys: varchar(512)
    desc: 企业管理授权
    topk: N|Y
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
    topk: JHYL|JYYL|QA2tiepai2|base
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
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: cust_company_type
    type: string
    phys: varchar(60)
    desc: 客户企业类型
    topk: CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER
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
  - name: electronic_auth_sign_status
    type: string
    phys: varchar(16)
    topk: PENDING|SIGNED
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: legal_auth
    type: string
    phys: varchar(512)
    desc: 法人代表授权
    topk: N|Y
  - name: msg_send
    type: string
    phys: varchar(10)
    desc: 消息发送
    topk: N|Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: need_cust_confirm
    type: string
    phys: varchar(512)
    desc: 是否需要客户确认
    topk: N|Y
  - name: oper_app_no
    type: string
    phys: varchar(128)
    desc: 运营中台流程编号
  - name: oper_channel
    type: string
    phys: varchar(50)
    desc: 运营中台变更渠道
    topk: operation-pplatform-common-new|operation-pplatform-not-edit-new
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
    topk: 1|CUST_CHECK_BACKTOCUSTOM|CUST_CHECK_CHECKING|CUST_CHECK_PASS
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
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
