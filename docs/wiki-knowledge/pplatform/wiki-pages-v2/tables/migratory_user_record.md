---
type: table
title: 迁移用户记录表
page_key: migratory_user_record
domain: 租户迁移
status: draft
anchors: [migratory_user_record]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












本表是"迁移存量用户是否已登录过产融"的判定载体，服务于迁移期 [[migratory_user_first_login]] 的一次性升级提示。记录在迁移落库时创建（`is_login="N"`），登录后由 `/cust-web/migratory/isEjectMsg` 翻转，状态机见 [[migratory_user_login_prompt]]。注意 `user_id` 存的是产融用户ID（FBP），不是 `sys_user` 主键的直接引用。

```ground:table
table: migratory_user_record
database: lowcode_pplatform
desc: 迁移用户记录表
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
  - name: is_login
    type: string
    phys: varchar(512)
    desc: 是否登录过
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
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
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
    desc: 迁移用户id
```

## 关联表

- [[cust_person_info]]：migratory_user_record.user_id → cust_person_info.user_id（copy:PlatFormMigratoryApplication.java，suggested）
## 需求背景

存量用户首次登录（当前迁移批次内）需弹出『【贴牌名称】平台已升级，新增【产品中心】，期待为您提供更好的服务』，且一个用户仅弹一次。产品侧据此要求：迁移落库时就必须为每个迁移人员预置一条"未登录"记录，登录后置为已登录，作为"只弹一次"的唯一依据。

## 版本演进

落库时的 `is_login` 由硬编码 `"N"` 写入，暂无中间态；查询侧以 `user_id + db_tenant_code` 作为组合判定条件。相关规则：[[migratory_user_record_insert]]；口径：[[migratory_user_first_login]]。
