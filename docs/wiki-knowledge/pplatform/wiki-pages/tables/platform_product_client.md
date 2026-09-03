---
type: table
title: 平台产品端口配置
page_key: platform_product_client
domain: 基线
status: draft
anchors: [platform_product_client]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 平台产品端口配置

（基线页：26 字段，行数估计 26。行语义/常用过滤待语义摄取增强。）

```ground:table
table: platform_product_client
database: lowcode_pplatform
desc: 平台产品端口配置
inactive: false
fields:
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
  - name: client_type
    type: string
    phys: varchar(32)
    desc: 客户端类型方式
    topk: ACFLOW|AMS|BEECREDIT|DEALER
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
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: beehive-scf.qhhrly.cn
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
  - name: ext_config
    type: string
    phys: varchar(1024)
    desc: 其他配置信息
  - name: link_type
    type: string
    phys: varchar(16)
    desc: 链接类型(iframe/redirect/forward)
    topk: iframe
  - name: multiple_type
    type: string
    phys: varchar(128)
    desc: 过滤类型
    topk: CORE|CORE_BRANCH|CORE_MANAGER|CORE_SUB
  - name: name
    type: string
    phys: varchar(128)
    desc: 名称
    topk: 保理易融|国内信用证|存货易融|应收易融
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_id
    type: number
    phys: bigint(20)
    desc: 平台产品id
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: status
    type: string
    phys: varchar(512)
    desc: 启用状态
    topk: Y
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
  - name: url
    type: string
    phys: varchar(1024)
    desc: 产品url
    topk: 3fede090446c4c8196a98d0721a6d021
  - name: wx_flag
    type: string
    phys: varchar(512)
    desc: 是否小程序
    topk: N|Y
```
