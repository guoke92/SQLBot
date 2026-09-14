---
type: table
title: CFCA证书升级业务上报与触达记录
page_key: ca_cfca_upgrade_report
domain: CA证书认证
status: draft
anchors: [ca_cfca_upgrade_report]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












ca_cfca_upgrade_report 记录 [[ca_upgrade_auth|CA 升级授权书]] 的出具情况：谁是被授权人、企业以什么角色出具、影像来自哪个来源系统、由哪个业务模块触发、是否已经触发待办/消息。它与 [[ca_certification_info]] 的 file_refs_json 是"业务实体"与"附件引用"的关系——授权书的文件路径最终落在 ca_certification_info.file_refs_json 的 embeddedFiles 里（serviceKey=CaUpgradeAuth），本表记录的是授权书这笔业务事实本身。

使用本表时有两点必须注意：company_type 是企业角色枚举（CORE/SUPPLIER/FINANCE/PLATFORM_COMPANY 等），不是客户类型；biz_module 在存量数据中存在 CFCA_CA_UPGRADE 与中文「CFCA证书升级」两种写法，做维度汇总时需先归一。

## 需求背景

升级授权书在运营侧存在多个影像来源系统（ACFLOW/RVSFACTOR_PC/ORDER/国内信用证），本表的 source_system 即用于区分；todo_triggered 用于标识是否已推动待办/消息。授权书盖章的前置条件与 [[non_build_success_no_ca]] 中描述的建档状态要求相关（要求 cust_build_status in (BUILD_SUCCESS, CUST_CHANGE)）。

## 版本演进

- v0：首次沉淀本表语义。biz_module 的中英双写法属历史遗留，尚未统一。

```ground:table
table: ca_cfca_upgrade_report
database: lowcode_pplatform
desc: CFCA证书升级业务上报与触达记录
fields:
  - name: company_type
    type: string
    phys: varchar(128)
    desc: 企业角色
    dict: ca_cfca_upgrade_report__company_type
    topk: "CORE|FINANCE|PLATFORM_COMPANY|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER"
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
  - name: todo_triggered
    type: string
    phys: varchar(2)
    desc: 是否曾触发待办/消息 Y/N
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
  - name: authorized_user_id
    type: number
    phys: bigint(20)
    desc: 被授权人用户 ID
  - name: authorized_user_name
    type: string
    phys: varchar(512)
    desc: 被授权人姓名
    topk: "何云|佘雨代|利胜健|吴志勇|张辉|徐玉梅|李坤|梁玉兰|洪俊俊|王曼黎|王鑫|花鸣强|蔡淑华|诸婧芙|赵大成|辛吉熙|陈波|陈淑华|黄岩|齐素"
  - name: biz_module
    type: string
    phys: varchar(128)
    desc: 所属模块
    topk: "CFCA_CA_UPGRADE|CFCA证书升级"
  - name: certification_no
    type: string
    phys: varchar(128)
    desc: 统码
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_id
    type: string
    phys: varchar(128)
    desc: 企业 ID
  - name: content
    type: string
    phys: text
    desc: 异常内容（单层 JSON）
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
  - name: customer_name
    type: string
    phys: varchar(512)
    desc: 企业/客户名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "LN1|beehive-scf.qhhrly.cn|sdhsg.beehive-scf.qhhrly.cn"
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: notify_time
    type: temporal
    phys: datetime
    desc: 触发时间
  - name: occur_time
    type: temporal
    phys: datetime
    desc: 异常发生时间
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: pass_info
    type: string
    phys: text
    desc: 透传 JSON
  - name: related_biz_no
    type: string
    phys: varchar(128)
    desc: 关联业务编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: source_system
    type: string
    phys: varchar(128)
    desc: 来源系统
  - name: task_id
    type: string
    phys: varchar(64)
    desc: 业务系统任务ID
  - name: title
    type: string
    phys: varchar(512)
    desc: 异常标题
  - name: trigger_scene
    type: string
    phys: varchar(128)
    desc: 触发场景
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

关联页面：[[ca_upgrade_auth]]、[[ca_certification_info]]、[[authorized_person]]、[[non_build_success_no_ca]]。