---
type: table
title: 客户邀请信息
page_key: cust_invite_info
domain: 经办人/联系人/管理员管理
status: draft
anchors: [cust_invite_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---















# 客户邀请信息

（基线页：26 字段，行数估计 210。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_invite_info
database: lowcode_pplatform
desc: 客户邀请信息
fields:
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
    topk: "base"
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
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "ISOLATE_TAG_hscc|LN1|LN2|beehive-scf.qhhrly.cn|jiuersanzuhu|ning"
  - name: email
    type: string
    phys: varchar(128)
    desc: 邮箱
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
  - name: progress
    type: string
    phys: varchar(64)
    desc: 进度
    topk: "AWAIT_CUST_CONFIRM|BUILD_FAIL|BUILD_SUCCESS|CUST_BUILDING|CUST_CHANGE|CUST_CONFIRM_AWAIT|INIT"
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
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```
