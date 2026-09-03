---
type: table
title: 客户接入秘钥信息
page_key: cust_access_secret
domain: 基线
status: draft
anchors: [cust_access_secret]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户接入秘钥信息

（基线页：26 字段，行数估计 19。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_access_secret
database: lowcode_pplatform
desc: 客户接入秘钥信息
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
  - name: channel
    type: string
    phys: varchar(64)
    desc: 应用id
    topk: ZTSJ|alipayAnt|alipayAnt-test|app_bosc_shtl
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
    topk: ISOLATE_TAG_YINHEKEJI|ISOLATE_TAG_pagoda|ISOLATE_TAG_trinasolar|ISOLATE_TAG_zjsj
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
  - name: encry_type
    type: string
    phys: varchar(64)
    desc: 加密类型
    topk: rsa
  - name: key_num
    type: number
    phys: int(11)
    desc: 密钥对
    topk: 2
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    topk: lls平台|中铁四局|天合光能|天马
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: password
    type: string
    phys: varchar(64)
    desc: 密码
  - name: pri_key
    type: string
    phys: varchar(256)
    desc: 私钥
  - name: pub_key
    type: string
    phys: varchar(256)
    desc: 公钥
  - name: rel_lls_secret_id
    type: number
    phys: bigint(22)
    desc: 关联平台密钥记录id
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: status_query_license_enabled
    type: string
    phys: varchar(4)
    desc: 建档状态查询是否返回营业执照并同步SFTP：Y-是 N-否
    topk: N|Y
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
