---
type: table
title: 企业立项申请表
page_key: wechat_project_approval_apply
domain: 微企链立项与项目审批
status: draft
anchors: [wechat_project_approval_apply]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












wechat_project_approval_apply 是项目立项统计页的主表，既承载来自企微审批的真实立项数据，也承载手工录入的[[concepts/simulated_project|模拟立项]]数据。列表、导出、提醒 Job 与批量变更都围绕本表展开，字段分为三类：审批来源标识（sp_type、system_delivery、act_procinst_status）、项目属性（project_type、project_phase、data_source、ka_white_label）、以及人员与产品信息（方案经理、运营对接人、产品类型、首笔落地时间）。

## 需求背景

需求文档未就本表单独提出主张；本次分析的全部字段语义均来自代码。项目阶段、企微审批状态、数据来源三个状态机分别见 [[processes/project_phase]]、[[processes/act_procinst_status]]、[[processes/data_source]]。

## 版本演进

v0 契约首版。人员字段采用「中文姓名字段 + 企微 userId 列表字段」的双轨存储：solution_manager 为姓名 CSV，solution_manager_wxid 为企微 userId 的 JSON 数组字符串，改人时由 [[rules/solution_manager_change_linkage|方案经理变更联动]] 保证两者一致，并把原值合并进 old_solution_manager。product_type_arr（编码 JSON）与 product_type（中文 CSV）同样成对。

```ground:table
table: wechat_project_approval_apply
database: lowcode_pplatform
desc: 企业立项申请表
fields:
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
    dict: wechat_project_approval_apply__act_procinst_status
    topk: "1|2|3|4"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: ka_white_label
    type: string
    phys: varchar(64)
    desc: KA是否贴牌
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: prd
    type: string
    phys: varchar(64)
    desc: 是否投产
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: project_type
    type: string
    phys: varchar(64)
    desc: 项目类型
    dict: wechat_project_approval_apply__project_type
    topk: "MAIN|SUB"
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
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "base"
  - name: apply_start_time
    type: temporal
    phys: datetime
    desc: 发起立项时间
  - name: archives_contact
    type: string
    phys: varchar(64)
    desc: 档案对接人
    topk: "108|383|463"
  - name: archives_contact_group
    type: string
    phys: varchar(100)
    desc: 档案组别
    topk: "A1|审核组2|运营组别0123"
  - name: bank_quota
    type: string
    phys: varchar(30)
    desc: 银行额度(万元)
    topk: "100|1000|10000|100000|1000万|100万|1234567890|200000|2000万|222|333|4324324"
  - name: business_center
    type: string
    phys: varchar(128)
    desc: 业务中心
  - name: bussiness_manager
    type: string
    phys: varchar(64)
    desc: 业务经理
  - name: capital_branch_name
    type: string
    phys: varchar(255)
    desc: 资方分支行
  - name: capital_org_full_name
    type: string
    phys: varchar(255)
    desc: 资方全称
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: comment
    type: string
    phys: varchar(500)
    desc: 备注
  - name: core_enterprise
    type: string
    phys: varchar(100)
    desc: 核心企业
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: credit_enhancer
    type: string
    phys: varchar(200)
    desc: 增信主体
    topk: "111|你容易|增信主体0806|增信主体818|投行增信主体0728|金融科技增信主体0728"
  - name: custom_field_one
    type: string
    phys: varchar(500)
    desc: 自定义字段一
    topk: "导入字段一测试-20260814114300"
  - name: custom_field_statistics_one
    type: string
    phys: varchar(500)
    desc: 自定义字段一(统计用)
  - name: custom_field_three
    type: string
    phys: varchar(500)
    desc: 自定义字段三
    topk: "导入字段三测试-20260814114300"
  - name: custom_field_two
    type: string
    phys: varchar(500)
    desc: 自定义字段二
    topk: "导入字段二测试-20260814114300"
  - name: data_source
    type: string
    phys: varchar(64)
    desc: 数据来源
    topk: "MANUAL|WECHAT"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "base"
  - name: enterprise_full_name
    type: string
    phys: varchar(255)
    desc: 企业全称
  - name: first_settlement_time
    type: temporal
    phys: datetime
    desc: 首笔放款时间
  - name: fund_manager
    type: string
    phys: varchar(64)
    desc: 管理人
  - name: lls_participate_role
    type: string
    phys: varchar(200)
    desc: 联易融参与角色
  - name: main_project_name
    type: string
    phys: varchar(200)
    desc: 主项目名称
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: old_solution_manager
    type: string
    phys: varchar(1000)
    desc: 前方案经理
  - name: op_contact
    type: string
    phys: varchar(64)
    desc: 运营对接人
    topk: "257|280|333|383|411|412|454|463|466|93"
  - name: op_contact_group
    type: string
    phys: varchar(100)
    desc: 运营组别
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: product_type
    type: string
    phys: varchar(200)
    desc: 产品类型
  - name: product_type_arr
    type: string
    phys: varchar(200)
    desc: 产品类型数组
  - name: project_approval_name
    type: string
    phys: varchar(200)
    desc: 立项名称
  - name: project_config_time
    type: temporal
    phys: datetime
    desc: 项目配置时间
  - name: project_exception_remark
    type: string
    phys: varchar(500)
    desc: 项目异常备注
  - name: project_focus_level
    type: string
    phys: varchar(500)
    desc: 项目投入关注度
  - name: project_id
    type: number
    phys: bigint(20)
    desc: 关联的项目id
  - name: project_manager
    type: string
    phys: varchar(64)
    desc: 项目经理
  - name: project_online_name
    type: string
    phys: varchar(200)
    desc: 项目上线名称
  - name: project_phase
    type: string
    phys: varchar(64)
    desc: 项目阶段
    topk: "HANG|IMPLEMENTATION|OPERATION"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: risk_control_contact
    type: string
    phys: varchar(64)
    desc: 风控对接人
    topk: "271|293|360|383|454|457|97"
  - name: risk_control_contact_group
    type: string
    phys: varchar(100)
    desc: 风控对接人组别
  - name: shelf_scale
    type: string
    phys: varchar(64)
    desc: 储架规模(万)
  - name: solution_manager
    type: string
    phys: varchar(64)
    desc: 方案经理
  - name: solution_manager_wxid
    type: string
    phys: varchar(64)
    desc: 方案经理企微id
  - name: sp_no
    type: string
    phys: varchar(64)
    desc: 企微审批编号
  - name: sp_pass_time
    type: temporal
    phys: datetime
    desc: 立项审批通过时间
  - name: sp_type
    type: string
    phys: varchar(64)
    desc: 类型
  - name: statics_op_time
    type: temporal
    phys: datetime
    desc: 项目统计更新时间
  - name: statics_op_user
    type: string
    phys: varchar(100)
    desc: 项目统计更新用户
  - name: system_delivery
    type: string
    phys: varchar(64)
    desc: 系统交付方式
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

## 关联表

- [[wechat_project_approval_field_history]]：wechat_project_approval_apply.sp_no → wechat_project_approval_field_history.sp_no（copy:ProjectStatisticsApplication.java，suggested）
