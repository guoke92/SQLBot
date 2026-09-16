---
type: table
title: 客户认证配置
page_key: cust_setting_config
domain: 企业银行账户/集团/SFTP
status: draft
anchors: [cust_setting_config]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [bank_account, company_build]
---

# 客户认证配置

租户级认证开关，运行时常取第一行。打款次数上限、是否打款验证、人脸、企业认证审核都在这里。库内开关值为 `yes`/`no`（不是 Y/N）。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[bank_account]]

`id`, `enable`, `create_time`, `update_time`, `payment_maximum_number`, `payment_verification`

### [[company_build]]

`id`, `enable`, `create_time`, `update_time`, `face_recognition`, `need_auth_verify`, `payment_maximum_number`, `payment_verification`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `authorization_change`, `authorization_offline`, `authorization_online`, `cfca_agreement`, `cust_id`, `db_tenant_code`, `invitation_code_period`, `invitation_code_period_unit`, `key_word`, `name`, `need_verify_no_key`, `no_key_word`, `organization_id`, `privacy_policy_agreement`, `remark`, `sending_interval`, `sending_interval_unti`, `user_agreement`

```ground:table
table: cust_setting_config
database: lowcode_pplatform
desc: 客户认证配置
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [bank_account, company_build]
  - name: code
    type: string
    phys: varchar(64)
    desc: "编码"
    topk: "9999999999"
    group: always
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    group: always
    scenes: [bank_account, company_build]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [bank_account, company_build]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [bank_account, company_build]
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
  - name: face_recognition
    type: string
    phys: varchar(64)
    desc: "人脸识别"
    topk: "no"
    scenes: [company_build]
  - name: need_auth_verify
    type: string
    phys: varchar(64)
    desc: "企业认证审核"
    topk: "yes"
    scenes: [company_build]
  - name: payment_maximum_number
    type: number
    phys: int(10)
    desc: "最多申请打款次数"
    roles: [query]
    scenes: [bank_account, company_build]
  - name: payment_verification
    type: string
    phys: varchar(64)
    desc: "打款验证"
    topk: "yes"
    scenes: [bank_account, company_build]
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
  - name: authorization_change
    type: string
    phys: varchar(512)
    desc: "数字证书服务协议"
  - name: authorization_offline
    type: string
    phys: varchar(512)
    desc: "授权确认书-线下签署"
    topk: "CT-202404081721209495040"
  - name: authorization_online
    type: string
    phys: varchar(512)
    desc: "授权确认书-线上签署"
  - name: cfca_agreement
    type: string
    phys: varchar(512)
    desc: "数字证书服务协议"
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: "企业id"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "beehive-scf.qhhrly.cn"
  - name: invitation_code_period
    type: number
    phys: int(10)
    desc: "邀请码有效期"
    topk: "1"
    labels: "1:是"
  - name: invitation_code_period_unit
    type: string
    phys: varchar(64)
    desc: "邀请码有效期单位"
  - name: key_word
    type: string
    phys: varchar(1024)
    desc: "企业关键信息"
  - name: name
    type: string
    phys: varchar(128)
    desc: "配置名称"
  - name: need_verify_no_key
    type: string
    phys: varchar(64)
    desc: "企业非关键信息变更审核"
    topk: "yes"
  - name: no_key_word
    type: string
    phys: varchar(1024)
    desc: "企业非关键信息配置"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: privacy_policy_agreement
    type: string
    phys: varchar(512)
    desc: "隐私政策"
    topk: "CT-202404031807156758507"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: sending_interval
    type: number
    phys: int(10)
    desc: "邀请码重复发送时间间隔"
    topk: "1"
    labels: "1:是"
  - name: sending_interval_unti
    type: string
    phys: varchar(64)
    desc: "邀请码重复发送时间间隔单位"
  - name: user_agreement
    type: string
    phys: varchar(512)
    desc: "用户协议"
    topk: "CT-202404031806394575219"
```
