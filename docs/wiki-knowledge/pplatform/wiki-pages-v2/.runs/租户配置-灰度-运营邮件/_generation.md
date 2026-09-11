---FILE: tables/tenant_setting_config.md---
---
type: table
title: tenant_setting_config（租户配置表）
page_key: table.tenant_setting_config
domain: 租户配置
status: draft
aliases:
  - tenant_setting_config
  - 租户配置表
  - 租户设置配置
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java
contract_version: "0.1"
---

tenant_setting_config 是租户维度的配置主表：一行代表一个「数据库租户」，承载租户的启用与生效状态、背景灰度颜色、项目码与默认项目约束、租户级运营人员与运营邮件触达配置、平台运营方、租户来源以及共享/主定制归属等运营配置。它是多租户隔离与租户查询的入口，几乎所有租户侧查询都以本表的 [[concepts/db_tenant_code]] 为主键、并以 `enable='Y'` 作为统一过滤条件（见 [[calibers/enabled_tenant]]）。

## 需求背景

产融侧需要为每个租户维护一套独立的运营配置，并在租户初始化时把项目级英文标识 [[concepts/tenant_flg_en]] 写为 `dbTenantCode`。随着共享（假租户）场景出现，同一个 `db_tenant_code` 下可以存在多个 `tenant_flg_en`，于是需要用 `share_flag` 判定，并把共享租户的配置写入 `tenant_setting_config_share`（见 [[calibers/shared_fake_tenant]]）。租户从「待生效」到「已生效」需要经过必填项校验，见 [[processes/tenant_status_effective]]；背景色则承载灰度窗口语义，见 [[processes/bg_color_gray]] 与 [[processes/global_bg_gray_switch]]。

## 版本演进

v0.1：依据当前语义分析快照（DB 取值分布 + 代码引用）建立字段语义基线，未包含字段新增/废弃的时间线。

```yaml
table: tenant_setting_config
fields:
  - name: db_tenant_code
    meaning: 数据租户标识/数据库租户编码，租户查询与多租户隔离的主键（唯一键 UNI）
    evidence: db
  - name: tenant_flg_en
    meaning: 项目标识（英文），租户在产融侧的项目级英文标识；初始化时被写为 dbTenantCode
    evidence: code
  - name: enable
    meaning: 启用标记，查询统一以 enable='Y' 过滤（存量全部为 Y）
    evidence: db
  - name: status
    meaning: 生效状态：Y=已生效，N=待生效（未生效占多数）
    evidence: db
  - name: bg_color
    meaning: 背景颜色：L=彩色（ColorConstants.LIGHT）、G=灰色（ColorConstants.GRAY）、null=未设置
    evidence: db
  - name: project_code_required
    meaning: 项目码是否必填 Y/N，为 Y 时要求同时配置 default_project_id
    evidence: code
  - name: default_project_id
    meaning: 默认关联项目ID，指向 tenant_project.id
    evidence: code
  - name: share_flag
    meaning: 租户共享标识，用于联易融自营「假租户」（同 dbTenantCode 多 tenantFlgEn）判定
    evidence: code
  - name: pushing_status
    meaning: 租户推送状态，非 CREATED 事件推送的前置开关（Y 表示已推过创建）
    evidence: code
  - name: op_update_user
    meaning: 租户运营配置更新人（独立于标准 update_user 记录）
    evidence: code
  - name: op_update_time
    meaning: 租户运营配置更新时间
    evidence: code
  - name: operator_id
    meaning: 租户级运营人员ID
    evidence: code
  - name: operator_name
    meaning: 租户级运营人员名称
    evidence: code
  - name: operator_email
    meaning: 租户级运营人员邮箱（运营邮件收件人）
    evidence: code
  - name: send_email
    meaning: 是否发送邮件（运营邮件触达开关）
    evidence: code
  - name: operator_ai_customer
    meaning: 是否开启智能客服，取值 '0'/'1'
    evidence: db
  - name: customer_card_type
    meaning: 客服名片类型：WX=微信名片，WX_WORK=企微名片
    evidence: db
  - name: platform_operator
    meaning: 平台运营方配置，JSON 数组，元素取值 platform / tenant
    evidence: db
  - name: source
    meaning: 租户来源，实测值 ACFLOW / pplatform
    evidence: db
  - name: is_stack
    meaning: 是否存量数据 Y/N
    evidence: db
  - name: main_tenant_flg_en
    meaning: 主定制项目标识（共享/主定制租户归属）
    evidence: db
  - name: access_mode
    meaning: 接入模式，实测值 DIRECT_INIT
    evidence: db
  - name: uni_social_credit_code
    meaning: 统一社会信用证编码，SSO/DBAss 初始化与保存校验的必填/合法性字段
    evidence: code
  - name: generate_electronic_auth_flag
    meaning: 是否生成电子版授权书：Y/N
    evidence: db
  - name: ai_resource_color
    meaning: 智能客服按钮颜色（颜色值字符串）
    evidence: db
```

相关页面：[[concepts/db_tenant_code]]、[[concepts/tenant_flg_en]]、[[concepts/enable]]、[[concepts/bg_color]]、[[concepts/tenant_operator]]、[[concepts/platform_operator]]、[[concepts/tenant_source]]、[[calibers/enabled_tenant]]、[[calibers/effective_tenant]]、[[calibers/lls_self_tenant]]、[[calibers/project_code_required_tenant]]、[[calibers/platform_operator_configured]]、[[rules/project_code_required_default_project]]。
---END FILE---

---FILE: tables/async_io_task.md---
---
type: table
title: async_io_task（异步导入导出任务表）
page_key: table.async_io_task
domain: 租户配置
status: draft
aliases:
  - async_io_task
  - 异步任务表
  - 导入导出任务表
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
sources:
  - db:async_io_task
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/job/AsyncIoTaskXxlJobHandler.java
contract_version: "0.1"
---

async_io_task 记录异步导入/导出任务的执行载体与结果产物，是租户侧批量数据操作（导入配置、导出清单等）的统一任务台账。任务通过 XXL-Job 分片广播被拉取执行，拉取口径见 [[calibers/pending_task_shard]]；任务状态机见 [[processes/async_io_task_status]]。`file_url` 的语义随状态变化：成功时是结果文件下载地址，失败时是错误文件下载地址。软删除使用字符串 `0/1`，见 [[concepts/is_deleted]]。

## 需求背景

大文件导入导出不能在同步请求内完成，因此引入任务表 + 调度器模式：调度抢到任务后以 CAS 方式置为 RUNNING，执行结束后按结果写 SUCCESS 或 FAILED，并回填结果文件地址或结果 JSON。导入部分失败时业务仍正常返回，但任务被判定为 FAILED，以便运营重试。

## 版本演进

v0.1：依据当前语义分析快照（代码枚举 + DB 取值分布）建立字段语义基线。

```yaml
table: async_io_task
fields:
  - name: status
    meaning: 异步导入导出任务状态，代码枚举 PENDING/RUNNING/SUCCESS/FAILED，实测含 SUCCESS/RUNNING/FAILED
    evidence: code
  - name: task_type
    meaning: 任务类型 IMPORT/EXPORT
    evidence: code
  - name: is_deleted
    meaning: 软删除标记：0=否 1=是
    evidence: code
  - name: file_url
    meaning: 成功=结果文件下载地址；失败=错误文件下载地址
    evidence: code
  - name: task_no
    meaning: 任务号，DB 自增，用于分片 MOD(task_no, shardTotal)=shardIndex
    evidence: code
```

相关页面：[[processes/async_io_task_status]]、[[calibers/not_deleted_async_task]]、[[calibers/pending_task_shard]]、[[concepts/is_deleted]]。
---END FILE---

---FILE: tables/tenant_project.md---
---
type: table
title: tenant_project（租户项目表）
page_key: table.tenant_project
domain: 租户配置
status: draft
aliases:
  - tenant_project
  - 租户项目表
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_project
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
contract_version: "0.1"
---

tenant_project 是租户下的项目维度档案，持有项目的各类对接人（运营、查验、风控、方案经理、业务经理）、项目级运营邮件配置与项目状态。它是 [[tables/tenant_setting_config]] 中 `default_project_id` 的指向对象，也是 [[concepts/op_contact_a]] 等对接人术语的落点。`top_flag=1` 表示项目上存在离职运营人员需要关注，前端会实时生成提示文本。

## 需求背景

租户配置需要按项目区分运营职责：不同项目配置不同的运营/风控/查验对接人，并决定该项目是否发送运营邮件。项目级运营邮件配置与租户级 [[concepts/tenant_operator]] 是不同层级，二者共同决定运营邮件的触达对象。

## 版本演进

v0.1：依据当前语义分析快照（代码引用）建立字段语义基线。

```yaml
table: tenant_project
fields:
  - name: top_flag
    meaning: 置顶标识，0/1，1 表示存在离职运营人员需关注
    evidence: code
  - name: text
    meaning: 备注/离职提示文本，前端 topFlag=1 时实时生成
    evidence: code
  - name: op_contact_a
    meaning: 运营对接人A（单个运营人员ID）
    evidence: code
  - name: op_contact_b
    meaning: 运营对接人B（多个运营人员ID）
    evidence: code
  - name: verification_contact
    meaning: 查验对接人
    evidence: code
  - name: risk_control_contact_a
    meaning: 风控对接人A
    evidence: code
  - name: risk_control_contact_b
    meaning: 风控对接人B
    evidence: code
  - name: solution_manager
    meaning: 方案经理
    evidence: code
  - name: business_manager
    meaning: 业务经理
    evidence: code
  - name: business_group
    meaning: 关联业务部门
    evidence: code
  - name: send_email
    meaning: 项目级是否发送运营邮件
    evidence: code
  - name: operator_email
    meaning: 项目级运营对接人邮箱
    evidence: code
  - name: project_status
    meaning: 项目状态，生效值由 ProjectStatusEnum.EFFECTIVE 判定
    evidence: code
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/op_contact_a]]、[[concepts/tenant_operator]]。
---END FILE---

---FILE: tables/cust_person_info.md---
---
type: table
title: cust_person_info（企业联系人表）
page_key: table.cust_person_info
domain: 租户配置
status: draft
aliases:
  - cust_person_info
  - 企业联系人表
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
sources:
  - db:cust_person_info
  - code:lowcode-pplatform-customer-management
contract_version: "0.1"
---

cust_person_info 记录企业联系人的基本信息。本页只覆盖与运营配置相关的字段：联系人上挂载的运营人 ID、姓名与账号。它代表「企业联系人级」的运营人归属，与租户级 [[concepts/tenant_operator]]（`tenant_setting_config.operator_*`）和项目级 [[concepts/op_contact_a]]（`tenant_project.op_contact_*`）分属三个不同层级，不可互换。

## 需求背景

同一家企业联系人可能由特定运营人员负责，需要在联系人维度上冗余运营人信息，便于按联系人追溯运营归属；该冗余与租户级、项目级运营人配置各自独立维护。

## 版本演进

v0.1：依据当前语义分析快照（代码引用）建立字段语义基线。

```yaml
table: cust_person_info
fields:
  - name: operator_id
    meaning: 联系人上的运营人ID（企业联系人级，区别于租户级 operator_id）
    evidence: code
  - name: operator_realname
    meaning: 联系人上的运营人姓名
    evidence: code
  - name: operator
    meaning: 联系人上的运营人账号（userName）
    evidence: code
```

相关页面：[[concepts/tenant_operator]]、[[concepts/op_contact_a]]。
---END FILE---

---FILE: processes/tenant_status_effective.md---
---
type: process
title: 租户生效状态（tenant_setting_config.status）
page_key: process.tenant_status_effective
domain: 租户配置
status: draft
aliases:
  - 租户生效状态
  - 待生效转已生效
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.status
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:effective
contract_version: "0.1"
---

租户配置的「生效」是一条单向人工推进的状态：新租户落在 `N`（待生效/未生效，存量中占多数），只有 `effective` 的必填项校验全部通过后才置为 `Y`。是否算作「生效租户」需要 `status='Y'` 与 `enable='Y'` 两个条件并列，见 [[calibers/effective_tenant]]；其中的必填项之一即项目码与默认项目的联动，见 [[rules/project_code_required_default_project]]。

## 需求背景

租户创建时往往缺少统一社会信用证编码、默认项目、平台运营方企业等前置信息，因此不能立即对外提供服务，需要「待生效」态承接配置补全，再由运营触发生效。生效门槛由校验项控制，避免未配置完整的租户进入可用列表。

## 版本演进

v0.1：登记当前代码中的状态取值与唯一一条 N→Y 迁移（必填项校验通过）。

```yaml
state_machine: 租户生效状态
field: tenant_setting_config.status
states:
  - value: "N"
    label: 待生效/未生效
    source: db_dist
  - value: "Y"
    label: 已生效
    source: db_dist
transitions:
  - from: "N"
    event: effective 必填项校验全部通过
    to: "Y"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:effective"
```

相关页面：[[tables/tenant_setting_config]]、[[calibers/effective_tenant]]、[[rules/project_code_required_default_project]]。
---END FILE---

---FILE: processes/bg_color_gray.md---
---
type: process
title: 租户背景颜色/灰度（tenant_setting_config.bg_color）
page_key: process.bg_color_gray
domain: 租户配置
status: draft
aliases:
  - 背景颜色状态
  - 灰度状态
  - bgColor
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.bg_color
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorGray
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorNull
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:setColorlight
contract_version: "0.1"
---

租户端的背景色由 `bg_color` 单一字段表达三种取值：`L`（彩色）、`G`（灰色）、`null`（未设置，按彩色处理）。灰度是全局窗口行为：当全局灰度窗口生效时，已设彩色的租户被打成灰色、未设颜色的租户也按灰色展示；客户端主动恢复彩色时字段回到 `null`，运营显式设为彩色时写入 `L`。全局窗口本身的状态见 [[processes/global_bg_gray_switch]]，灰色租户的筛选口径见 [[calibers/gray_bg_tenant]]。

## 需求背景

需要在不改主题色、不改智能客服按钮色的前提下，对全量租户做临时性灰度（如纪念日），因此把灰度语义单独收敛到 `bg_color` 上，避免与 `main_theme_color`、`ai_resource_color` 混淆。

## 版本演进

v0.1：登记当前代码中可达的取值与四条颜色迁移路径。

```yaml
state_machine: 租户背景颜色/灰度
field: tenant_setting_config.bg_color
states:
  - value: "L"
    label: 彩色
    source: code_enum
  - value: "G"
    label: 灰色
    source: code_enum
  - value: "null"
    label: 未设置（按彩色处理）
    source: db_dist
transitions:
  - from: "null"
    event: 全局灰度窗口生效且租户未设颜色
    to: "G"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorGray"
  - from: "L"
    event: 全局灰度窗口生效
    to: "G"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorGray"
  - from: "G"
    event: 客户端恢复彩色(bgcolor/reset/light)
    to: "null"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorNull"
  - from: "null"
    event: setColorlight 设为彩色
    to: "L"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:setColorlight"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/bg_color]]、[[concepts/gray_background]]、[[processes/global_bg_gray_switch]]、[[calibers/gray_bg_tenant]]。
---END FILE---

---FILE: processes/global_bg_gray_switch.md---
---
type: process
title: 全局背景灰度开关（Redis 缓存 BgColorCacheDto）
page_key: process.global_bg_gray_switch
domain: 租户配置
status: draft
aliases:
  - 全局灰度开关
  - BGCOLOR_SWITCH
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:setBgColor
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:getBgColor
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:bgColorClear
contract_version: "0.1"
---

全局灰度窗口不落库，而是以 `RedisKeyConstants.BGCOLOR_SWITCH_TTL` 对应的 `BgColorCacheDto` 缓存承载，缓存内记录 `startDate~endDate`。写入窗口即进入 ON；读取时若 `now` 超过 `endTime` 即判定过期，等效 OFF；调用清理接口直接删除缓存回到 OFF。该开关驱动 [[processes/bg_color_gray]] 中租户颜色的变更。

## 需求背景

灰度窗口需要秒级生效、按时自动失效，且不应为每个租户写库，因此以带 TTL 的缓存作为开关源，读取侧再做一次时间判定，兼顾「未到时间不生效」和「过期即失效」。

## 版本演进

v0.1：登记当前代码中三个入口（写入、读取判定、清理）构成的开关状态。

```yaml
state_machine: 全局背景灰度开关（Redis 缓存）
field: RedisKeyConstants.BGCOLOR_SWITCH_TTL(BgColorCacheDto)
states:
  - value: "ON"
    label: 灰度窗口生效中
    source: code_enum
  - value: "OFF"
    label: 灰度窗口未生效/已过期
    source: code_enum
transitions:
  - from: "OFF"
    event: bgcolor/set 写入 startDate~endDate
    to: "ON"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:setBgColor"
  - from: "ON"
    event: now 超出 endTime（读取时判定过期）
    to: "OFF"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:getBgColor"
  - from: "ON"
    event: bgcolor/reset/light 删除缓存
    to: "OFF"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:bgColorClear"
```

相关页面：[[processes/bg_color_gray]]、[[concepts/bg_color]]、[[calibers/gray_bg_tenant]]。
---END FILE---

---FILE: processes/async_io_task_status.md---
---
type: process
title: 异步导入导出任务状态（async_io_task.status）
page_key: process.async_io_task_status
domain: 租户配置
status: draft
aliases:
  - 异步任务状态
  - 导入导出任务状态
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/job/AsyncIoTaskXxlJobHandler.java:handleNonStreamResult
contract_version: "0.1"
---

任务从 PENDING 开始，由 XXL-Job 分片抢单（见 [[calibers/pending_task_shard]]）后以 CAS 置为 RUNNING，随后分化多条终态路径：正常成功写 SUCCESS 并回填结果文件或结果 JSON；抛异常、导入部分失败、或超过 `timeoutMinutes` 被超时清理，都落 FAILED。FAILED 的 `file_url` 语义是错误文件下载地址，SUCCESS 则是结果文件地址。

## 需求背景

导入部分失败时业务代码可能正常返回，但运营侧需要明确感知失败并拿到错误行文件，因此把「含失败行」也判定为 FAILED；同时为防止任务卡死在 RUNNING，引入超时清理路径将其收敛到 FAILED。

## 版本演进

v0.1：登记当前代码枚举中的四个状态与六条迁移路径。

```yaml
state_machine: 异步导入导出任务状态
field: async_io_task.status
states:
  - value: "PENDING"
    label: 待执行
    source: code_enum
  - value: "RUNNING"
    label: 执行中
    source: code_enum
  - value: "SUCCESS"
    label: 成功
    source: code_enum
  - value: "FAILED"
    label: 失败
    source: code_enum
transitions:
  - from: "PENDING"
    event: 调度抢到任务 markRunning(CAS)
    to: "RUNNING"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markRunning"
  - from: "RUNNING"
    event: 执行成功（下载流/结果落库）
    to: "SUCCESS"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markSuccessWithFile"
  - from: "RUNNING"
    event: 执行成功（结果 JSON）
    to: "SUCCESS"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markSuccessWithResult"
  - from: "RUNNING"
    event: 执行抛异常
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markFailed"
  - from: "RUNNING"
    event: 导入部分失败（业务正常返回但含失败行）
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/job/AsyncIoTaskXxlJobHandler.java:handleNonStreamResult"
  - from: "RUNNING"
    event: 超时清理（超过 timeoutMinutes）
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markRunningTimeout"
```

相关页面：[[tables/async_io_task]]、[[calibers/pending_task_shard]]、[[calibers/not_deleted_async_task]]、[[concepts/is_deleted]]。
---END FILE---

---FILE: processes/tenant_pushing_status.md---
---
type: process
title: 租户推送状态（tenant_setting_config.pushing_status）
page_key: process.tenant_pushing_status
domain: 租户配置
status: draft
aliases:
  - 租户推送状态
  - pushingStatus
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.pushing_status
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:pushing
contract_version: "0.1"
---

`pushing_status` 是租户推送的前置开关：推送 CREATED 类型以外的租户事件之前，会先校验该字段是否已置 `Y`，从而保证「创建事件先于其他事件」的顺序约束。当前证据中只观测到 `Y`（已推送创建事件）一个取值，未推送一侧的显式取值未在证据中给出。

## 需求背景

租户事件存在顺序依赖：更新、生效等事件只有在创建事件成功推送后才有意义。用一个可由数据库直接判定的状态位替代跨系统查询，成本更低且可重放。

## 版本演进

v0.1：登记当前唯一有证据的取值与迁移路径。

```yaml
state_machine: 租户推送状态
field: tenant_setting_config.pushing_status
states:
  - value: "Y"
    label: 已推送创建事件
    source: code_enum
transitions:
  - from: "null"
    event: 推送 CREATED 租户事件前
    to: "Y"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:pushing"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/tenant_source]]。
---END FILE---

---FILE: calibers/enabled_tenant.md---
---
type: caliber
title: 启用租户
page_key: caliber.enabled_tenant
domain: 租户配置
status: draft
aliases:
  - 启用租户
  - enable='Y' 租户
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.enable
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
contract_version: "0.1"
---

「启用租户」是所有租户查询的默认底座口径：`getFirstByDbTenantCode`、`getById`、`listActicveAll` 等入口都在 SQL 上拼接 `enable='Y'`。注意它与「生效」不是同一件事——`enable` 是记录启用态（存量数据实测全部为 Y），`status` 才是租户业务生效态，见 [[calibers/effective_tenant]]。

## 需求背景

租户记录存在停用需求，但历史数据几乎都是启用态，因此把 `enable` 固化为查询常量条件，避免各入口遗漏造成已停用租户被读取。

## 版本演进

v0.1：依据代码中统一过滤条件与 DB 实测分布（全为 Y）建立口径。

```yaml
caliber: 启用租户
predicate: "tenant_setting_config.enable = 'Y'"
scope: 所有租户查询（getFirstByDbTenantCode / getById / listActicveAll 等）
evidence: db + code:TenantDomainService.java
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/enable]]、[[calibers/effective_tenant]]。
---END FILE---

---FILE: calibers/effective_tenant.md---
---
type: caliber
title: 已生效租户
page_key: caliber.effective_tenant
domain: 租户配置
status: draft
aliases:
  - 已生效租户
  - activeList
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.status
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:listActicveAll
contract_version: "0.1"
---

「已生效租户」= `status='Y'` 且 `enable='Y'`，用在生效租户列表（activeList）与租户生效校验上。由于 `status='N'`（待生效）在存量中占多数，漏写任一条件都会显著改变结果集，因此本口径必须两条件并列，不能退化为 [[calibers/enabled_tenant]]。

## 需求背景

租户从待生效到已生效是人工推进的过程（见 [[processes/tenant_status_effective]]），下游只应消费已生效租户，因此需要一个可直接下推到 SQL 的组合口径。

## 版本演进

v0.1：依据 `listActicveAll` 的查询条件建立口径。

```yaml
caliber: 已生效租户
predicate: "tenant_setting_config.status = 'Y' AND tenant_setting_config.enable = 'Y'"
scope: activeList 生效租户列表 / 租户生效校验
evidence: "code:TenantDomainService.java:listActicveAll"
```

相关页面：[[tables/tenant_setting_config]]、[[processes/tenant_status_effective]]、[[calibers/enabled_tenant]]、[[concepts/enable]]。
---END FILE---

---FILE: calibers/gray_bg_tenant.md---
---
type: caliber
title: 灰色背景租户
page_key: caliber.gray_bg_tenant
domain: 租户配置
status: draft
aliases:
  - 灰色背景租户
  - G 灰度租户
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.bg_color
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:getTentantColorSet
contract_version: "0.1"
---

客户端读取背景色时，以 `bg_color='G'` 识别灰色租户；该口径的生效前提是全局灰度窗口处于 ON（见 [[processes/global_bg_gray_switch]]）。注意 `bg_color` 为 `null` 的租户在窗口内也会被处理成灰色，但库内取值仍是 null，因此本口径只覆盖「已显式置灰」的租户。

## 需求背景

灰度窗口期间需要批量把彩色租户翻成灰色，并保留客户端可单方面恢复彩色的能力，因此「灰色」既可能来自库内取值也可能来自窗口计算，查询口径需要明确区分。

## 版本演进

v0.1：依据 `getTentantColorSet` 与 `bg_color` 取值分布建立口径。

```yaml
caliber: 灰色背景租户
predicate: "tenant_setting_config.bg_color = 'G'"
scope: 客户端背景色展示（灰度窗口内）
evidence: "code:TenantAppliactionService.java:getTentantColorSet"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/bg_color]]、[[concepts/gray_background]]、[[processes/bg_color_gray]]、[[processes/global_bg_gray_switch]]。
---END FILE---

---FILE: calibers/stack_tenant_data.md---
---
type: caliber
title: 存量租户数据
page_key: caliber.stack_tenant_data
domain: 租户配置
status: draft
aliases:
  - 存量租户
  - isStack
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.is_stack
contract_version: "0.1"
---

以 `is_stack='Y'` 标记从历史系统迁移或早期即存在的租户数据，用于区分租户数据的来源批次。该口径常用于判断某租户是否受历史行为约束（例如背景色/灰度、生效流程的差异化处理）。当前证据仅给出该取值的存在，未展开具体分支逻辑。

## 需求背景

租户存在存量与新增两类来源，部分运营配置在存量租户上需要特殊处理，因此需要一个可查询的数据来源标记。

## 版本演进

v0.1：依据 DB 取值分布建立口径。

```yaml
caliber: 存量租户数据
predicate: "tenant_setting_config.is_stack = 'Y'"
scope: 租户数据来源区分
evidence: db
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/tenant_source]]。
---END FILE---

---FILE: calibers/lls_self_tenant.md---
---
type: caliber
title: 联易融自营租户
page_key: caliber.lls_self_tenant
domain: 租户配置
status: draft
aliases:
  - 联易融自营租户
  - isLlsTenant
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:isLlsTenant
contract_version: "0.1"
---

自营租户由两个可配置常量界定：`db_tenant_code` 等于平台租户配置值，或 `tenant_flg_en` 等于联易融租户标识值。该口径是 SSO/DBAss 初始化的前置判断——非自营租户才执行初始化流程。判定依据同时落在 [[concepts/db_tenant_code]] 与 [[concepts/tenant_flg_en]] 两个术语上，体现了两字段在业务上的分叉。

## 需求背景

联易融自营租户由内部系统对接，不需要走外部租户的 SSO/DBAss 初始化，因此需要在初始化前把这类租户识别出来并短路。

## 版本演进

v0.1：依据 `isLlsTenant` 判定逻辑建立口径。

```yaml
caliber: 联易融自营租户
predicate: "tenant_setting_config.db_tenant_code = ${tenantProperties.platformTenantDbTenantCode} OR tenant_setting_config.tenant_flg_en = ${tenantProperties.llsTenantFlgEn}"
scope: 非自营租户才做 SSO/DBAss 初始化
evidence: "code:TenantAppliactionService.java:isLlsTenant"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/db_tenant_code]]、[[concepts/tenant_flg_en]]、[[calibers/shared_fake_tenant]]。
---END FILE---

---FILE: calibers/shared_fake_tenant.md---
---
type: caliber
title: 共享假租户
page_key: caliber.shared_fake_tenant
domain: 租户配置
status: draft
aliases:
  - 假租户
  - 共享租户
  - existEarlyLLsTenant
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.share_flag
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:existEarlyLLsTenant
contract_version: "0.1"
---

共享假租户判定条件是 `share_flag='Y'` 且本次请求的 `tenant_flg_en` 与配置行不一致：此时 `syncTenant` 不写 `tenant_setting_config`，而改写 `tenant_setting_config_share`。该口径解释了为什么同一个 [[concepts/db_tenant_code]] 下可能存在多个 [[concepts/tenant_flg_en]]——共享租户复用同一数据租户，但以不同项目标识对外。

## 需求背景

同一数据库租户下要承载多个项目标识（品牌）的共享配置，若直接写主表会互相覆盖，因此引入独立的共享配置表与写入分支。

## 版本演进

v0.1：依据 `existEarlyLLsTenant` 与 `share_flag` 字段语义建立口径。

```yaml
caliber: 共享假租户
predicate: "tenant_setting_config.share_flag = 'Y' AND tenant_flg_en <> 请求 tenantFlgEn"
scope: syncTenant 时写入 tenant_setting_config_share 而非 tenant_setting_config
evidence: "code:TenantDomainService.java:existEarlyLLsTenant"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/db_tenant_code]]、[[concepts/tenant_flg_en]]、[[calibers/lls_self_tenant]]。
---END FILE---

---FILE: calibers/not_deleted_async_task.md---
---
type: caliber
title: 未删除异步任务
page_key: caliber.not_deleted_async_task
domain: 租户配置
status: draft
aliases:
  - 未删除任务
  - is_deleted='0'
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
sources:
  - db:async_io_task.is_deleted
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java
contract_version: "0.1"
---

任务分页、查询与软删除都以 `is_deleted='0'` 为未删除判定。该字段是字符串 `0/1`，既不是布尔值也不是 `Y/N`，因此调用方必须显式写字符串，见 [[concepts/is_deleted]] 与 [[processes/async_io_task_status]]。

## 需求背景

任务记录需要保留用于审计与结果文件回溯，因此采用软删除而非物理删除，查询侧统一追加未删除条件。

## 版本演进

v0.1：依据 `AsyncIoTaskManager` 中查询条件建立口径。

```yaml
caliber: 未删除异步任务
predicate: "async_io_task.is_deleted = '0'"
scope: 任务分页/查询/软删
evidence: "code:AsyncIoTaskManager.java"
```

相关页面：[[tables/async_io_task]]、[[concepts/is_deleted]]、[[calibers/pending_task_shard]]。
---END FILE---

---FILE: calibers/supplier_company.md---
---
type: caliber
title: 供应商企业
page_key: caliber.supplier_company
domain: 租户配置
status: draft
aliases:
  - 供应商企业
  - SUPPLIER
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/AssetOperatorSyncApplication.java:syncAssetOperator
contract_version: "0.1"
---

在企业类型为 `SUPPLIER` 的范围内，资产审核运营人员的同步才生效；非供应商企业不参与该同步。该口径限定运营人员同步的作用域，避免把审核运营人写到不相关的企业上。

## 需求背景

资产审核的运营人归属只对供应商企业有业务意义，因此同步任务在入口处按企业类型裁剪数据集。

## 版本演进

v0.1：依据 `syncAssetOperator` 的企业类型过滤建立口径。

```yaml
caliber: 供应商企业
predicate: "cust_company_info.cust_company_type = 'SUPPLIER'"
scope: 资产审核运营人员同步仅对供应商生效
evidence: "code:AssetOperatorSyncApplication.java:syncAssetOperator"
```

相关页面：[[concepts/tenant_operator]]、[[concepts/op_contact_a]]。
---END FILE---

---FILE: calibers/project_code_required_tenant.md---
---
type: caliber
title: 项目码必填租户
page_key: caliber.project_code_required_tenant
domain: 租户配置
status: draft
aliases:
  - 项目码必填租户
  - projectCodeRequired
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.project_code_required
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:checkBeforeSave
contract_version: "0.1"
---

`project_code_required='Y'` 的租户在保存前会进入更严格的校验分支：要求 `default_project_id` 非空，否则阻断保存（见 [[rules/project_code_required_default_project]]）。该口径与租户生效流程共同决定租户能否进入可用状态。

## 需求背景

部分租户以项目码作为业务主键，必须绑定默认项目才能创建业务单据，因此把「项目码必填」做成租户级开关而非全局规则。

## 版本演进

v0.1：依据 `checkBeforeSave` 的前置校验建立口径。

```yaml
caliber: 项目码必填租户
predicate: "tenant_setting_config.project_code_required = 'Y'"
scope: 保存前置校验要求 default_project_id 非空
evidence: "code:TenantDomainService.java:checkBeforeSave"
```

相关页面：[[tables/tenant_setting_config]]、[[rules/project_code_required_default_project]]、[[processes/tenant_status_effective]]。
---END FILE---

---FILE: calibers/platform_operator_configured.md---
---
type: caliber
title: 配置了平台运营方
page_key: caliber.platform_operator_configured
domain: 租户配置
status: draft
aliases:
  - 配置了平台运营方
  - platform_operator 含 platform
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.platform_operator
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/component/PlatformComponentFacade.java:needPlatformOperatorCompany
contract_version: "0.1"
---

`platform_operator` 是 JSON 数组，元素取值 `platform` / `tenant` 可组合。仅当数组包含 `platform` 时，租户生效校验才要求平台运营方企业存在；因此「配了运营方」与「需要运营方企业」不是等价条件，见 [[concepts/platform_operator]]。

## 需求背景

平台运营方与租户方运营方在业务上职责不同；只有涉及平台运营的租户才需要在生效时校验运营方企业主体，避免对纯租户方运营的租户施加无谓的前置条件。

## 版本演进

v0.1：依据 `needPlatformOperatorCompany` 判定建立口径。

```yaml
caliber: 配置了平台运营方
predicate: "tenant_setting_config.platform_operator 包含 'platform'"
scope: 租户生效必填校验是否需要校验平台运营方企业
evidence: "code:PlatformComponentFacade.java:needPlatformOperatorCompany"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/platform_operator]]、[[processes/tenant_status_effective]]。
---END FILE---

---FILE: calibers/pending_task_shard.md---
---
type: caliber
title: 待执行任务分片
page_key: caliber.pending_task_shard
domain: 租户配置
status: draft
aliases:
  - 待执行任务分片
  - listPendingByShard
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
sources:
  - db:async_io_task.task_no
  - db:async_io_task.status
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:listPendingByShard
contract_version: "0.1"
---

XXL-Job 分片广播拉取待执行任务时，用 `MOD(task_no, shardTotal) = shardIndex` 在分片间均分任务号，并叠加 `status='PENDING'` 与未删除条件。由于 `task_no` 是 DB 自增列，取模天然形成近似均匀分布，无需额外调度表。

## 需求背景

异步任务量随导入导出使用量增长，单机轮询会造成处理延迟；使用分片广播 + 取模可以让每个执行器实例只处理自己的一份任务，同时避免多实例重复抢占（抢占仍由 CAS 状态迁移兜底，见 [[processes/async_io_task_status]]）。

## 版本演进

v0.1：依据 `listPendingByShard` 的查询构造建立口径。

```yaml
caliber: 待执行任务分片
predicate: "async_io_task.status = 'PENDING' AND MOD(task_no, shardTotal) = shardIndex AND is_deleted <> '1'"
scope: XXL-Job 分片广播拉取
evidence: "code:AsyncIoTaskManager.java:listPendingByShard"
```

相关页面：[[tables/async_io_task]]、[[processes/async_io_task_status]]、[[calibers/not_deleted_async_task]]。
---END FILE---

---FILE: concepts/db_tenant_code.md---
---
type: concept
title: dbTenantCode
page_key: concept.db_tenant_code
domain: 租户配置
status: draft
aliases:
  - db_tenant_code
  - 数据租户标识
  - 数据库租户编码
  - 租户编码
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.db_tenant_code
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
contract_version: "0.1"
maps_to: tenant_setting_config.db_tenant_code
field_targets:
  - tenant_setting_config.db_tenant_code
adjudication: boundary
also_confused_with:
  - tenantFlgEn
---

`dbTenantCode` 是数据租户标识/数据库租户编码，承担多租户数据隔离主键职责，对应 [[tables/tenant_setting_config]] 的唯一键 `db_tenant_code`。与之最易混淆的是 [[concepts/tenant_flg_en]]：初始化时 `tenant_flg_en` 会被写成与 `dbTenantCode` 相等，但后续语义分叉——在共享假租户场景下，同一个 `db_tenant_code` 可以对应多个 `tenant_flg_en`（见 [[calibers/shared_fake_tenant]]）。因此二者不可互换使用：`dbTenantCode` 回答「数据属于哪个租户库域」，`tenantFlgEn` 回答「以哪个项目/品牌标识对外」。

## 需求背景

多租户隔离需要一个稳定、唯一的库级主键，租户侧几乎所有查询（含 [[calibers/enabled_tenant]]）都以此为入口，因此该术语的边界必须在需求与实现两侧保持一致。

## 版本演进

v0.1：确立与 `tenantFlgEn` 的边界裁决（boundary），记录初始化相等、后续分叉的事实。
---END FILE---

---FILE: concepts/tenant_flg_en.md---
---
type: concept
title: tenantFlgEn
page_key: concept.tenant_flg_en
domain: 租户配置
status: draft
aliases:
  - tenant_flg_en
  - 项目标识（英文）
  - 租户英文标识
  - projectMark
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.tenant_flg_en
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
contract_version: "0.1"
maps_to: tenant_setting_config.tenant_flg_en
field_targets:
  - tenant_setting_config.tenant_flg_en
adjudication: boundary
also_confused_with:
  - dbTenantCode
---

`tenantFlgEn` 是租户在产融侧的项目级英文标识，Excel 导入列名「项目标识(产融 tenant_flg_en)」即指该字段。它既被用于租户查询，又被当作项目标识使用，因此与 [[concepts/db_tenant_code]] 的边界必须显式声明（见 [[calibers/shared_fake_tenant]]、[[calibers/lls_self_tenant]]）。初始化时二者被写成相等，但共享租户下同 `dbTenantCode` 可有多 `tenantFlgEn`。

## 需求背景

同一数据租户要承载多个项目/品牌标识对外展示与服务，项目标识因此从租户标识中独立出来，成为可一对多的维度。

## 版本演进

v0.1：确立与 `dbTenantCode` 的边界裁决（boundary）。
---END FILE---

---FILE: concepts/bg_color.md---
---
type: concept
title: bgColor
page_key: concept.bg_color
domain: 租户配置
status: draft
aliases:
  - 背景颜色
  - 灰度颜色
  - bg_color
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.bg_color
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java
contract_version: "0.1"
maps_to: tenant_setting_config.bg_color
field_targets:
  - tenant_setting_config.bg_color
adjudication: boundary
also_confused_with:
  - main_theme_color
  - ai_resource_color
---

`bgColor` 只承载灰度开关语义，取值 `L`（彩色，ColorConstants.LIGHT）、`G`（灰色，ColorConstants.GRAY）、`null`（未设置，按彩色处理）。它不表达主题色，也不表达智能客服按钮色——`main_theme_color` 与 [[tables/tenant_setting_config]] 中的 `ai_resource_color` 各自独立。状态迁移见 [[processes/bg_color_gray]]，配套的全局窗口见 [[processes/global_bg_gray_switch]]。

## 需求背景

临时性全局灰度需要与常规配色解耦，避免灰度操作污染主题配置，因此把灰度收敛到单一字段上。

## 版本演进

v0.1：确立与 `main_theme_color`、`ai_resource_color` 的边界裁决（boundary）。
---END FILE---

---FILE: concepts/gray_background.md---
---
type: concept
title: 灰度背景
page_key: concept.gray_background
domain: 租户配置
status: draft
aliases:
  - 灰色背景
  - G
  - ColorConstants.GRAY
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.bg_color
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java
contract_version: "0.1"
maps_to: "tenant_setting_config.bg_color = 'G'"
field_targets:
  - tenant_setting_config.bg_color
adjudication: synonym
also_confused_with: []
---

「灰度背景」「灰色背景」「G」「ColorConstants.GRAY」指同一件事：[[tables/tenant_setting_config]] 中 `bg_color='G'` 所表达的灰色展示态。它是同义集合，不引入新的字段；筛选口径见 [[calibers/gray_bg_tenant]]，取值流转见 [[processes/bg_color_gray]]。

## 需求背景

灰度窗口期间前端需要统一的灰阶展示，业务与代码中对该状态的叫法不一，需要收敛为同一术语。

## 版本演进

v0.1：判定为同义词（synonym），不涉及字段边界争议。
---END FILE---

---FILE: concepts/enable.md
---
type: concept
title: enable
page_key: concept.enable
domain: 租户配置
status: draft
aliases:
  - 启用标记
  - enable
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.enable
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
contract_version: "0.1"
maps_to: tenant_setting_config.enable
field_targets:
  - tenant_setting_config.enable
adjudication: boundary
also_confused_with:
  - status
---

`enable` 是记录启用态（实测存量全部为 `Y`），`status` 是租户业务生效态（`N/Y` 并存）。二者最容易被当成同一件事，但查询「生效租户」必须两条件并列，见 [[calibers/effective_tenant]] 与 [[calibers/enabled_tenant]]。停用一个租户与让一个租户尚未生效是两种不同业务动作，不可用一个字段替代另一个。

## 需求背景

记录级启停（是否还有效地存在于系统中）与业务级生效（是否完成配置校验可以对外服务）是两个正交维度，因此拆成两字段。

## 版本演进

v0.1：确立与 `status` 的边界裁决（boundary）。
---END FILE---

---FILE: concepts/tenant_operator.md---
---
type: concept
title: 运营人员(租户级)
page_key: concept.tenant_operator
domain: 租户配置
status: draft
aliases:
  - operator_id
  - operator_name
  - operator_email
  - 运营人
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java
contract_version: "0.1"
maps_to: tenant_setting_config.operator_id / operator_name / operator_email
field_targets:
  - tenant_setting_config.operator_id
  - tenant_setting_config.operator_name
  - tenant_setting_config.operator_email
adjudication: boundary
also_confused_with:
  - opContactA
  - cust_person_info.operator_id
---

「运营人员」在系统里存在于三个层级，本概念只指租户级：[[tables/tenant_setting_config]] 的 `operator_id` / `operator_name` / `operator_email`，用于运营邮件触达（配合 `send_email`，并由 `op_update_user` / `op_update_time` 记录运营配置的更新轨迹）。项目级对应 [[concepts/op_contact_a]] 等 `tenant_project.op_contact_*`；企业联系人级对应 [[tables/cust_person_info]] 的 `operator_id` / `operator_realname` / `operator`。三者不可混用，运营邮件的最终收件人需按层级叠加判断。

## 需求背景

租户级运营人承担面向整个租户的运营邮件触达；项目级对接人承担具体项目的协作；企业联系人级运营人用于追溯联系人归属。层级不同，责任范围与变更频率都不同。

## 版本演进

v0.1：确立与 `opContactA`、`cust_person_info.operator_id` 的边界裁决（boundary）。
---END FILE---

---FILE: concepts/op_contact_a.md---
---
type: concept
title: 运营对接人A
page_key: concept.op_contact_a
domain: 租户配置
status: draft
aliases:
  - op_contact_a
  - opContactA
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
contract_version: "0.1"
maps_to: tenant_project.op_contact_a / cust_project_rel.op_contact_a / wec_project_operation_rel.op_contact_a
field_targets:
  - tenant_project.op_contact_a
  - cust_project_rel.op_contact_a
  - wec_project_operation_rel.op_contact_a
adjudication: boundary
also_confused_with:
  - operator_id
---

`opContactA` 是项目级运营对接人 A，取值为单个运营人员 ID，并同时落在项目主档与两处关联表上；更新时需要联动 `op_contact_a_group` 以保证分组一致。它与租户级/联系人级的 `operator_id` 属于不同维度（见 [[concepts/tenant_operator]]），不可互相赋值。同表的 `op_contact_b` 表示可多个运营人员ID的对接人B。

## 需求背景

一个项目按 A/B 双人对接运营是长期协作约定，关联表冗余保存是为了按客户、按项目两条检索路径都能直接命中对接人。

## 版本演进

v0.1：确立与 `operator_id` 的边界裁决（boundary），并登记三处落点。
---END FILE---

---FILE: concepts/platform_operator.md---
---
type: concept
title: 平台运营方
page_key: concept.platform_operator
domain: 租户配置
status: draft
aliases:
  - platform_operator
  - platformOperator
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.platform_operator
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/component/PlatformComponentFacade.java:needPlatformOperatorCompany
contract_version: "0.1"
maps_to: tenant_setting_config.platform_operator(JSON数组)
field_targets:
  - tenant_setting_config.platform_operator
adjudication: boundary
also_confused_with: []
---

`platform_operator` 以 JSON 数组存储，元素取值 `platform` / `tenant`，可组合。它的判定是「包含」而非「等于」：仅当数组含 `platform` 时才要求运营方企业存在，见 [[calibers/platform_operator_configured]]。因此「配置了平台运营方」与「需要校验运营方企业」不是等价条件。

## 需求背景

平台运营与租户方运营是两种运营主体，校验条件与业务前置不同，故用可组合数组表达，避免为两种组合各建字段。

## 版本演进

v0.1：登记 JSON 数组语义与「包含 platform」判定口径。
---END FILE---

---FILE: concepts/tenant_source.md---
---
type: concept
title: 租户来源
page_key: concept.tenant_source
domain: 租户配置
status: draft
aliases:
  - source
  - 租户来源id
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.source
  - db:tenant_setting_config.source_id
contract_version: "0.1"
maps_to: tenant_setting_config.source / source_id
field_targets:
  - tenant_setting_config.source
  - tenant_setting_config.source_id
adjudication: boundary
also_confused_with: []
---

`source` 标记租户由哪一个上游系统创建，实测值为 `ACFLOW` / `pplatform`；`source_id` 是对应上游系统中的记录 ID。二者成对使用：一个说明来源系统，一个说明来源主键。与 [[calibers/stack_tenant_data]]（`is_stack` 区分存量/新增）语义相邻但不同——来源说明「从哪来」，存量标记说明「是否历史数据」。

## 需求背景

租户可能由多个上游系统同步创建，需要可追溯来源系统与来源主键，以便回查与对账。

## 版本演进

v0.1：依据 `source` 实测取值建立术语基线。
---END FILE---

---FILE: concepts/is_deleted.md---
---
type: concept
title: 软删除标记
page_key: concept.is_deleted
domain: 租户配置
status: draft
aliases:
  - is_deleted
  - 删除标识
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java
contract_version: "0.1"
maps_to: async_io_task.is_deleted / operation_user.deleted
field_targets:
  - async_io_task.is_deleted
  - operation_user.deleted
adjudication: boundary
also_confused_with: []
---

软删除标记在各表使用字符串 `0/1`，既不是布尔值也不是 `Y/N`。查询未删除数据必须显式写 `'0'`（见 [[calibers/not_deleted_async_task]]）；若按 `Y/N` 或布尔语义书写条件，会静默返回错误结果集。注意部分表列名为 `deleted`，取值约定相同但列名不同，不可按列名统一拼接。

## 需求背景

任务与用户记录需要保留用于审计与结果回溯，因此采用软删除；字符串取值来自历史实现约定，短期内不做类型收敛。

## 版本演进

v0.1：登记 `0/1` 字符串取值约定与显式 `'0'` 查询要求。
---END FILE---

---FILE: rules/project_code_required_default_project.md---
---
type: rule
title: 项目码必填联动默认项目
page_key: rule.project_code_required_default_project
domain: 租户配置
status: draft
aliases:
  - 项目码必填
  - projectCodeRequired
  - defaultProjectId 必填
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:checkBeforeSave
contract_version: "0.1"
---

当租户配置了 `projectCodeRequired='Y'`（即 [[calibers/project_code_required_tenant]]），保存前必须同时提供 `defaultProjectId`，否则直接抛错阻断保存。`defaultProjectId` 指向 [[tables/tenant_project]]，因此该规则把「项目码必填」的租户与一个默认项目强绑定，避免出现要求项目码却没有默认项目可回的悬空配置。

## 需求背景

以项目码作为业务主键的租户在创建业务单据时必须能回落到一个默认项目；若只开必填开关而不绑定默认项目，会在业务提交环节才暴露问题，因此把校验前移到租户保存。

## 版本演进

v0.1：依据 `checkBeforeSave` 中的前置校验建立规则；`field_targets` 中第二项在语义分析来源中被截断，暂未登记，待补证后回填。

```yaml
rule: 项目码必填联动默认项目
content: "projectCodeRequired='Y' 时 defaultProjectId 必须非空，否则抛「项目码为必填时，请先配置默认关联项目」"
impact: 阻断租户保存
field_targets:
  - tenant_setting_config.project_code_required
```

相关页面：[[tables/tenant_setting_config]]、[[tables/tenant_project]]、[[calibers/project_code_required_tenant]]、[[processes/tenant_status_effective]]。
---END FILE---

---REVIEW: rule | 项目码必填联动默认项目---
语义分析中该规则的 `field_targets` 在 `"tenant_setting_config.defau` 处被截断，第二项无法逐字确认。当前锚点块只登记了完整可见的 `tenant_setting_config.project_code_required`；补全后需回填 `default_project_id`（或实际字段）并复核 content 与 impact 是否完整。
---END REVIEW---

---REVIEW: table | scope.databases 物理库名缺证---
语义分析只给出代码模块路径（lowcode-pplatform-tenant-management / lowcode-pplatform-customer-management）与表名，未给出物理库名。所有页面 frontmatter 的 `scope.databases` 暂以模块名占位，待补齐物理库名（含是否分库、共享库归属）后统一替换，并同步 [[calibers/shared_fake_tenant]] 中 `tenant_setting_config_share` 的库归属。
---END REVIEW---

---REVIEW: caliber | 配置项占位符取值未知---
[[calibers/lls_self_tenant]] 的 predicate 依赖 `${tenantProperties.platformTenantDbTenantCode}` 与 `${tenantProperties.llsTenantFlgEn}`，语义分析未给出这两个配置项的实际取值或环境差异。锚点块按原文保留占位符，未做替换；需补证后确认是否存在多环境不同判定结果。
---END REVIEW---

---REVIEW: process | 租户推送状态取值不完整---
[[processes/tenant_pushing_status]] 仅观测到 `Y`（已推送创建事件）一个取值，未推送一侧的显式取值（null / N / 其他）在证据中未出现。当前锚点块只登记 `Y` 与一条 from=null 的迁移，不臆造状态值；待补充未推送侧取值与失败重试路径。
---END REVIEW---