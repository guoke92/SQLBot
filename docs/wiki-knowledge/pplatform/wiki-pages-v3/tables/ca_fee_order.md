---
type: table
title: CA 服务费订单
page_key: ca_fee_order
domain: CA证书收费
status: draft
anchors: [ca_fee_order]
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

# CA 服务费订单

场景 [[scenarios/ca_fee]] 的**流水表**：一行是一次首次缴费 / 续费 / 存量补录。企业当前结论在主档 [[tables/ca_fee_company]]。

`order_status` 的 PAID 不等于企业 `pay_status` 的 PAID（多笔订单、关闭单、到期回落），见 [[concepts/paid]]。取值与库分布见 [[enums/order_status]]。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[ca_fee]]

`id`, `enable`, `create_time`, `update_time`, `agreement_signed`, `annual_fee`, `bocom_txn_sts`, `certification_no`, `company_type`, `invoice_status`, `order_no`, `order_status`, `order_type`, `pay_amount`, `pay_time`, `project_id`, `service_end`, `service_start`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `agreement_file_path`, `agreement_sign_time`, `agreement_version`, `app_tenant_code`, `bocom_pay_info`, `bocom_plfm_bsn_id`, `bocom_plfm_ser_no`, `bocom_req_sn`, `close_reason`, `company_id`, `company_name`, `db_tenant_code`, `invoice_fail_reason`, `invoice_file_path`, `invoice_no`, `invoice_request_id`, `name`, `operate_logs`, `organization_id`, `pay_method`, `pay_remark`, `project_name`, `remark`, `tenant_id`, `version`

```ground:table
table: ca_fee_order
database: lowcode_pplatform
desc: CA服务费订单
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
    topk: "N|Y"
    labels: "N:否|Y:是"
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
  - name: agreement_signed
    type: string
    phys: varchar(2)
    desc: "是否已签署收费协议"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [ca_fee]
  - name: annual_fee
    type: number
    phys: int(10)
    desc: "应缴年费（元）"
    scenes: [ca_fee]
  - name: bocom_txn_sts
    type: string
    phys: varchar(64)
    desc: "响应状态"
    topk: "00"
    scenes: [ca_fee]
  - name: certification_no
    type: string
    phys: varchar(64)
    desc: "统一社会信用代码"
    scenes: [ca_fee]
  - name: company_type
    type: string
    phys: varchar(64)
    desc: "企业角色：SUPPLIER/CORE"
    topk: "CORE|PROJECT_COMPANY|SUPPLIER"
    scenes: [ca_fee]
  - name: invoice_status
    type: string
    phys: varchar(64)
    desc: "发票状态"
    dict: invoice_status
    topk: "ISSUED|PENDING"
    labels: "ISSUED:已开票|PENDING:开票中"
    scenes: [ca_fee]
  - name: order_no
    type: string
    phys: varchar(128)
    desc: "订单号，唯一键"
    scenes: [ca_fee]
  - name: order_status
    type: string
    phys: varchar(64)
    desc: "订单状态"
    dict: order_status
    topk: "CLOSED|PAID|PAIDING|PENDING|UNPAID"
    labels: "CLOSED:已关闭|PAID:已缴费|PENDING:未缴费"
    scenes: [ca_fee]
  - name: order_type
    type: string
    phys: varchar(64)
    desc: "订单类型"
    topk: "FIRST|RENEW|RENEW_EXPIRED|STOCK"
    scenes: [ca_fee]
  - name: pay_amount
    type: number
    phys: int(10)
    desc: "实缴金额（元）"
    scenes: [ca_fee]
  - name: pay_time
    type: temporal
    phys: datetime
    desc: "缴费成功时间"
    scenes: [ca_fee]
  - name: project_id
    type: number
    phys: bigint(20)
    desc: "触发项目 ID"
    scenes: [ca_fee]
  - name: service_end
    type: temporal
    phys: date
    desc: "本单服务周期截止日（含）"
    scenes: [ca_fee]
  - name: service_start
    type: temporal
    phys: date
    desc: "本单服务周期起始日（含）"
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
  - name: agreement_file_path
    type: string
    phys: varchar(2048)
    desc: "签章后协议文件 COS 路径"
    labels: "COS:路径"
  - name: agreement_sign_time
    type: temporal
    phys: datetime
    desc: "收费协议签署时间"
  - name: agreement_version
    type: string
    phys: varchar(64)
    desc: "签署时绑定的收费协议版本号"
    topk: "V1.0"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "base"
  - name: bocom_pay_info
    type: string
    phys: text
    desc: "交e保虚拟户快照JSON"
  - name: bocom_plfm_bsn_id
    type: string
    phys: varchar(128)
    desc: "平台业务编号"
  - name: bocom_plfm_ser_no
    type: string
    phys: varchar(128)
    desc: "交e保平台流水号"
  - name: bocom_req_sn
    type: string
    phys: varchar(128)
    desc: "请求流水号"
  - name: close_reason
    type: string
    phys: varchar(1024)
    desc: "关闭原因（关开关/手动关闭等）"
  - name: company_id
    type: number
    phys: bigint(20)
    desc: "企业 ID"
  - name: company_name
    type: string
    phys: varchar(512)
    desc: "企业名称"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "ISOLATE_TAG_boscebl|ISOLATE_TAG_yccsfzjt|LN1|beehive-scf.qhhrly.cn|xylxchf"
  - name: invoice_fail_reason
    type: string
    phys: varchar(64)
    desc: "开票失败原因"
  - name: invoice_file_path
    type: string
    phys: varchar(2048)
    desc: "发票PDF 文件COS路径"
  - name: invoice_no
    type: string
    phys: varchar(128)
    desc: "发票号码"
  - name: invoice_request_id
    type: string
    phys: varchar(256)
    desc: "开票平台请求号"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: operate_logs
    type: string
    phys: text
    desc: "操作轨迹 JSON 数组"
    labels: "JSON:数组"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: pay_method
    type: string
    phys: varchar(64)
    desc: "支付方式"
    topk: "BOCOM"
  - name: pay_remark
    type: string
    phys: varchar(512)
    desc: "打款备注"
  - name: project_name
    type: string
    phys: varchar(512)
    desc: "项目名称"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: "所属租户 ID"
  - name: version
    type: number
    phys: int(10)
    desc: "乐观锁版本号，更新订单状态时自增"
```
