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
contract_version: "0.3"
belong: tables
scenes: [tenant_config]
---

# 异步导入导出任务

用户文件任务。状态名为枚举名 PENDING/RUNNING/SUCCESS/FAILED，没有中文 displayName。`is_deleted` 为 `'0'`/`'1'`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[tenant_config]]

`id`, `enable`, `create_time`, `update_time`, `is_deleted`, `status`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `biz_args_json`, `biz_class`, `biz_method`, `ctx_json`, `db_tenant_code`, `end_time`, `error_msg`, `file_name`, `file_url`, `menu_code`, `menu_name`, `name`, `organization_id`, `remark`, `result_text`, `start_time`, `task_name`, `task_no`, `task_type`, `user_id`, `user_name`

```ground:table
table: async_io_task
database: lowcode_pplatform
desc: 异步导入导出任务
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [tenant_config]
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
    scenes: [tenant_config]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [tenant_config]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [tenant_config]
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
  - name: is_deleted
    type: string
    phys: varchar(1)
    desc: "软删"
    topk: "0|1"
    labels: "0:否|1:是"
    scenes: [tenant_config]
  - name: status
    type: string
    phys: varchar(16)
    desc: "状态"
    dict: async_io_status
    topk: "FAILED|RUNNING|SUCCESS"
    roles: [query]
    scenes: [tenant_config]
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
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "base"
  - name: biz_args_json
    type: string
    phys: text
    desc: "参数 JSON"
  - name: biz_class
    type: string
    phys: varchar(264)
    desc: "Controller Bean 全限定名"
  - name: biz_method
    type: string
    phys: varchar(512)
    desc: "方法签名 name(paramTypes)"
  - name: ctx_json
    type: string
    phys: text
    desc: "上下文：userId/custId/companyType/dbTenantCode 等"
    labels: "dbTenantCode:等"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "all"
  - name: end_time
    type: temporal
    phys: datetime
    desc: "任务结束时间"
  - name: error_msg
    type: string
    phys: text
    desc: "失败原因"
  - name: file_name
    type: string
    phys: varchar(300)
    desc: "文件名"
  - name: file_url
    type: string
    phys: varchar(1000)
    desc: "成功:结果文件 / 失败:错误文件 的下载地址"
  - name: menu_code
    type: string
    phys: varchar(64)
    desc: "业务菜单标识"
    topk: "CUST_INPUT_BATCH|CUST_PROJECT_REL_BATCH|PROJECT_REPORT_STATISTICS|TENANT_PROJECT_CONFIG|WECHAT_PROJECT_APPROVAL"
  - name: menu_name
    type: string
    phys: varchar(200)
    desc: "业务菜单名称"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: result_text
    type: string
    phys: text
    desc: "业务返回"
  - name: start_time
    type: temporal
    phys: datetime
    desc: "任务开始时间"
  - name: task_name
    type: string
    phys: varchar(200)
    desc: "任务名称"
  - name: task_no
    type: number
    phys: bigint(20)
    desc: "任务号"
  - name: task_type
    type: string
    phys: varchar(32)
    desc: "任务类型"
    topk: "EXPORT|IMPORT"
  - name: user_id
    type: number
    phys: bigint(20)
    desc: "用户ID"
  - name: user_name
    type: string
    phys: varchar(200)
    desc: "发起人姓名"
```
