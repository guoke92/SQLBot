---
type: table
title: 企微立项申请
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
contract_version: "0.3"
belong: tables
scenes: [wechat_project_stats]
---

# 企微立项申请

立项统计主档。`act_procinst_status`：代码注释 `'1'` 审批中、`'2'` 已通过。`data_source`：MANUAL 模拟立项 / WECHAT 真实立项。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[wechat_project_stats]]

`id`, `enable`, `create_time`, `update_time`, `act_procinst_status`, `data_source`, `first_settlement_time`, `project_id`, `project_phase`, `sp_no`, `sp_type`

### 未分窗

仍留表页，待代码证据划入场景：`ka_white_label`, `prd`, `product_type`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `app_tenant_code`, `apply_start_time`, `archives_contact`, `archives_contact_group`, `bank_quota`, `business_center`, `bussiness_manager`, `capital_branch_name`, `capital_org_full_name`, `comment`, `core_enterprise`, `credit_enhancer`, `custom_field_one`, `custom_field_statistics_one`, `custom_field_three`, `custom_field_two`, `db_tenant_code`, `enterprise_full_name`, `fund_manager`, `lls_participate_role`, `main_project_name`, `name`, `old_solution_manager`, `op_contact`, `op_contact_group`, `organization_id`, `product_type_arr`, `project_approval_name`, `project_config_time`, `project_exception_remark`, `project_focus_level`, `project_manager`, `project_online_name`, `project_type`, `remark`, `risk_control_contact`, `risk_control_contact_group`, `shelf_scale`, `solution_manager`, `solution_manager_wxid`, `sp_pass_time`, `statics_op_time`, `statics_op_user`, `system_delivery`

```ground:table
table: wechat_project_approval_apply
database: lowcode_pplatform
desc: 企业立项申请表
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [wechat_project_stats]
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
    group: always
    scenes: [wechat_project_stats]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [wechat_project_stats]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [wechat_project_stats]
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
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: "当前审批状态"
    topk: "1|2|3|4"
    roles: [query]
    scenes: [wechat_project_stats]
  - name: data_source
    type: string
    phys: varchar(64)
    desc: "数据来源"
    topk: "MANUAL|WECHAT"
    scenes: [wechat_project_stats]
  - name: first_settlement_time
    type: temporal
    phys: datetime
    desc: "首笔落地时间"
    scenes: [wechat_project_stats]
  - name: ka_white_label
    type: string
    phys: varchar(64)
    desc: "KA是否贴牌"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: prd
    type: string
    phys: varchar(64)
    desc: "是否投产"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: product_type
    type: string
    phys: varchar(200)
    desc: "产品类型"
    dict: product_type
    labels: "GENERAL:通用产品|INTERWORKING:互通产品|2:全部产品"
  - name: project_id
    type: number
    phys: bigint(20)
    desc: "项目id"
    scenes: [wechat_project_stats]
  - name: project_phase
    type: string
    phys: varchar(64)
    desc: "项目阶段"
    topk: "HANG|IMPLEMENTATION|OPERATION"
    scenes: [wechat_project_stats]
  - name: sp_no
    type: string
    phys: varchar(64)
    desc: "审批单号"
    roles: [query]
    scenes: [wechat_project_stats]
  - name: sp_type
    type: string
    phys: varchar(64)
    desc: "审批类型"
    roles: [query]
    scenes: [wechat_project_stats]
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
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "base"
  - name: apply_start_time
    type: temporal
    phys: datetime
    desc: "发起立项时间"
  - name: archives_contact
    type: string
    phys: varchar(64)
    desc: "档案对接人"
    topk: "108|383|463"
  - name: archives_contact_group
    type: string
    phys: varchar(100)
    desc: "档案组别"
    topk: "A1|审核组2|运营组别0123"
  - name: bank_quota
    type: string
    phys: varchar(30)
    desc: "银行额度(万元)"
    topk: "100|1000|10000|100000|1000万|100万|1234567890|200000|2000万|222|333|4324324"
  - name: business_center
    type: string
    phys: varchar(128)
    desc: "业务中心"
  - name: bussiness_manager
    type: string
    phys: varchar(64)
    desc: "业务经理"
  - name: capital_branch_name
    type: string
    phys: varchar(255)
    desc: "资方分支行"
  - name: capital_org_full_name
    type: string
    phys: varchar(255)
    desc: "资方全称"
  - name: comment
    type: string
    phys: varchar(500)
    desc: "备注"
  - name: core_enterprise
    type: string
    phys: varchar(100)
    desc: "核心企业"
  - name: credit_enhancer
    type: string
    phys: varchar(200)
    desc: "增信主体"
    topk: "111|你容易|增信主体0806|增信主体818|投行增信主体0728|金融科技增信主体0728"
  - name: custom_field_one
    type: string
    phys: varchar(500)
    desc: "自定义字段一"
    topk: "导入字段一测试-20260814114300"
  - name: custom_field_statistics_one
    type: string
    phys: varchar(500)
    desc: "自定义字段一(统计用)"
  - name: custom_field_three
    type: string
    phys: varchar(500)
    desc: "自定义字段三"
    topk: "导入字段三测试-20260814114300"
  - name: custom_field_two
    type: string
    phys: varchar(500)
    desc: "自定义字段二"
    topk: "导入字段二测试-20260814114300"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "base"
  - name: enterprise_full_name
    type: string
    phys: varchar(255)
    desc: "企业全称"
  - name: fund_manager
    type: string
    phys: varchar(64)
    desc: "管理人"
  - name: lls_participate_role
    type: string
    phys: varchar(200)
    desc: "联易融参与角色"
  - name: main_project_name
    type: string
    phys: varchar(200)
    desc: "主项目名称"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: old_solution_manager
    type: string
    phys: varchar(1000)
    desc: "前方案经理"
  - name: op_contact
    type: string
    phys: varchar(64)
    desc: "运营对接人"
    topk: "257|280|333|383|411|412|454|463|466|93"
  - name: op_contact_group
    type: string
    phys: varchar(100)
    desc: "运营组别"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: product_type_arr
    type: string
    phys: varchar(200)
    desc: "产品类型数组"
  - name: project_approval_name
    type: string
    phys: varchar(200)
    desc: "立项名称"
  - name: project_config_time
    type: temporal
    phys: datetime
    desc: "项目配置时间"
  - name: project_exception_remark
    type: string
    phys: varchar(500)
    desc: "项目异常备注"
  - name: project_focus_level
    type: string
    phys: varchar(500)
    desc: "项目投入关注度"
  - name: project_manager
    type: string
    phys: varchar(64)
    desc: "项目经理"
  - name: project_online_name
    type: string
    phys: varchar(200)
    desc: "项目上线名称"
  - name: project_type
    type: string
    phys: varchar(64)
    desc: "项目类型"
    topk: "MAIN|SUB"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: risk_control_contact
    type: string
    phys: varchar(64)
    desc: "风控对接人"
    topk: "271|293|360|383|454|457|97"
  - name: risk_control_contact_group
    type: string
    phys: varchar(100)
    desc: "风控对接人组别"
  - name: shelf_scale
    type: string
    phys: varchar(64)
    desc: "储架规模(万)"
  - name: solution_manager
    type: string
    phys: varchar(64)
    desc: "方案经理"
  - name: solution_manager_wxid
    type: string
    phys: varchar(64)
    desc: "方案经理企微id"
  - name: sp_pass_time
    type: temporal
    phys: datetime
    desc: "立项审批通过时间"
  - name: statics_op_time
    type: temporal
    phys: datetime
    desc: "项目统计更新时间"
  - name: statics_op_user
    type: string
    phys: varchar(100)
    desc: "项目统计更新用户"
  - name: system_delivery
    type: string
    phys: varchar(64)
    desc: "系统交付方式"
```
