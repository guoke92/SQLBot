---
type: table
title: 企业变更记录
page_key: cust_change_record
domain: 企业变更与运营变更
status: draft
anchors: [cust_change_record]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:CustChangeRecordDO.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [company_change]
---

# 企业变更记录

场景 [[company_change]] 的**主档**。`cust_id` 是 [[cust_company_info]].id，不是 `code`。`alter_type_id` 是变更项配置主键的逗号列表，不能当单值外键 JOIN。

`status` 与企业准入 [[check_status]] 共用 `CheckStatus` 字典，但是变更单自己的审核列，流转见 [[cust_change_record_status]]。库中还有 `'1'`、`CUSTS003`、`returnCust-日期` 等代码枚举外的值，不能当正式状态过滤。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_change]]

`id`, `enable`, `create_time`, `update_time`, `alter_mode`, `alter_type_id`, `cust_company_type`, `cust_id`, `need_cust_confirm`, `status`

### 未分窗

仍留表页，待代码证据划入场景：`admin_auth`, `cust_type`, `legal_auth`, `msg_send`, `need_resign_auth`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `alter_data`, `alter_type`, `app_tenant_code`, `cust_name`, `db_tenant_code`, `electronic_auth_sign_status`, `name`, `oper_app_no`, `oper_channel`, `oper_cust_id`, `oper_cust_info`, `organization_id`, `pp_cust_info`, `remark`

```ground:table
table: cust_change_record
database: lowcode_pplatform
desc: 客户变更记录
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [company_change]
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
    group: always
    scenes: [company_change]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [company_change]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [company_change]
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
  - name: admin_auth
    type: string
    phys: varchar(512)
    desc: "企业管理授权"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: alter_mode
    type: string
    phys: varchar(10)
    desc: "变更方式"
    dict: alter_mode
    topk: "1|2"
    labels: "1:平台变更|2:企业自行变更"
    scenes: [company_change]
  - name: alter_type_id
    type: string
    phys: varchar(1024)
    desc: "变更项记录id"
    scenes: [company_change]
  - name: cust_company_type
    type: string
    phys: varchar(60)
    desc: "客户企业类型"
    topk: "CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER|FINANCE|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER|["CORE"]"
    scenes: [company_change]
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: "客户记录id"
    scenes: [company_change]
  - name: cust_type
    type: string
    phys: varchar(512)
    desc: "客户类型"
    dict: cust_type
    topk: "1|2|3|4"
    labels: "1:个人客户|2:企业客户|3:运营方企业客户|4:企业客户"
  - name: legal_auth
    type: string
    phys: varchar(512)
    desc: "法人代表授权"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: msg_send
    type: string
    phys: varchar(10)
    desc: "消息发送"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: need_cust_confirm
    type: string
    phys: varchar(512)
    desc: "是否需要客户确认"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [company_change]
  - name: need_resign_auth
    type: string
    phys: varchar(1)
    desc: "是否需要重签授权书：Y-是，N-否。直推在识别变更项时写入，后续只读"
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: status
    type: string
    phys: varchar(512)
    desc: "变更状态"
    scenes: [company_change]
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
  - name: alter_data
    type: string
    phys: varchar(1024)
    desc: "变更数据"
  - name: alter_type
    type: string
    phys: varchar(526)
    desc: "变更类型"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "JHYL|JYYL|QA2tiepai2|base|common"
  - name: cust_name
    type: string
    phys: varchar(128)
    desc: "客户名称"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: electronic_auth_sign_status
    type: string
    phys: varchar(16)
    topk: "PENDING|SIGNED"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: oper_app_no
    type: string
    phys: varchar(128)
    desc: "运营中台流程编号"
  - name: oper_channel
    type: string
    phys: varchar(50)
    desc: "运营中台变更渠道"
    topk: "DIRECT_INIT|operation-pplatform-common-new|operation-pplatform-not-edit-new"
  - name: oper_cust_id
    type: number
    phys: bigint(22)
    desc: "运营中台客户id"
  - name: oper_cust_info
    type: string
    phys: text
    desc: "运营中台客户信息"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: pp_cust_info
    type: string
    phys: text
    desc: "产融客户信息"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
```

```ground:relation
type: EQUI_JOIN
left: cust_change_record.cust_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:CustChangeRecordDO.java
```
