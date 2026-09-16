---
type: table
title: CA 服务费项目配置
page_key: ca_fee_project_config
domain: CA证书收费
status: draft
anchors: [ca_fee_project_config]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [ca_fee]
---

# CA 服务费项目配置

场景 [[scenarios/ca_fee]] 的**配置表**：项目是否收费、角色价、特殊名单。不是主档，问「已缴费企业」不要 FROM 本表。

`agreement_version`、`pay_channel` 不是 [[enums/enable]]。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[ca_fee]]

`id`, `enable`, `create_time`, `update_time`, `charge_enabled`, `core_annual_fee`, `project_id`, `special_company_list`, `supplier_annual_fee`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `agreement_version`, `app_tenant_code`, `block_scene_list`, `db_tenant_code`, `last_toggle_time`, `name`, `organization_id`, `pay_channel`, `remark`, `tenant_id`

```ground:table
table: ca_fee_project_config
database: lowcode_pplatform
desc: CA服务费项目配置
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [ca_fee]
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
    group: always
    scenes: [ca_fee]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [ca_fee]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [ca_fee]
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
  - name: charge_enabled
    type: string
    phys: varchar(2)
    desc: "是否开启CA收费"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [ca_fee]
  - name: core_annual_fee
    type: number
    phys: int(10)
    desc: "核心企业角色年费（元）"
    scenes: [ca_fee]
  - name: project_id
    type: number
    phys: bigint(20)
    desc: "项目ID"
    scenes: [ca_fee]
  - name: special_company_list
    type: string
    phys: text
    desc: "特殊企业配置JSON数组"
    scenes: [ca_fee]
  - name: supplier_annual_fee
    type: number
    phys: int(10)
    desc: "供应商角色年费（元）"
    scenes: [ca_fee]
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
  - name: agreement_version
    type: string
    phys: varchar(64)
    desc: "当前绑定收费协议版本号"
    topk: "V1.0"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "GREENTOWNAT|JYYL|base|boscxsbl|boscxyc|sdhsg|shanghaiyinhang"
  - name: block_scene_list
    type: string
    phys: text
    desc: "拦截场景编码 JSON 数组，元素见 CaFeeInterceptSceneEnum"
    labels: "JSON:数组"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: last_toggle_time
    type: temporal
    phys: datetime
    desc: "最近一次收费开关切换时间"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: pay_channel
    type: string
    phys: text
    desc: "缴费渠道JSON数组"
    labels: "[]:空拦截场景列表：不对未缴费企业做任何场景化拦截。|[\:存量已开收费项目迁移默认：四场景全选，保持 MVP 全量拦截。|PROJECT_DISABLED:evaluate 豁免/无需缴费原因|30:交e保未到账时前端重试间隔（秒，§6.7）|00:交e保划扣 txnSts：成功|01:交e保划扣 txnSts：银行明确失败，保留流水且禁止再次划扣|发票开具中，开具完成后可前往缴费记录下载:缴费成功页发票提示（§6.8）|companyId:消息模板上下文：企业 ID|custName:消息模板上下文：企业名称（与消息中心 {custName} 对齐）|orderNo:消息模板上下文：订单号|certificationNo:消息模板上下文：统码|serviceEndDate:消息模板上下文：服务期截止日 yyyy-MM-dd|todoDetailScene:消息模板上下文：待办场景码 NEW_PAY/ABOUT_TO_EXPIRE/EXPIRED|todoDetailMessage:消息模板上下文：待办详情完整文案（§3.1.1.2）|sceneLabel:消息模板上下文：场景标识，如【即将到期场景】|【待缴费/新缴费场景】:需求 §3.1.1.2 场景标识（与消息模板 subject 对齐）|您的CA服务费已到期，请完成缴费后再办理业务。:门户 portalCheck：needPay=Y & needOpenCa=N & feeStatus=EXPIRED|您的CA证书服务费未缴纳，请先完成CA认证。:门户 portalCheck：needPay=Y & needOpenCa=Y|您的CA服务费未缴纳，请完成缴费后再办理业务。:门户 portalCheck：needPay=Y & needOpenCa=N & feeStatus=UNPAID|业务功能暂不可用:拦截弹窗标题（需求 §5.4）|PAY:拦截按钮类型：管理员「去缴纳」|CONFIRM:拦截按钮类型：经办人「确认」|当前您的企业CA电子签章服务费尚未缴纳，请先完成电子签章服务费缴纳。:管理员拦截主文案（需求 §5.4）|当前您的企业CA电子签章服务费尚未缴纳，请先联系企业管理员%s完成电子签章服务费缴纳。:经办人拦截主文案模板，%s=管理员姓名|当前您的企业CA电子签章服务费尚未缴纳，请先联系企业管理员完成电子签章服务费缴纳。:经办人拦截主文案（未能解析管理员姓名时的降级）|7:续费提醒天数阈值（§5.2 ABOUT_TO_EXPIRE）"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: "所属租户"
```
