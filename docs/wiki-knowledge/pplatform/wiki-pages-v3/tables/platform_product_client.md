---
type: table
title: 平台产品客户端
page_key: platform_product_client
domain: 平台产品配置
status: draft
anchors: [platform_product_client]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [platform_product]
---

# 平台产品客户端

产品在各客户端的入口配置，用于 URL 路由。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[platform_product]]

`id`, `enable`, `create_time`, `update_time`, `client_type`, `link_type`, `platform_product_id`, `status`

### 未分窗

仍留表页，待代码证据划入场景：`wx_flag`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `ext_config`, `multiple_type`, `name`, `organization_id`, `remark`, `url`

```ground:table
table: platform_product_client
database: lowcode_pplatform
desc: 平台产品端口配置
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [platform_product]
  - name: code
    type: string
    phys: varchar(64)
    desc: "编码"
    group: always
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    group: always
    scenes: [platform_product]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [platform_product]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [platform_product]
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
    phys: varchar(32)
    desc: "客户端类型"
    topk: "ACFLOW|AMS|BEECREDIT|DEALER|ORDER|RVSFACTOR_PC"
    roles: [query]
    scenes: [platform_product]
  - name: link_type
    type: string
    phys: varchar(16)
    desc: "链接类型"
    topk: "iframe"
    scenes: [platform_product]
  - name: platform_product_id
    type: number
    phys: bigint(20)
    desc: "平台产品id"
    roles: [query]
    scenes: [platform_product]
  - name: status
    type: string
    phys: varchar(512)
    desc: "状态"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    scenes: [platform_product]
  - name: wx_flag
    type: string
    phys: varchar(512)
    desc: "是否小程序"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "beehive-scf.qhhrly.cn"
  - name: ext_config
    type: string
    phys: varchar(1024)
    desc: "其他配置信息"
  - name: multiple_type
    type: string
    phys: varchar(128)
    desc: "过滤类型"
    topk: "CORE|CORE_BRANCH|CORE_MANAGER|CORE_SUB|DEALER|FINANCE|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER|default"
  - name: name
    type: string
    phys: varchar(128)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: url
    type: string
    phys: varchar(1024)
    desc: "产品url"
```
