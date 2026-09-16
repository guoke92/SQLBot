---
type: table
title: 渠道 SFTP
page_key: cust_sftp
domain: 企业银行账户/集团/SFTP
status: draft
anchors: [cust_sftp]
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

# 渠道 SFTP

按 `channel` + `enable='Y'` 取文件通道。无企业外键。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[channel_access]]

`id`, `enable`, `create_time`, `update_time`, `channel`, `host`, `name`, `port`, `user_name`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `organization_id`, `password`, `private_key`, `private_key_pwd`, `remark`

```ground:table
table: cust_sftp
database: lowcode_pplatform
desc: 客戶sftp信息
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
    topk: "Y"
    labels: "Y:是"
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
    topk: "ZTSJ|alipayAnt|alipayAnt-test|app_bosc_shtl|app_jkny|bgy|dahua|dahua-test|eascs|hbjg|longteng|meituan|sny|sny_test|tianma|trinasolar"
    roles: [query]
    scenes: [channel_access]
  - name: host
    type: string
    phys: varchar(64)
    desc: "服务器地址IP地址"
    topk: "qa.sftp.lls.com|uat.sftp.lls.com"
    scenes: [channel_access]
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
    scenes: [channel_access]
  - name: port
    type: number
    phys: int(10)
    desc: "端口"
    scenes: [channel_access]
  - name: user_name
    type: string
    phys: varchar(64)
    desc: "登录用户名"
    topk: "app_JingKeNengY926_20240614|app_LongTengYC_609152804|app_alipayAnt_202606301619|app_bgy_20250306|app_bosc_shtl|app_cclocal_601636163|app_dahua2026041601|app_eascs_2022070823|app_ofhbjg_20260409|app_sny_202607235624|app_trinasolar_2023051522|app_ztsj_2026033169|meituan"
    scenes: [channel_access]
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
    topk: "ISOLATE_TAG_pagoda|ISOLATE_TAG_trinasolar|ISOLATE_TAG_zjsj|ZTSJ|beehive-scf.qhhrly.cn|eascs.beehive-scf.qhhrly.cn|jkny|minmetals|sny|tianma.beehive-scf.qhhrly.cn|xylxchf"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: password
    type: string
    phys: varchar(64)
    desc: "登录密码"
  - name: private_key
    type: string
    phys: varchar(64)
    desc: "私钥"
  - name: private_key_pwd
    type: string
    phys: varchar(256)
    desc: "私钥的密码"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
```
