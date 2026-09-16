---
type: table
title: 渠道接入密钥
page_key: cust_access_secret
domain: 准入接入与接入密钥
status: draft
anchors: [cust_access_secret]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [channel_access]
---

# 渠道接入密钥

按 `channel` + `enable='Y'` 校验 OpenAPI / 准入。不指向企业主键。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[channel_access]]

`id`, `enable`, `create_time`, `update_time`, `channel`, `encry_type`, `name`

### 未分窗

仍留表页，待代码证据划入场景：`status_query_license_enabled`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `key_num`, `organization_id`, `password`, `pri_key`, `pub_key`, `rel_lls_secret_id`, `remark`

```ground:table
table: cust_access_secret
database: lowcode_pplatform
desc: 客户接入秘钥信息
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [channel_access]
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
    topk: "N|Y"
    labels: "N:否|Y:是"
    roles: [query]
    group: always
    scenes: [channel_access]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [channel_access]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [channel_access]
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
  - name: channel
    type: string
    phys: varchar(64)
    desc: "渠道"
    topk: "ZTSJ|alipayAnt|alipayAnt-test|app_bosc_shtl|app_jkny|bgy|dahua|dahua-test|eascs|hbjg|lls|longteng|meituan|sny|sny_test|tianma|trinapower|trinasolar|yhkj"
    roles: [query]
    scenes: [channel_access]
  - name: encry_type
    type: string
    phys: varchar(64)
    desc: "加密类型"
    topk: "rsa"
    scenes: [channel_access]
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
    scenes: [channel_access]
  - name: status_query_license_enabled
    type: string
    phys: varchar(4)
    desc: "建档状态查询是否返回营业执照并同步SFTP：Y-是 N-否"
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
    topk: "ISOLATE_TAG_YINHEKEJI|ISOLATE_TAG_pagoda|ISOLATE_TAG_trinasolar|ISOLATE_TAG_zjsj|ZTSJ|beehive-scf.qhhrly.cn|eascs.beehive-scf.qhhrly.cn|jkny|minmetals|sny|tianma.beehive-scf.qhhrly.cn|xylxchf"
  - name: key_num
    type: number
    phys: int(11)
    desc: "密钥对"
    topk: "2"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: password
    type: string
    phys: varchar(64)
    desc: "密码"
  - name: pri_key
    type: string
    phys: varchar(256)
    desc: "私钥"
  - name: pub_key
    type: string
    phys: varchar(256)
    desc: "公钥"
  - name: rel_lls_secret_id
    type: number
    phys: bigint(22)
    desc: "关联平台密钥记录id"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
```
