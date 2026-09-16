---
type: table
title: 租户项目
page_key: tenant_project
domain: 租户产品/互通产品/租户项目
status: draft
anchors: [tenant_project]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [tenant_project, company_project, project_online_approval]
---

# 租户项目

可运行项目实例。`product_id` → [[tenant_product]].id；`project_status` 落库 `'0'`/`'1'`/`'2'`。`wechat_audit_no` 对齐立项 `sp_no`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_project]]

`id`, `enable`, `create_time`, `update_time`, `channel_code`, `platform_product_code`, `project_status`

### [[project_online_approval]]

`id`, `enable`, `create_time`, `update_time`, `project_approval_id`, `project_status`, `wechat_audit_no`

### [[tenant_project]]

`id`, `enable`, `create_time`, `update_time`, `channel_code`, `platform_product_code`, `product_id`, `project_approval_id`, `project_status`, `source`, `wechat_audit_no`

### 未分窗

仍留表页，待代码证据划入场景：`cover_operator`, `cust_oper_show`, `is_add`, `is_prd`, `share_flag`, `test_data`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `business_group`, `business_manager`, `bussiness_project_relation`, `config_json`, `config_model`, `custom_field_one`, `custom_field_three`, `custom_field_two`, `db_tenant_code`, `first_settlement_time`, `invite_customer_service_words`, `logo_path`, `name`, `op_contact_a`, `op_contact_a_group`, `op_contact_b`, `op_update_time`, `op_update_user`, `operater_card_type`, `operator_email`, `operator_id`, `operator_name`, `organization_id`, `project_agreement`, `project_code`, `project_config_version`, `project_create_time`, `project_effective_time`, `project_relation`, `project_tag`, `ref_tenant_project_platform_product`, `ref_tenant_project_product_code`, `ref_tenant_project_tenant_code`, `refer_tenant_project_id`, `remark`, `risk_control_contact_a`, `risk_control_contact_a_group`, `risk_control_contact_b`, `send_email`, `solution_manager`, `source_id`, `tenant_flg_en`, `tenant_id`, `text`, `top_flag`, `verification_contact`, `verification_contact_group`, `wechat_audit_pass_time`

```ground:table
table: tenant_project
database: lowcode_pplatform
desc: 租户项目配置
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "主键"
    roles: [query]
    group: always
    scenes: [company_project, project_online_approval, tenant_project]
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
    scenes: [company_project, project_online_approval, tenant_project]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    roles: [result]
    group: always
    scenes: [company_project, project_online_approval, tenant_project]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [company_project, project_online_approval, tenant_project]
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
    phys: varchar(128)
    desc: "渠道编码"
    roles: [query]
    scenes: [company_project, tenant_project]
  - name: cover_operator
    type: string
    phys: varchar(2)
    desc: "是否覆盖运营"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: cust_oper_show
    type: string
    phys: varchar(10)
    desc: "建档运营名片展示"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_add
    type: string
    phys: varchar(64)
    desc: "是否新增，Y：是，N：否，默认为N"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_prd
    type: string
    phys: varchar(4)
    desc: "是否生产数据"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: platform_product_code
    type: string
    phys: varchar(32)
    desc: "平台产品编码"
    topk: "ACFLOW|BEECREDIT|DRAFT|DRAFTQA|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
    roles: [query]
    scenes: [company_project, tenant_project]
  - name: product_id
    type: number
    phys: bigint(20)
    desc: "租户产品id"
    roles: [query]
    scenes: [tenant_project]
  - name: project_approval_id
    type: number
    phys: bigint(20)
    desc: "上线审批id"
    scenes: [project_online_approval, tenant_project]
  - name: project_status
    type: string
    phys: varchar(512)
    desc: "项目状态"
    dict: project_status
    topk: "0|1|2"
    labels: "0:待生效|1:已生效|2:已失效"
    roles: [query]
    scenes: [company_project, project_online_approval, tenant_project]
  - name: share_flag
    type: string
    phys: varchar(4)
    desc: "共享租户"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: source
    type: string
    phys: varchar(32)
    desc: "来源"
    topk: "ACFLOW|ORDER|RVSFACTOR_PC|STORAGE|pplatform"
    scenes: [tenant_project]
  - name: test_data
    type: string
    phys: varchar(4)
    desc: "是否测试数据"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: wechat_audit_no
    type: string
    phys: varchar(40)
    desc: "企微审批号"
    scenes: [project_online_approval, tenant_project]
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
    topk: "GREENTOWNAT|JHYL|JYYL|Liugongscf|NAURA|QA2tiepai2|YINHEKEJI|base|boscxsbl|boscxyc|chenguang|hylg|reversefactoring|sdhsg|shanghaiyinhang"
  - name: business_group
    type: string
    phys: varchar(100)
    desc: "关联业务部门"
    topk: "11|部门a"
  - name: business_manager
    type: string
    phys: varchar(64)
    desc: "业务经理"
  - name: bussiness_project_relation
    type: string
    phys: varchar(100)
    desc: "运营项目归属"
  - name: config_json
    type: string
    phys: text
    desc: "配置详情"
  - name: config_model
    type: string
    phys: varchar(8)
    desc: "项目配置模式(XYC)"
    topk: "admin|normal"
  - name: custom_field_one
    type: string
    phys: varchar(500)
    desc: "自定义字段一"
  - name: custom_field_three
    type: string
    phys: varchar(500)
    desc: "自定义字段三"
  - name: custom_field_two
    type: string
    phys: varchar(500)
    desc: "自定义字段二"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: first_settlement_time
    type: temporal
    phys: datetime
    desc: "首笔落地时间"
  - name: invite_customer_service_words
    type: string
    phys: varchar(500)
    desc: "客服话术"
  - name: logo_path
    type: string
    phys: varchar(526)
    desc: "logo路径"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
    roles: [query, result]
  - name: op_contact_a
    type: string
    phys: varchar(64)
    desc: "运营对接人A"
    topk: "141|267|271|280|305|333|344|360|383|411|412|415|420|430|454|463|466|93|97"
    roles: [query, result]
  - name: op_contact_a_group
    type: string
    phys: varchar(100)
    desc: "运营组别"
    roles: [query, result]
  - name: op_contact_b
    type: string
    phys: varchar(400)
    desc: "运营对接人B"
    roles: [result]
  - name: op_update_time
    type: temporal
    phys: datetime
    desc: "运营信息更新时间"
    roles: [result]
  - name: op_update_user
    type: string
    phys: varchar(64)
    desc: "运营信息更新人"
    roles: [result]
  - name: operater_card_type
    type: string
    phys: varchar(12)
    desc: "运营名片类型"
    topk: "WX|WX_WORK"
  - name: operator_email
    type: string
    phys: varchar(100)
    desc: "运营对接人邮箱"
  - name: operator_id
    type: string
    phys: varchar(100)
    desc: "运营人员id"
  - name: operator_name
    type: string
    phys: varchar(100)
    desc: "运营对接人名称"
    topk: "112|12321321|4353|yinxiguang|乔|刘宁|唐唐|对先生A|王莲|计娜|阮班良|顾振清|香莲"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: project_agreement
    type: string
    phys: varchar(512)
    desc: "项目协议"
  - name: project_code
    type: string
    phys: varchar(128)
    desc: "项目编码"
  - name: project_config_version
    type: string
    phys: varchar(64)
    desc: "项目配置版本"
    topk: "config|configPro"
  - name: project_create_time
    type: temporal
    phys: datetime
    desc: "项目创建时间"
  - name: project_effective_time
    type: temporal
    phys: datetime
    desc: "项目生效时间"
  - name: project_relation
    type: string
    phys: varchar(100)
    desc: "项目归属"
    topk: "111|1111"
  - name: project_tag
    type: string
    phys: varchar(150)
    desc: "项目标签"
    topk: "PRD|TEST"
  - name: ref_tenant_project_platform_product
    type: string
    phys: varchar(128)
    desc: "平台产品-项目关联"
  - name: ref_tenant_project_product_code
    type: string
    phys: varchar(128)
    desc: "租户产品-项目"
  - name: ref_tenant_project_tenant_code
    type: string
    phys: varchar(128)
    desc: "租户-项目"
  - name: refer_tenant_project_id
    type: number
    phys: bigint(20)
    desc: "复制的租户项目"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: risk_control_contact_a
    type: string
    phys: varchar(64)
    desc: "风控对接人A"
    topk: "209|210|267|271|333|344|360|363|383|411|415|441|454|97"
    roles: [query, result]
  - name: risk_control_contact_a_group
    type: string
    phys: varchar(64)
    desc: "风控组别"
    roles: [query, result]
  - name: risk_control_contact_b
    type: string
    phys: varchar(64)
    desc: "风控对接人B"
    roles: [result]
  - name: send_email
    type: string
    phys: varchar(100)
    desc: "是否发送邮件"
    topk: "0|1"
    labels: "0:否|1:是"
  - name: solution_manager
    type: string
    phys: varchar(64)
    desc: "方案经理"
  - name: source_id
    type: string
    phys: varchar(32)
    desc: "项目来源id"
  - name: tenant_flg_en
    type: string
    phys: varchar(128)
    desc: "项目标识（英文）"
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: "租户编码"
  - name: text
    type: string
    phys: varchar(1000)
    desc: "备注"
  - name: top_flag
    type: string
    phys: varchar(4)
    desc: "置顶标识"
    topk: "0|1"
    labels: "0:否|1:是"
  - name: verification_contact
    type: string
    phys: varchar(64)
    desc: "查验对接人"
    topk: "333|360|383|404|430|OP001"
    roles: [query, result]
  - name: verification_contact_group
    type: string
    phys: varchar(64)
    desc: "查验组别"
    roles: [query, result]
  - name: wechat_audit_pass_time
    type: temporal
    phys: datetime
    desc: "项目立项审批通过时间"
```

```ground:relation
type: EQUI_JOIN
left: tenant_project.product_id
right: tenant_product.id
cardinality: many_to_one
status: proposed
evidence: code_path:TenantProjectDomainService.java
```
