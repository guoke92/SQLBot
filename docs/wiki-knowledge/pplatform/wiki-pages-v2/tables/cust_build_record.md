---
type: table
title: 建档推送运营记录表
page_key: cust_build_record
domain: 企业建档与认证状态机
status: draft
anchors: [cust_build_record]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












本表承载客户建档异步流程失败后的补偿重试登记。与 [[client_api_sync_error]] 不同，本表没有独立的重试次数列，重试计数写在 `returnData` 的 JSON 里；失败类型写在 `remark` 前缀里，由 xxl-job 按前缀筛选后整体重放 `regAsyncService.orchestrateAsync(context)`（`pushData` 即反序列化来源）。

## 需求背景

建档链路中存在「文件推送」与「拉起流程」两个易失败的外部动作，失败时不直接抛出，而是调用 `saveCompensationRecord` 落一条 PENDING 记录，由 `regAsyncCompensationJobHandler` 定时捞取重试。重试状态机见 [[cust_build_compensation_retry]]，重试上限规则见 [[compensation_max_retry]]，失败类型识别见 [[compensation_fail_type]]。

## 版本演进

- 补偿记录以 `remark LIKE 'COMPENSATION_%'` 作为识别口径，见 [[compensation_record_filter]]；job 只扫 PENDING/RETRYING，见 [[compensation_retry_task_filter]]。
- 重试成功在 `remark` 追加 `_RETRY_SUCCESS`，达上限追加 `_FAILED_MAX_RETRY_n`，是判断记录终态最直接的旁证。

```ground:table
table: cust_build_record
database: lowcode_pplatform
desc: 建档推送运营记录表
fields:
  - name: electronic_auth_sign_status
    type: string
    phys: varchar(16)
    dict: electronic_auth_sign_status
    topk: "PENDING|SIGNED"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
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
    topk: "base"
  - name: channel
    type: string
    phys: varchar(60)
    desc: 渠道
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
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
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 企业ID
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: person_id
    type: number
    phys: bigint(20)
    desc: 联系人ID
  - name: plat_cust_id
    type: number
    phys: bigint(20)
    desc: 运营中台ID
  - name: plat_person_id
    type: number
    phys: bigint(20)
    desc: 运营中台ID
  - name: push_data
    type: string
    phys: varchar(1000)
    desc: 推送json
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: retry_status
    type: string
    phys: varchar(20)
    desc: 补偿重试状态：PENDING-待重试，RETRYING-重试中，SUCCESS-重试成功，FAILED-重试失败
  - name: return_data
    type: string
    phys: varchar(1000)
    desc: 返回data
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

- [[cust_company_info]]：cust_build_record.cust_id → cust_company_info.id（java-eq:OperCustFacade.java，suggested）
