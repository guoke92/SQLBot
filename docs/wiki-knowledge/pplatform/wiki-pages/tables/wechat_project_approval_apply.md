---
type: table
title: 企业立项申请表
page_key: wechat_project_approval_apply
domain: 基线
status: draft
anchors: [wechat_project_approval_apply]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 企业立项申请表

（基线页：66 字段，行数估计 78。行语义/常用过滤待语义摄取增强。）

```ground:table
table: wechat_project_approval_apply
database: lowcode_pplatform
desc: 企业立项申请表
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: product_type
    type: string
    phys: varchar(200)
    desc: 产品类型
    dict: product_type
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
    topk: 1|2|3|4
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: base
  - name: apply_start_time
    type: temporal
    phys: datetime
    desc: 发起立项时间
    group: approval_pass_time_group
  - name: archives_contact
    type: string
    phys: varchar(64)
    desc: 档案对接人
    topk: 108|383|463
  - name: archives_contact_group
    type: string
    phys: varchar(100)
    desc: 档案组别
    topk: A1|审核组2|运营组别0123
  - name: bank_quota
    type: string
    phys: varchar(30)
    desc: 银行额度(万元)
    topk: 100|1000|10000|100000
  - name: business_center
    type: string
    phys: varchar(128)
    desc: 业务中心
    topk: SaaS方案部|业务中心_编辑20260814171509|业务中心_编辑20260814172238|企划发展部
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
    topk: 1|53434|fff|备注
  - name: core_enterprise
    type: string
    phys: varchar(100)
    desc: 核心企业
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1480444461854887938|1631538947253182466|1780425849947410433|1801438863791919106
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: caiweicheng|chenzerong|linyanxiang|liuhaiou
  - name: credit_enhancer
    type: string
    phys: varchar(200)
    desc: 增信主体
    topk: 111|你容易|增信主体0806|增信主体818
  - name: custom_field_one
    type: string
    phys: varchar(500)
    desc: 自定义字段一
    topk: 导入字段一测试-20260814114300
  - name: custom_field_statistics_one
    type: string
    phys: varchar(500)
    desc: 自定义字段一(统计用)
    topk: 1|54343|ffff|自动编辑自定义字段一0826
  - name: custom_field_three
    type: string
    phys: varchar(500)
    desc: 自定义字段三
    topk: 导入字段三测试-20260814114300
  - name: custom_field_two
    type: string
    phys: varchar(500)
    desc: 自定义字段二
    topk: 导入字段二测试-20260814114300
  - name: data_source
    type: string
    phys: varchar(64)
    desc: 数据来源
    topk: MANUAL|WECHAT
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: base
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
  - name: enterprise_full_name
    type: string
    phys: varchar(255)
    desc: 企业全称
  - name: first_settlement_time
    type: temporal
    phys: datetime
    desc: 首笔放款时间
    group: project_up_time_group
  - name: fund_manager
    type: string
    phys: varchar(64)
    desc: 管理人
    topk: 33|你是第一张|张三|李四
  - name: ka_white_label
    type: string
    phys: varchar(64)
    desc: KA是否贴牌
    topk: N|Y
  - name: lls_participate_role
    type: string
    phys: varchar(200)
    desc: 联易融参与角色
    topk: 其他
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
    topk: 257|280|333|383
  - name: op_contact_group
    type: string
    phys: varchar(100)
    desc: 运营组别
    topk: 1|可乐可口2|审核组2|组三
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: prd
    type: string
    phys: varchar(64)
    desc: 是否投产
    topk: N|Y
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
    topk: 1|5343|ffff|异常备注-模拟立项编辑测试0826
  - name: project_focus_level
    type: string
    phys: varchar(500)
    desc: 项目投入关注度
    topk: 1|3434|fffff|投入关注度_编辑20260814171509
  - name: project_id
    type: number
    phys: bigint(20)
    desc: 关联的项目id
  - name: project_manager
    type: string
    phys: varchar(64)
    desc: 项目经理
    topk: 导入项目经理测试
  - name: project_online_name
    type: string
    phys: varchar(200)
    desc: 项目上线名称
    topk: LN1应收易融项目|创维集团项目1
  - name: project_phase
    type: string
    phys: varchar(64)
    desc: 项目阶段
    topk: HANG|IMPLEMENTATION|OPERATION
  - name: project_type
    type: string
    phys: varchar(64)
    desc: 项目类型
    topk: MAIN|SUB
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: risk_control_contact
    type: string
    phys: varchar(64)
    desc: 风控对接人
    topk: 271|293|360|383
  - name: risk_control_contact_group
    type: string
    phys: varchar(100)
    desc: 风控对接人组别
    topk: 1|QA测试二组|ams|xxcc
  - name: shelf_scale
    type: string
    phys: varchar(64)
    desc: 储架规模(万)
    topk: 200万|500万|5555|为什么说明年
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
    topk: 投行产品类业务|金融科技业务
  - name: statics_op_time
    type: temporal
    phys: datetime
    desc: 项目统计更新时间
  - name: statics_op_user
    type: string
    phys: varchar(100)
    desc: 项目统计更新用户
    topk: 刘倍材|刘宁|林彦湘|欧阳鹏飞
  - name: system_delivery
    type: string
    phys: varchar(64)
    desc: 系统交付方式
    topk: SaaS|本地化
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1480444461854887938|1631538947253182466|1761948088379621378|1780425849947410433
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: caiweicheng|chenkaiwen|chenzerong|linyanxiang
```
