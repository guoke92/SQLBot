---
type: table
title: 用户企业角色
page_key: cust_user_rel
domain: 经办人/联系人/管理员管理
status: draft
anchors: [cust_user_rel]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












`cust_user_rel` 是联系人到企业/角色的旧关联表。抽样显示它几乎不再承载业务语义：DB 实测仅 1 行，且 `company_type='NULL_VALUE'`、`user_type='admin'`，与 [[cust_person_info]] 使用的 `accountAdmin/accountNormal` 词表不一致。

## 需求背景

主题内「谁属于哪家企业」的判定已迁到 `cust_person_info.ref_cust_company_info` / `cust_company_id` 与 `sys_cust_user_rel`，本表不参与 [[valid_person]]、[[company_admin]] 等核心口径。排查历史数据问题时，不应把本表的 `user_type='admin'` 当作管理员证据。

## 版本演进

判断为历史遗留/近似废弃表；取值词表未随 [[person_type]] 收敛，保留仅用于追溯早期关联关系。

```ground:table
table: cust_user_rel
database: lowcode_pplatform
desc: 用户企业角色
fields:
  - name: company_type
    type: string
    phys: varchar(512)
    desc: 企业类型
    dict: cust_user_rel__company_type
    topk: "NULL_VALUE"
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
  - name: user_type
    type: string
    phys: varchar(512)
    desc: 联系人类型
    dict: cust_user_rel__user_type
    topk: "admin"
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
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
    topk: "a"
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 企业id
  - name: company_name
    type: string
    phys: varchar(200)
    desc: 企业名称
    topk: "深"
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
  - name: type_status
    type: string
    phys: varchar(512)
    desc: 客户角色
    topk: "EFFECT"
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
  - name: user_id
    type: number
    phys: bigint(20)
    desc: 用户id
```

## 关联表

- [[cust_company_info]]：cust_user_rel.company_id → cust_company_info.id（write-flow:SubmitCustInfoEnhanceService.java，confirmed）
- [[cust_person_info]]：cust_user_rel.user_type → cust_person_info.user_type（copy:SubmitCustInfoEnhanceService.java，suggested）
