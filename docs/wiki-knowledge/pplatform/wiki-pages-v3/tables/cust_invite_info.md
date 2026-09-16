---
type: table
title: 客户邀请
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
contract_version: "0.3"
belong: tables
scenes: [company_contact]
---

# 客户邀请

邀请进度 `progress` 绑定 [[cust_build_status]]，回调按企业名称+租户与企业建档状态同步。没有指向企业主键的等值 JOIN。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_contact]]

`id`, `enable`, `create_time`, `update_time`, `channel_code`, `contact_name`, `contact_phone`, `name`, `progress`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `email`, `invite_cust_id`, `invite_from`, `invite_time`, `organization_id`, `remark`

```ground:table
table: cust_invite_info
database: lowcode_pplatform
desc: 客户邀请信息
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [company_contact]
  - name: code
    type: string
    phys: varchar(64)
    desc: "编码"
    group: always
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    roles: [query]
    group: always
    scenes: [company_contact]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [company_contact]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [company_contact]
  - name: create_by
    type: string
    phys: varchar(100)
    desc: "创建人id"
    group: always
  - name: create_user
    type: string
    phys: varchar(100)
    desc: "创建人名称"
    group: always
  - name: update_by
    type: string
    phys: varchar(100)
    desc: "更新人id"
    group: always
  - name: update_user
    type: string
    phys: varchar(100)
    desc: "更新人名称"
    group: always
  - name: channel_code
    type: string
    phys: varchar(64)
    desc: "渠道编码"
    scenes: [company_contact]
  - name: contact_name
    type: string
    phys: varchar(128)
    desc: "联系人姓名"
    scenes: [company_contact]
  - name: contact_phone
    type: string
    phys: varchar(20)
    desc: "联系人手机"
    scenes: [company_contact]
  - name: name
    type: string
    phys: varchar(64)
    desc: "被邀请企业名称"
    scenes: [company_contact]
  - name: progress
    type: string
    phys: varchar(64)
    desc: "进度"
    dict: cust_build_status
    topk: "AWAIT_CUST_CONFIRM|BUILD_FAIL|BUILD_SUCCESS|CUST_BUILDING|CUST_CHANGE|CUST_CONFIRM_AWAIT|INIT"
    labels: "AWAIT_CUST_CONFIRM:待客户确认|BUILD_FAIL:认证失败|BUILD_SUCCESS:认证成功|CUST_BUILDING:审核中|CUST_CHANGE:变更|CUST_CONFIRM_AWAIT:待客户认证|INIT:初始化"
    roles: [query]
    scenes: [company_contact]
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: "审批结束时间"
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: "流程实例ID"
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: "流程申请编号"
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: "当前审批状态"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "base"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "ISOLATE_TAG_hscc|LN1|LN2|beehive-scf.qhhrly.cn|jiuersanzuhu|ning"
  - name: email
    type: string
    phys: varchar(128)
    desc: "邮箱"
  - name: invite_cust_id
    type: number
    phys: bigint(22)
    desc: "邀请客户id"
  - name: invite_from
    type: string
    phys: varchar(64)
    desc: "邀请主体"
  - name: invite_time
    type: temporal
    phys: datetime
    desc: "邀请时间"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
```
