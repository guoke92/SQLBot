---
type: table
title: 租户项目配置
page_key: tenant_project
domain: 基线
status: draft
anchors: [tenant_project]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 租户项目配置

（基线页：75 字段，行数估计 3231。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_project
database: lowcode_pplatform
desc: 租户项目配置
inactive: false
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
    roles: [query]
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
    roles: [query, result]
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    roles: [query, result]
  - name: op_contact_a
    type: string
    phys: varchar(64)
    desc: 运营对接人A
    topk: 141|267|271|280
    roles: [query, result]
  - name: op_contact_a_group
    type: string
    phys: varchar(100)
    desc: 运营组别
    topk: 1|2|3|ams
    roles: [query, result]
  - name: risk_control_contact_a
    type: string
    phys: varchar(64)
    desc: 风控对接人A
    topk: 209|210|267|271
    roles: [query, result]
  - name: risk_control_contact_a_group
    type: string
    phys: varchar(64)
    desc: 风控组别
    topk: 1|2|ams|zu1
    roles: [query, result]
  - name: verification_contact
    type: string
    phys: varchar(64)
    desc: 查验对接人
    topk: 333|360|383|404
    roles: [query, result]
  - name: verification_contact_group
    type: string
    phys: varchar(64)
    desc: 查验组别
    topk: 1|11|ams|审核组2
    roles: [query, result]
  - name: project_status
    type: string
    phys: varchar(512)
    desc: 项目状态
    dict: project_status
    topk: 0|1|2
  - name: source
    type: string
    phys: varchar(32)
    desc: 项目来源
    dict: tenant_project__source
    topk: ACFLOW|ORDER|RVSFACTOR_PC|STORAGE
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
    topk: GREENTOWNAT|JHYL|JYYL|Liugongscf
  - name: business_group
    type: string
    phys: varchar(100)
    desc: 关联业务部门
    topk: 11|部门a
  - name: business_manager
    type: string
    phys: varchar(64)
    desc: 业务经理
    topk: 1|11|111|5435363
  - name: bussiness_project_relation
    type: string
    phys: varchar(100)
    desc: 运营项目归属
    topk: 111|2|543543543|df
  - name: channel_code
    type: string
    phys: varchar(128)
    desc: 渠道码
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: config_json
    type: string
    phys: text
    desc: 配置详情
  - name: config_model
    type: string
    phys: varchar(8)
    desc: 项目配置模式(XYC)
    topk: admin|normal
  - name: cover_operator
    type: string
    phys: varchar(2)
    desc: 是否覆盖运营
    topk: N|Y
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    roles: [result]
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: cust_oper_show
    type: string
    phys: varchar(10)
    desc: 建档运营名片展示
    topk: N|Y
  - name: custom_field_one
    type: string
    phys: varchar(500)
    desc: 自定义字段一
    topk: 0121-01|1|35435435|你好呀
  - name: custom_field_three
    type: string
    phys: varchar(500)
    desc: 自定义字段三
    topk: 0121-03|11|2|3
  - name: custom_field_two
    type: string
    phys: varchar(500)
    desc: 自定义字段二
    topk: 0121-02|1|11|2
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: first_settlement_time
    type: temporal
    phys: datetime
    desc: 首笔落地时间
    group: project_up_time_group
  - name: invite_customer_service_words
    type: string
    phys: varchar(500)
    desc: 客服话术
  - name: is_add
    type: string
    phys: varchar(64)
    desc: 是否新增，Y：是，N：否，默认为N
    topk: N|Y
  - name: is_prd
    type: string
    phys: varchar(4)
    desc: 是否生产数据
    topk: N|Y
  - name: logo_path
    type: string
    phys: varchar(526)
    desc: logo路径
  - name: op_contact_b
    type: string
    phys: varchar(400)
    desc: 运营对接人B
    roles: [result]
  - name: op_update_time
    type: temporal
    phys: datetime
    desc: 运营信息更新时间
    roles: [result]
  - name: op_update_user
    type: string
    phys: varchar(64)
    desc: 运营信息更新人
    topk: wangxianglian|丁铁|刘倍材|刘婷
    roles: [result]
  - name: operater_card_type
    type: string
    phys: varchar(12)
    desc: 运营名片类型
    topk: WX|WX_WORK
  - name: operator_email
    type: string
    phys: varchar(100)
    desc: 运营对接人邮箱
    topk: 112@11.com|123@qq.com|2131231232@qq.com|5435435@163.com
  - name: operator_id
    type: string
    phys: varchar(100)
    desc: 运营人员id
  - name: operator_name
    type: string
    phys: varchar(100)
    desc: 运营对接人名称
    topk: 112|12321321|4353|yinxiguang
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(32)
    desc: 平台产品编码
    topk: ACFLOW|BEECREDIT|DRAFT|DRAFTQA
    roles: [result]
  - name: product_id
    type: number
    phys: bigint(20)
    desc: 产品编码
  - name: project_agreement
    type: string
    phys: varchar(512)
    desc: 项目协议
  - name: project_approval_id
    type: number
    phys: bigint(20)
    desc: 项目线上审批ID
  - name: project_code
    type: string
    phys: varchar(128)
    desc: 项目编码
  - name: project_config_version
    type: string
    phys: varchar(64)
    desc: 项目配置版本
    topk: config|configPro
  - name: project_create_time
    type: temporal
    phys: datetime
    desc: 项目创建时间
    group: project_create_time_group
  - name: project_effective_time
    type: temporal
    phys: datetime
    desc: 项目生效时间
    group: project_create_time_group, project_effective_time_group
  - name: project_relation
    type: string
    phys: varchar(100)
    desc: 项目归属
    topk: 111|1111
  - name: project_tag
    type: string
    phys: varchar(150)
    desc: 项目标签
    topk: PRD|TEST
  - name: ref_tenant_project_platform_product
    type: string
    phys: varchar(128)
    desc: 平台产品-项目关联
    topk: 007142024a5c425bb3673f753060e534|b8468d68ba0a4762bda0f7b9164e4f6a
  - name: ref_tenant_project_product_code
    type: string
    phys: varchar(128)
    desc: 租户产品-项目
  - name: ref_tenant_project_tenant_code
    type: string
    phys: varchar(128)
    desc: 租户-项目
  - name: refer_tenant_project_id
    type: number
    phys: bigint(20)
    desc: 复制的租户项目
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: risk_control_contact_b
    type: string
    phys: varchar(64)
    desc: 风控对接人B
    roles: [result]
  - name: send_email
    type: string
    phys: varchar(100)
    desc: 是否发送邮件
    topk: 0|1
  - name: share_flag
    type: string
    phys: varchar(4)
    desc: 共享租户
    topk: N|Y
  - name: solution_manager
    type: string
    phys: varchar(64)
    desc: 方案经理
    topk: 1|11|111|53543643
  - name: source_id
    type: string
    phys: varchar(32)
    desc: 项目来源id
  - name: tenant_flg_en
    type: string
    phys: varchar(128)
    desc: 项目标识（英文）
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: 租户编码
  - name: test_data
    type: string
    phys: varchar(4)
    desc: 是否测试数据
    topk: N|Y
  - name: text
    type: string
    phys: varchar(1000)
    desc: 备注
  - name: top_flag
    type: string
    phys: varchar(4)
    desc: 置顶标识
    topk: 0|1
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
  - name: wechat_audit_no
    type: string
    phys: varchar(40)
    desc: 企微审批编号
  - name: wechat_audit_pass_time
    type: temporal
    phys: datetime
    desc: 项目立项审批通过时间
```

## 关联表

- [[ca_fee_project_config]]：tenant_project.id → ca_fee_project_config.project_id（write-flow:CaFeeProjectConfigService.java，confirmed）
- [[cust_project_rel]]：tenant_project.ref_tenant_project_platform_product → cust_project_rel.ref_cust_project_rel_platform_product（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[platform_product]]：tenant_project.ref_tenant_project_platform_product → platform_product.code（ref-convention:TenantProjectDO.java，suggested）
- [[tenant_product]]：tenant_project.ref_tenant_project_tenant_code → tenant_product.ref_tenant_product_tenant_setting_config（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_project_approval]]：tenant_project.code → tenant_project_approval.ref_tenant_project_approval_tenant_project（ref-convention:TenantProjectApprovalDO.java，suggested）
