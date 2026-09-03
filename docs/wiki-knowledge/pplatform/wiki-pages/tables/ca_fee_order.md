---
type: table
title: CA服务费订单
page_key: ca_fee_order
domain: 基线
status: draft
anchors: [ca_fee_order]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# CA服务费订单

（基线页：52 字段，行数估计 1351。行语义/常用过滤待语义摄取增强。）

```ground:table
table: ca_fee_order
database: lowcode_pplatform
desc: CA服务费订单
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: invoice_status
    type: string
    phys: varchar(64)
    desc: 发票状态
    dict: invoice_status
    topk: ISSUED|PENDING
  - name: order_status
    type: string
    phys: varchar(64)
    desc: 订单状态
    dict: order_status
    topk: CLOSED|PAID|PAIDING|PENDING
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
  - name: agreement_file_path
    type: string
    phys: varchar(2048)
    desc: 签章后协议文件 COS 路径
  - name: agreement_sign_time
    type: temporal
    phys: datetime
    desc: 收费协议签署时间
  - name: agreement_signed
    type: string
    phys: varchar(2)
    desc: 是否已签署收费协议
    topk: N|Y
  - name: agreement_version
    type: string
    phys: varchar(64)
    desc: 签署时绑定的收费协议版本号
    topk: V1.0
  - name: annual_fee
    type: number
    phys: int(10)
    desc: 应缴年费（元）
    topk: 0|100|120|125
    group: annual_fee_group
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: base
  - name: bocom_pay_info
    type: string
    phys: text
    desc: 交e保虚拟户快照JSON
  - name: bocom_plfm_bsn_id
    type: string
    phys: varchar(128)
    desc: 平台业务编号
    topk: 31020250010
  - name: bocom_plfm_ser_no
    type: string
    phys: varchar(128)
    desc: 交e保平台流水号
  - name: bocom_req_sn
    type: string
    phys: varchar(128)
    desc: 请求流水号
  - name: bocom_txn_sts
    type: string
    phys: varchar(64)
    desc: 响应状态
    topk: 00
  - name: certification_no
    type: string
    phys: varchar(64)
    desc: 统一社会信用代码
  - name: close_reason
    type: string
    phys: varchar(1024)
    desc: 关闭原因（关开关/手动关闭等）
    topk: 企业取消关联该项目|服务已到期|特殊定价调整为0元|特殊定价配置已移除
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 企业 ID
  - name: company_name
    type: string
    phys: varchar(512)
    desc: 企业名称
  - name: company_type
    type: string
    phys: varchar(64)
    desc: 企业角色：SUPPLIER/CORE
    topk: CORE|PROJECT_COMPANY|SUPPLIER
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 2058511807267647490|2071421244075745282|2071574824476811266|2071787264137306113
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: 13833257680|14749404214|15843203591|18806292030
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_boscebl|ISOLATE_TAG_yccsfzjt|LN1|beehive-scf.qhhrly.cn
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
  - name: invoice_fail_reason
    type: string
    phys: varchar(64)
    desc: 开票失败原因
  - name: invoice_file_path
    type: string
    phys: varchar(2048)
    desc: 发票PDF 文件COS路径
  - name: invoice_no
    type: string
    phys: varchar(128)
    desc: 发票号码
  - name: invoice_request_id
    type: string
    phys: varchar(256)
    desc: 开票平台请求号
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: operate_logs
    type: string
    phys: text
    desc: 操作轨迹 JSON 数组
  - name: order_no
    type: string
    phys: varchar(128)
    desc: 订单号，唯一键
  - name: order_type
    type: string
    phys: varchar(64)
    desc: 订单类型
    topk: FIRST|RENEW|RENEW_EXPIRED|STOCK
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: pay_amount
    type: number
    phys: int(10)
    desc: 实缴金额（元）
    topk: 0|100|120|125
    group: annual_fee_group, pay_amount_group
  - name: pay_method
    type: string
    phys: varchar(64)
    desc: 支付方式
    topk: BOCOM
  - name: pay_remark
    type: string
    phys: varchar(512)
    desc: 打款备注
  - name: pay_time
    type: temporal
    phys: datetime
    desc: 缴费成功时间
    group: pay_amount_group
  - name: project_id
    type: number
    phys: bigint(20)
    desc: 触发项目 ID
  - name: project_name
    type: string
    phys: varchar(512)
    desc: 项目名称
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: service_end
    type: temporal
    phys: date
    desc: 本单服务周期截止日（含）
  - name: service_start
    type: temporal
    phys: date
    desc: 本单服务周期起始日（含）
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: 所属租户 ID
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 2058511807267647490|2071421244075745282|2071574824476811266|2071787264137306113
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: 13833257680|14749404214|15843203591|18806292030
  - name: version
    type: number
    phys: int(10)
    desc: 乐观锁版本号，更新订单状态时自增
    topk: 0|1|18|2
```

## 关联表

- [[ca_fee_company]]：ca_fee_order.project_id → ca_fee_company.source_project_id（write-flow:CaFeeOrderService.java，confirmed）
