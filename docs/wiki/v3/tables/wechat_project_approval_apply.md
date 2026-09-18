---
type: table
title: 企业立项申请表
page_key: wechat_project_approval_apply
belong: tables
status: draft
anchors: [wechat_project_approval_apply]
sources: ['database_schema:lowcode_pplatform.wechat_project_approval_apply', 'code_path:approval/ProjectApprovalApplication.java:1347']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [wechat_project_approval_field_history, wechat_project_approval_apply__sp_type,
  wechat_project_approval_apply__product_type, wechat_project_approval_apply__prd,
  wechat_project_approval_apply__enable, wechat_project_approval_apply__act_procinst_status,
  wechat_project_approval_apply__project_type, wechat_project_approval_apply__ka_white_label,
  wechat_project_approval_apply__project_phase, wechat_project_approval_apply__data_source,
  wechat_project_approval_apply__system_delivery, wechat_project_approval_apply__lls_participate_role]
---

# 企业立项申请表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: wechat_project_approval_apply
database: lowcode_pplatform
desc: 企业立项申请表
inactive: false
primary_key: [id]
grain: 企微审批单
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
  dict: [金融科技业务, 投行产品类业务, 金融科技业务（仅智能工具）]
- name: product_type
  type: string
  desc: 产品类型
  dict: [凭证-直保, '凭证-直保,凭证-再保', 供应链票据, 供应链ABS/ABN, '凭证-直保,凭证-再保,凭证-质押', 凭证-质押, 凭证-再保,
    供应链ABS, 本地化, '凭证-直保,凭证-质押', 线上保理-再保, '凭证-直保,凭证-再保,凭证-质押,线上保理-直保,线上保理-再保,跨境保理,线上保理-质押,供应链票据,国内信用证,订单融资,经销商融资,其他（具体在项目描述中说明）',
    '凭证-直保,凭证-再保,凭证-质押,线上保理-直保,线上保理-再保,经销商融资', SaaS+本地化, '订单融资,经销商融资', 跨境保理, 线上保理-质押,
    '凭证-直保,凭证-再保,订单融资', '凭证-直保,凭证-再保,凭证-质押,线上保理-直保,线上保理-质押,线上保理-再保,跨境保理,供应链票据,国内信用证,订单融资,经销商融资,其他（具体在项目描述中说明）',
    '凭证-再保,凭证-直保', 线上保理-直保, 应收账款ABS/ABN, '其他（具体在项目描述中说明）,经销商融资,国内信用证', 供应链非标, 订单融资,
    经销商融资]
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
- name: op_contact_group
  type: string
  desc: 运营组别
- name: archives_contact
  type: string
  desc: 档案对接人
- name: archives_contact_group
  type: string
  desc: 档案组别
- name: risk_control_contact
  type: string
  desc: 风控对接人
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
  dict: [SaaS, SaaS+本地化, 本地化]
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
  dict: [原始权益人/发起机构&资产服务机构, 原始权益人/发起机构, 其他]
- name: shelf_scale
  type: string
  desc: 储架规模(万)
default_filter:
  predicate: wechat_project_approval_apply.enable = 'Y'
  trust: confirmed
  evidence: code_path:approval/ProjectApprovalApplication.java:1347
```

## 页面链接

### 关联表

- [[tables/wechat_project_approval_field_history]]

### 字典

- [[dicts/wechat_project_approval_apply__sp_type]]（`wechat_project_approval_apply.sp_type`）
- [[dicts/wechat_project_approval_apply__product_type]]（`wechat_project_approval_apply.product_type`）
- [[dicts/wechat_project_approval_apply__prd]]（`wechat_project_approval_apply.prd`）
- [[dicts/wechat_project_approval_apply__enable]]（`wechat_project_approval_apply.enable`）
- [[dicts/wechat_project_approval_apply__act_procinst_status]]（`wechat_project_approval_apply.act_procinst_status`）
- [[dicts/wechat_project_approval_apply__project_type]]（`wechat_project_approval_apply.project_type`）
- [[dicts/wechat_project_approval_apply__ka_white_label]]（`wechat_project_approval_apply.ka_white_label`）
- [[dicts/wechat_project_approval_apply__project_phase]]（`wechat_project_approval_apply.project_phase`）
- [[dicts/wechat_project_approval_apply__data_source]]（`wechat_project_approval_apply.data_source`）
- [[dicts/wechat_project_approval_apply__system_delivery]]（`wechat_project_approval_apply.system_delivery`）
- [[dicts/wechat_project_approval_apply__lls_participate_role]]（`wechat_project_approval_apply.lls_participate_role`）
