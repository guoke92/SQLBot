---
type: table
title: 异步导入导出任务
page_key: async_io_task
domain: 租户配置/灰度/运营邮件
status: draft
anchors: [async_io_task]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












异步导入导出任务表登记文件型异步作业的调度与结果信息，是租户侧批量导入导出（如运营配置批量回写）的落地载体。任务号由 MySQL 自增生成并由应用层用作分片调度键，状态列驱动 [[async_io_task_status]] 状态机，`file_url` 承载结果文件或错误文件的 COS object key。

读取与清理遵循 [[async_io_task_not_deleted]]、[[async_io_task_pending]] 与 [[async_io_task_running]] 三个口径；IMPORT 登记时刻意不写用户上传源文件路径，避免下载链路把源文件当成结果文件返回。

## 需求背景
批量导入导出耗时较长，需要异步化并可在文件管理中查询进度、下载结果与错误文件；节点强杀或 OOM 后停留在 RUNNING 的任务需要能被超时兜底清理为失败，避免任务长期悬挂。

## 版本演进
v0.1（本页）：首版契约，仅覆盖语义分析中有证据的 4 个字段；字段物理类型未采集，暂记 `unknown`。

```ground:table
table: async_io_task
database: lowcode_pplatform
desc: 异步导入导出任务
fields:
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
  - name: is_deleted
    type: string
    phys: varchar(1)
    desc: 软删除：0 否 1 是
    dict: is_deleted
    topk: "0|1"
    labels: "0:否|1:是"
  - name: status
    type: string
    phys: varchar(16)
    desc: 状态
    dict: async_io_task__status
    topk: "FAILED|RUNNING|SUCCESS"
  - name: task_type
    type: string
    phys: varchar(32)
    desc: 任务类型
    dict: task_type
    topk: "EXPORT|IMPORT"
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
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: ctx_json
    type: string
    phys: text
    desc: 上下文：userId/custId/companyType/dbTenantCode 等
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "all"
  - name: end_time
    type: temporal
    phys: datetime
    desc: 任务结束时间
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
    desc: 成功:结果文件 / 失败:错误文件 的下载地址
  - name: menu_code
    type: string
    phys: varchar(64)
    desc: 业务菜单标识
    topk: "CUST_INPUT_BATCH|CUST_PROJECT_REL_BATCH|PROJECT_REPORT_STATISTICS|TENANT_PROJECT_CONFIG|WECHAT_PROJECT_APPROVAL"
  - name: menu_name
    type: string
    phys: varchar(200)
    desc: 业务菜单名称
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
  - name: task_name
    type: string
    phys: varchar(200)
    desc: 任务名称
  - name: task_no
    type: number
    phys: bigint(20)
    desc: 任务号
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
  - name: user_id
    type: number
    phys: bigint(20)
    desc: 用户ID
  - name: user_name
    type: string
    phys: varchar(200)
    desc: 发起人姓名
```