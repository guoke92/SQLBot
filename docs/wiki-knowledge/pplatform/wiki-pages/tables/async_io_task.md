---
type: table
title: 异步导入导出任务
page_key: async_io_task
domain: 基线
status: draft
anchors: [async_io_task]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 异步导入导出任务

（基线页：37 字段，行数估计 272。行语义/常用过滤待语义摄取增强。）

```ground:table
table: async_io_task
database: lowcode_pplatform
desc: 异步导入导出任务
inactive: false
fields:
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
    topk: base
  - name: biz_args_json
    type: string
    phys: text
    desc: 参数 JSON
  - name: biz_class
    type: string
    phys: varchar(264)
    desc: Controller Bean 全限定名
  - name: biz_method
    type: string
    phys: varchar(512)
    desc: 方法签名 name(paramTypes)
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1364399217692581890|1480444461854887938|1534087161817419777|1718930920919470081
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: chenkaiwen|linyanxiang|liubeicai|liuning
  - name: ctx_json
    type: string
    phys: text
    desc: 上下文：userId/custId/companyType/dbTenantCode 等
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: all
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: end_time
    type: temporal
    phys: datetime
    desc: 任务结束时间
    group: end_time_group, start_time_group
  - name: error_msg
    type: string
    phys: text
    desc: 失败原因
  - name: file_name
    type: string
    phys: varchar(300)
    desc: 文件名
  - name: file_url
    type: string
    phys: varchar(1000)
    desc: "成功:结果文件 / 失败:错误文件 的下载地址"
  - name: is_deleted
    type: string
    phys: varchar(1)
    desc: 软删除：0 否 1 是
    topk: 0|1
  - name: menu_code
    type: string
    phys: varchar(64)
    desc: 业务菜单标识
    topk: CUST_INPUT_BATCH|CUST_PROJECT_REL_BATCH|PROJECT_REPORT_STATISTICS|TENANT_PROJECT_CONFIG
  - name: menu_name
    type: string
    phys: varchar(200)
    desc: 业务菜单名称
    topk: 企业批量关联项目|企微立项审批|客户录入批量导入|项目立项统计
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: result_text
    type: string
    phys: text
    desc: 业务返回
  - name: start_time
    type: temporal
    phys: datetime
    desc: 任务开始时间
    group: end_time_group, start_time_group
  - name: status
    type: string
    phys: varchar(16)
    desc: 状态
    topk: FAILED|RUNNING|SUCCESS
  - name: task_name
    type: string
    phys: varchar(200)
    desc: 任务名称
    topk: 企业批量关联项目|企微审批申请信息-导入|企微审批申请信息-导出|客户录入批量导入
  - name: task_no
    type: number
    phys: bigint(20)
    desc: 任务号
  - name: task_type
    type: string
    phys: varchar(32)
    desc: 任务类型
    topk: EXPORT|IMPORT
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1364399217692581890|1480444461854887938|1534087161817419777|1718930920919470081
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: chenkaiwen|linyanxiang|liubeicai|liuning
  - name: user_id
    type: number
    phys: bigint(20)
    desc: 用户ID
  - name: user_name
    type: string
    phys: varchar(200)
    desc: 发起人姓名
    topk: 刘倍材|刘宁|刘宁2|周录彬zhoulubin
```
