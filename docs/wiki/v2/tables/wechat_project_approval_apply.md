---
type: table
title: 企业立项申请表
page_key: wechat_project_approval_apply
belong: tables
status: draft
anchors: [wechat_project_approval_apply]
sources: ['database_schema:lowcode_pplatform.wechat_project_approval_apply']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [wechat_project_approval_field_history, wechat_project_approval_apply__prd,
  wechat_project_approval_apply__op_contact, wechat_project_approval_apply__archives_contact,
  wechat_project_approval_apply__risk_control_contact, wechat_project_approval_apply__enable,
  wechat_project_approval_apply__act_procinst_status, wechat_project_approval_apply__project_type,
  wechat_project_approval_apply__ka_white_label, wechat_project_approval_apply__project_phase,
  wechat_project_approval_apply__data_source, wechat_project_approval_apply__bank_quota]
---

# 企业立项申请表

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: wechat_project_approval_apply
database: lowcode_pplatform
desc: 企业立项申请表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [project_approval_name, main_project_name, project_online_name, code,
  name, capital_org_full_name, capital_branch_name, enterprise_full_name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: sp_no
  type: string
  desc: 企微审批编号
- name: sp_type
  type: string
  desc: 类型
- name: product_type
  type: string
  desc: 产品类型
- name: project_approval_name
  type: string
  desc: 立项名称
- name: main_project_name
  type: string
  desc: 主项目名称
- name: sp_pass_time
  type: temporal
  desc: 立项审批通过时间
- name: project_online_name
  type: string
  desc: 项目上线名称
- name: prd
  type: string
  desc: 是否投产
  dict: [N, Y]
- name: bussiness_manager
  type: string
  desc: 业务经理
- name: op_contact
  type: string
  desc: 运营对接人
  dict: ['454', '383', '466', '463', '280', '257', '333', '93', '412', '411']
- name: op_contact_group
  type: string
  desc: 运营组别
- name: archives_contact
  type: string
  desc: 档案对接人
  dict: ['463', '383', '97', '108']
- name: archives_contact_group
  type: string
  desc: 档案组别
- name: risk_control_contact
  type: string
  desc: 风控对接人
  dict: ['360', '383', '97', '454', '293', '271', '457', '257']
- name: risk_control_contact_group
  type: string
  desc: 风控对接人组别
- name: comment
  type: string
  desc: 备注
- name: project_manager
  type: string
  desc: 项目经理
- name: solution_manager
  type: string
  desc: 方案经理
- name: custom_field_one
  type: string
  desc: 自定义字段一
- name: custom_field_two
  type: string
  desc: 自定义字段二
- name: custom_field_three
  type: string
  desc: 自定义字段三
- name: project_id
  type: number
  desc: 关联的项目id
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict: [Y, N]
- name: remark
  type: string
  desc: remark
- name: create_by
  type: string
  desc: 创建人id
- name: create_user
  type: string
  desc: 创建人名称
- name: create_time
  type: temporal
  desc: 创建时间
  nullable: false
- name: update_by
  type: string
  desc: 更新人id
- name: update_user
  type: string
  desc: 更新人名称
- name: update_time
  type: temporal
  desc: 更新时间
  nullable: false
- name: act_procinst_id
  type: string
  desc: 流程实例ID
- name: app_tenant_code
  type: string
  desc: 逻辑租户标识
- name: db_tenant_code
  type: string
  desc: 数据租户标识
- name: act_procinst_no
  type: string
  desc: 流程申请编号
- name: act_procinst_status
  type: string
  desc: 当前审批状态
  dict: ['2', '3', '4', '1']
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
- name: project_config_time
  type: temporal
  desc: 项目配置时间
- name: first_settlement_time
  type: temporal
  desc: 首笔放款时间
- name: project_type
  type: string
  desc: 项目类型
  dict: [SUB, MAIN]
- name: ka_white_label
  type: string
  desc: KA是否贴牌
  dict: [Y, N]
- name: project_phase
  type: string
  desc: 项目阶段
  dict: [IMPLEMENTATION, OPERATION, HANG]
- name: apply_start_time
  type: temporal
  desc: 发起立项时间
- name: business_center
  type: string
  desc: 业务中心
- name: capital_org_full_name
  type: string
  desc: 资方全称
- name: project_exception_remark
  type: string
  desc: 项目异常备注
- name: capital_branch_name
  type: string
  desc: 资方分支行
- name: enterprise_full_name
  type: string
  desc: 企业全称
- name: project_focus_level
  type: string
  desc: 项目投入关注度
- name: data_source
  type: string
  desc: 数据来源
  dict: [WECHAT, MANUAL]
- name: custom_field_statistics_one
  type: string
  desc: 自定义字段一(统计用)
- name: solution_manager_wxid
  type: string
  desc: 方案经理企微id
- name: old_solution_manager
  type: string
  desc: 前方案经理
- name: system_delivery
  type: string
  desc: 系统交付方式
- name: product_type_arr
  type: string
  desc: 产品类型数组
- name: statics_op_user
  type: string
  desc: 项目统计更新用户
- name: statics_op_time
  type: temporal
  desc: 项目统计更新时间
- name: bank_quota
  type: string
  desc: 银行额度(万元)
  dict: [1000万, 100万, '1000', '10000', '4324324', '100', '200000', '1234567890', '333',
    2000万, '222', '100000']
- name: core_enterprise
  type: string
  desc: 核心企业
- name: credit_enhancer
  type: string
  desc: 增信主体
- name: fund_manager
  type: string
  desc: 管理人
- name: lls_participate_role
  type: string
  desc: 联易融参与角色
- name: shelf_scale
  type: string
  desc: 储架规模(万)
```

## 页面链接

### 关联表

- [[tables/wechat_project_approval_field_history]]

### 字典

- [[dicts/wechat_project_approval_apply__prd]]（`wechat_project_approval_apply.prd`）
- [[dicts/wechat_project_approval_apply__op_contact]]（`wechat_project_approval_apply.op_contact`）
- [[dicts/wechat_project_approval_apply__archives_contact]]（`wechat_project_approval_apply.archives_contact`）
- [[dicts/wechat_project_approval_apply__risk_control_contact]]（`wechat_project_approval_apply.risk_control_contact`）
- [[dicts/wechat_project_approval_apply__enable]]（`wechat_project_approval_apply.enable`）
- [[dicts/wechat_project_approval_apply__act_procinst_status]]（`wechat_project_approval_apply.act_procinst_status`）
- [[dicts/wechat_project_approval_apply__project_type]]（`wechat_project_approval_apply.project_type`）
- [[dicts/wechat_project_approval_apply__ka_white_label]]（`wechat_project_approval_apply.ka_white_label`）
- [[dicts/wechat_project_approval_apply__project_phase]]（`wechat_project_approval_apply.project_phase`）
- [[dicts/wechat_project_approval_apply__data_source]]（`wechat_project_approval_apply.data_source`）
- [[dicts/wechat_project_approval_apply__bank_quota]]（`wechat_project_approval_apply.bank_quota`）
