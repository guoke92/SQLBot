---
type: table
title: 客户邀请信息
page_key: cust_invite_info
belong: tables
domain: 基线
status: draft
anchors: [cust_invite_info]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户邀请信息

（基线页：26 字段，行数估计 203。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_invite_info
database: lowcode_pplatform
desc: 客户邀请信息
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: progress
    type: string
    phys: varchar(64)
    desc: 进度
    dict: cust_build_status
    topk: AWAIT_CUST_CONFIRM|BUILD_FAIL|BUILD_SUCCESS|CUST_BUILDING
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
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: base
  - name: channel_code
    type: string
    phys: varchar(64)
    desc: 渠道码
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: contact_name
    type: string
    phys: varchar(128)
    desc: 联系人
  - name: contact_phone
    type: string
    phys: varchar(20)
    desc: 联系人手机号码
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
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_hscc|LN1|LN2|beehive-scf.qhhrly.cn
  - name: email
    type: string
    phys: varchar(128)
    desc: 邮箱
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: invite_cust_id
    type: number
    phys: bigint(22)
    desc: 邀请客户id
  - name: invite_from
    type: string
    phys: varchar(64)
    desc: 邀请主体
  - name: invite_time
    type: temporal
    phys: datetime
    desc: 邀请时间
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
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
