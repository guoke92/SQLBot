---
type: table
title: 企业变更项配置
page_key: cust_change_cfg
domain: 企业变更与运营变更
status: draft
anchors: [cust_change_cfg]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:CustChangeCfgDO.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [company_change]
---

# 企业变更项配置

场景 [[company_change]] 的配置表。按 `identify_style`、`client_type`、`head_company`、`cust_type` 匹配企业可用变更项。问变更单不要 FROM 本表。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_change]]

`id`, `enable`, `create_time`, `update_time`, `client_type`, `head_company`, `identify_style`, `item_code`, `open_process`, `plat_item`

### 未分窗

仍留表页，待代码证据划入场景：`cust_type`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `data_desc`, `db_tenant_code`, `name`, `oper_item`, `organization_id`, `remark`

```ground:table
table: cust_change_cfg
database: lowcode_pplatform
desc: 客户变更配置
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
  - name: client_type
    type: string
    phys: varchar(20)
    desc: "端类型"
    topk: "ACCOUNT_PRODUCT|AGW"
    scenes: [company_change]
  - name: cust_type
    type: string
    phys: varchar(512)
    desc: "客户类型"
    dict: cust_type
    topk: "1|2|3"
    labels: "1:个人客户|2:企业客户|3:运营方企业客户"
  - name: head_company
    type: string
    phys: varchar(10)
    desc: "是否总公司维度配置"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [company_change]
  - name: identify_style
    type: string
    phys: varchar(512)
    desc: "认证方式"
    dict: identify_style
    topk: "INVITE|INVITE_AGW|SELF|SIMPLE"
    labels: "INVITE:邀请认证-客户录入|INVITE_AGW:邀请认证-内管录入|SELF:自主认证|SIMPLE:简易认证"
    scenes: [company_change]
  - name: item_code
    type: string
    phys: varchar(128)
    desc: "变更项编码"
    topk: "UN0001|UN0002|UN0003|UN0004|UN0005|UN0006|UN0007|UN0008|UN0009|UN0010|UN0011|UN0012|UN0013|UN0014|UN0015|UN0016"
    roles: [query]
    scenes: [company_change]
  - name: open_process
    type: string
    phys: varchar(10)
    desc: "该变更项是否开启流程"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [company_change]
  - name: plat_item
    type: string
    phys: varchar(128)
    desc: "平台侧变更项名称"
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
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
  - name: data_desc
    type: string
    phys: varchar(128)
    desc: "变更需要材料说明"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "beehive-scf.lianyirong.com.cn|beehive-scf.qhhrly.cn"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: oper_item
    type: string
    phys: varchar(128)
    desc: "运营中台变更项"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
```
