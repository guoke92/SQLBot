---FILE: tables/tenant_setting_config.md---
---
type: table
title: 租户配置表 tenant_setting_config
page_key: tenant_setting_config
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [租户配置表, 租户设置表, tenant_setting_config]
oid: 1
scope:
  databases: [unknown]
sources:
  - "db:tenant_setting_config 全量分布（enable 364 行全为 Y；status Y=124 / N=240；operator_ai_customer '0'=108 / '1'=15）"
  - "code:TenantDomainService / TenantAppliactionService / TenantSettingConfigController"
contract_version: "0.1"
---

租户配置表是租户开通、生效、灰度与运营触达的配置中枢：一行代表一个租户（同一 `db_tenant_code` 下可再挂多条项目标识行或共享行）。它同时承担三个角色——数据隔离键的落点（[[db_tenant_code]]）、生效状态机的载体（[[tenant_status_effective]]）以及灰度背景色与运营邮件开关的来源（[[tenant_bg_color_gray]]、[[operator_email]]）。

读取路径以 [[enable_tenant_config]] 为前置口径，只有启用行才参与业务；状态维度区分 [[tenant_effective]] 与 [[tenant_pending_effective]]。租户落库过程涉及两条特殊分支：迁移租户的占位落库（[[tenant_migratory_approval_placeholder]]）与自营假租户的共享落表（[[rule_share_self_tenant]]）。

## 需求背景
租户需要按租户维度完成合同模板、通知、待办、短信、平台运营方、门户页、产品与基础信息等配置，全部校验通过后才允许状态回写为已生效；存量迁移租户先以「待生效」占位落库，避免触发新增事件。灰度窗口内的颜色控制与运营邮件开关也集中在本表，供前端与推送链路读取。

## 版本演进
v0.1（本页）：首版契约，仅覆盖语义分析中有证据的 22 个字段；字段物理类型未采集，暂记 `unknown`。表内其余物理列（如主键、审计列）尚未纳入本契约。

```ground:table
table: tenant_setting_config
fields:
  - name: db_tenant_code
    type: unknown
    desc: "数据租户标识，租户级数据隔离键，表上为 UNI 唯一；全模块按此列取租户配置"
    dict: ""
  - name: enable
    type: unknown
    desc: "启用标记 Y/N，DB 全量 364 行均为 Y；所有读取路径（getFirstByDbTenantCode / getByTenantFlagEn / listActicveAll）都以 enable='Y' 为前置条件"
    dict: "Y/N"
  - name: status
    type: unknown
    desc: "租户生效状态，Y=已生效；仅 effective 八项配置校验全部通过后才回写 Y，否则保持 N/空（导出时展示为『待生效』）"
    dict: "Y/N"
  - name: tenant_flg_en
    type: unknown
    desc: "项目标识（英文），XYC 体系下的租户唯一标识；afterCreate 初始化时会被强制置为 db_tenant_code"
    dict: ""
  - name: code
    type: unknown
    desc: "租户编码，UNI 唯一，保存前做唯一性校验并给出『已存在』提示；与 db_tenant_code 语义不同"
    dict: ""
  - name: bg_color
    type: unknown
    desc: "背景颜色，L=彩色 G=灰色；实际生效受 Redis 灰度开关缓存（BGCOLOR_SWITCH_TTL）控制"
    dict: "L/G"
  - name: ai_resource_color
    type: unknown
    desc: "智能客服按钮颜色，自由字符串（DB 存在 '#2664fd'、'222' 等脏值）；基础信息保存后若为空会以 main_theme_color 兜底"
    dict: ""
  - name: operator_ai_customer
    type: unknown
    desc: "是否开启智能客服，取值是字符 '0'/'1' 而非 Y/N（DB: '0'=108、'1'=15）"
    dict: "0/1"
  - name: project_code_required
    type: unknown
    desc: "项目码是否必填 Y/N；等于 Y 时强制要求 default_project_id 非空"
    dict: "Y/N"
  - name: default_project_id
    type: unknown
    desc: "默认关联项目，指向 tenant_project.id"
    dict: ""
  - name: share_flag
    type: unknown
    desc: "租户共享标识；为 Y 且同 db_tenant_code 已有主记录但 tenant_flg_en 不同时，按『自营假租户』走 tenant_setting_config_share 而不新建主表记录"
    dict: "Y/N"
  - name: source
    type: unknown
    desc: "租户来源：平台自建写常量 'pplatform'，迁移租户直接写 BizSystemDTO.bizSystemCode（DB 出现 ACFLOW 198 行）"
    dict: ""
  - name: source_id
    type: unknown
    desc: "来源方唯一 id；平台自建时取自身主键的字符串形式"
    dict: ""
  - name: pushing_status
    type: unknown
    desc: "创建事件是否已推送 Y/N，是非 CREATED 租户事件推送（变更/生效）的前置门控"
    dict: "Y/N"
  - name: platform_operator
    type: unknown
    desc: "平台运营方，JSON 数组字符串（如 [\"platform\",\"tenant\"]），需解析后与 PlatformOperatorEnum.dictKey 比较"
    dict: "PlatformOperatorEnum.dictKey"
  - name: send_email
    type: unknown
    desc: "是否发送运营邮件 Y/N，与 operator_email 配合决定触达对象"
    dict: "Y/N"
  - name: operator_email
    type: unknown
    desc: "运营人员邮箱，运营邮件收件人；DB 中存在测试脏值（如 1198273@qq.com）"
    dict: ""
  - name: customer_card_type
    type: unknown
    desc: "客服名片类型，WX_WORK=发送企微名片，WX=发送微信名片"
    dict: "WX_WORK/WX"
  - name: generate_electronic_auth_flag
    type: unknown
    desc: "是否生成电子版授权书 Y/N，由 updateOperationConfigById 直写（不做空串转 null 之外的规范化）"
    dict: "Y/N"
  - name: migratory_flag
    type: unknown
    desc: "迁移标志，实际是 JSON 串 '{\"billMigratory\":true}'（DB 全量同值），不是 Y/N 布尔"
    dict: ""
  - name: dbass_app_id
    type: unknown
    desc: "DBAss 应用 id，初始化时统一写入 Nacos 配置的产融 appId（DB 仅两个值，243 行集中在 app_ChanRongPin336_20240529）"
    dict: ""
  - name: sso_sys_channel
    type: unknown
    desc: "PC 端 SSO 渠道号，取 dbass tenantAndAppIdAuth 返回中 scpr-pplatform-pc 对应的 sysChannel"
    dict: ""
```
---END FILE---

---FILE: tables/async_io_task.md---
---
type: table
title: 异步导入导出任务表 async_io_task
page_key: async_io_task
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [异步任务表, 导入导出任务表, async_io_task]
oid: 1
scope:
  databases: [unknown]
sources:
  - "db:async_io_task.status 分布（RUNNING=3）；is_deleted 字符串 '0'/'1'"
  - "code:AsyncIoTaskManager / AsyncIoTaskXxlJobHandler"
contract_version: "0.1"
---

异步导入导出任务表登记文件型异步作业的调度与结果信息，是租户侧批量导入导出（如运营配置批量回写）的落地载体。任务号由 MySQL 自增生成并由应用层用作分片调度键，状态列驱动 [[async_io_task_status]] 状态机，`file_url` 承载结果文件或错误文件的 COS object key。

读取与清理遵循 [[async_io_task_not_deleted]]、[[async_io_task_pending]] 与 [[async_io_task_running]] 三个口径；IMPORT 登记时刻意不写用户上传源文件路径，避免下载链路把源文件当成结果文件返回。

## 需求背景
批量导入导出耗时较长，需要异步化并可在文件管理中查询进度、下载结果与错误文件；节点强杀或 OOM 后停留在 RUNNING 的任务需要能被超时兜底清理为失败，避免任务长期悬挂。

## 版本演进
v0.1（本页）：首版契约，仅覆盖语义分析中有证据的 4 个字段；字段物理类型未采集，暂记 `unknown`。

```ground:table
table: async_io_task
fields:
  - name: task_no
    type: unknown
    desc: "任务号，MySQL 自增生成（应用层不 set），同时作为分片调度键 MOD(task_no, shardTotal)"
    dict: ""
  - name: status
    type: unknown
    desc: "异步任务状态，落库为枚举 name() 大写值 PENDING/RUNNING/SUCCESS/FAILED"
    dict: "PENDING/RUNNING/SUCCESS/FAILED"
  - name: is_deleted
    type: unknown
    desc: "软删标记 '0'=否 '1'=是（字符串，非 Y/N）"
    dict: "0/1"
  - name: file_url
    type: unknown
    desc: "成功=结果文件 / 失败=错误文件 的 COS object key；IMPORT 登记时刻意不写用户上传源文件 path，避免被当成结果文件下载"
    dict: ""
```
---END FILE---

---FILE: tables/cust_person_info.md---
---
type: table
title: 客户联系人表 cust_person_info
page_key: cust_person_info
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [联系人表, 客户人员表, cust_person_info]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AssetOperatorSyncApplication.syncAssetOperator / operCustFacade.getOperatorList"
contract_version: "0.1"
---

客户联系人表登记企业下的联系人及其运营对接关系，是资产审核运营人员同步的取数来源。`ref_cust_company_info` 以企业 code（非主键 id）关联 [[cust_company_info]]，`operator_id` 指向运营中台人员，语义见 [[operator_id]]。

筛选企业下联系人时使用 [[cust_person_enable]] 口径。

## 需求背景
存量运营方与资产审核运营人员需要按企业维度批量同步到产品侧，同步前必须过滤掉未启用的联系人，且运营人员必须用运营中台的人员 id 比对，不能误用本地主键。

## 版本演进
v0.1（本页）：首版契约，仅覆盖语义分析中有证据的 2 个字段；字段物理类型未采集，暂记 `unknown`。

```ground:table
table: cust_person_info
fields:
  - name: ref_cust_company_info
    type: unknown
    desc: "关联企业 code，与 cust_company_info.code 对应（注意不是主键 id）"
    dict: ""
  - name: operator_id
    type: unknown
    desc: "运营人员 id，指向运营中台人员（operCustFacade.getOperatorList 返回），不是本地表主键"
    dict: ""
```
---END FILE---

---FILE: tables/cust_company_info.md---
---
type: table
title: 客户企业表 cust_company_info
page_key: cust_company_info
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [企业表, 客户企业表, cust_company_info]
oid: 1
scope:
  databases: [unknown]
sources:
  - "db:cust_company_info.cust_company_type JSON 数组字符串（如 [\"SUPPLIER\"]）"
  - "code:CustGeneralProductApplication.syncExistingPlatformOperatorToProducts"
contract_version: "0.1"
---

客户企业表登记企业主体的角色与启用状态，是企业级资产审核与运营方推送的主表。企业角色以 JSON 数组字符串存储，资产审核同步只对 SUPPLIER 生效；存量运营方全量扫描使用 [[cust_company_enable]] 口径。

## 需求背景
一家企业可能同时具备多种角色，因此角色以 JSON 数组落库并按角色筛选同步范围；未启用的企业不参与运营方推送。

## 版本演进
v0.1（本页）：首版契约，仅覆盖语义分析中有证据的 1 个字段；字段物理类型未采集，暂记 `unknown`。

```ground:table
table: cust_company_info
fields:
  - name: cust_company_type
    type: unknown
    desc: "企业角色，JSON 数组字符串（如 [\"SUPPLIER\"]）；资产审核同步仅对 SUPPLIER 生效"
    dict: ""
```
---END FILE---

---FILE: processes/tenant_status_effective.md---
---
type: process
title: 租户生效状态机
page_key: tenant_status_effective
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [租户生效状态, status 状态机, effective]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService.effective / predicateEffective；TenantAppliactionService.syncTenant"
  - "db:tenant_setting_config.status 分布 Y=124 / N=240"
contract_version: "0.1"
---

租户生效状态机描述 `tenant_setting_config.status` 在「待生效 → 已生效」之间的迁移。生效是一次全量校验：合同模板、通知、待办、短信、平台运营方、门户页、产品、基础信息八项配置全部通过后，才把 `status` 回写为 Y；任一未完成则返回告警并保持原状态。迁移租户落库时不显式设置状态，保持空/待生效。

该状态机与三个口径直接相关：[[enable_tenant_config]]（读取前置）、[[tenant_effective]]（已生效筛选）、[[tenant_pending_effective]]（待生效筛选）。状态字段本身见 [[tenant_setting_config]]。

## 需求背景
租户创建后配置项分散在多个模块，需要一次性校验后才允许对外生效，避免半配置租户被业务使用；迁移租户为避免触发新增事件，先以占位状态落库。

## 版本演进
v0.1（本页）：首版契约，三态与四条迁移均来自语义分析证据；暂无历史版本记录。

```ground:process
name: 租户生效状态
field: tenant_setting_config.status
states:
  - value: "N"
    label: 待生效
    source: db_dist
  - value: "Y"
    label: 已生效
    source: db_dist
  - value: ""
    label: 空/未生效（迁移租户初始态，导出展示为『待生效』）
    source: code_const
transitions:
  - from: "N"
    event: "effective() 八项配置（合同模板/通知/待办/短信/平台运营方/门户页/产品/基础信息）全部校验通过"
    to: "Y"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:effective#L108"
  - from: "N"
    event: "任一配置项未完成 → 返回 WindowAlertDTO.alertEnabled=true，状态不变"
    to: "N"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:predicateEffective"
  - from: "任意"
    event: "syncTenant 迁移租户落库（不显式设置 status，保持待生效）"
    to: ""
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:syncTenant"
```
---END FILE---

---FILE: processes/async_io_task_status.md---
---
type: process
title: 异步导入导出任务状态机
page_key: async_io_task_status
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [异步任务状态, async_io_task.status, PENDING/RUNNING/SUCCESS/FAILED]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AsyncIoTaskManager.markRunning / markSuccessWithResult / markSuccessWithFile / markImportFailed / markRunningTimeout；AsyncIoTaskXxlJobHandler.handleFailure"
  - "db:async_io_task.status 分布（RUNNING=3）"
contract_version: "0.1"
---

异步导入导出任务状态机描述 `async_io_task.status` 从 PENDING 出发的四条分支：正常无流返回或带文件成功上传 COS 都进入 SUCCESS；业务抛错、导入存在失败行、以及 RUNNING 停留超过 timeoutMinutes 的兜底清理都进入 FAILED。PENDING → RUNNING 使用 CAS 更新（where status=PENDING）保证并发下只有一个执行者抢到任务。

相关口径：[[async_io_task_pending]]（分片拉取）、[[async_io_task_running]]（超时清理）、[[async_io_task_not_deleted]]（查询可见性）。

## 需求背景
文件型导入导出需要异步执行、可观测、可重试；节点被强杀或 OOM 后必须由超时兜底把悬挂任务收敛为失败，避免任务永久停在执行中。

## 版本演进
v0.1（本页）：首版契约，四态与六条迁移均来自语义分析证据；暂无历史版本记录。

```ground:process
name: 异步导入导出任务状态
field: async_io_task.status
states:
  - value: "PENDING"
    label: 待执行
    source: code_enum
  - value: "RUNNING"
    label: 执行中
    source: db_dist
  - value: "SUCCESS"
    label: 成功
    source: db_dist
  - value: "FAILED"
    label: 失败
    source: db_dist
transitions:
  - from: "PENDING"
    event: "CAS markRunning（where status=PENDING）"
    to: "RUNNING"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markRunning"
  - from: "RUNNING"
    event: "业务方法正常返回且无 stream"
    to: "SUCCESS"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markSuccessWithResult"
  - from: "RUNNING"
    event: "业务方法返回下载字节流并上传 COS 成功"
    to: "SUCCESS"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markSuccessWithFile"
  - from: "RUNNING"
    event: "业务方法抛 Throwable（handleFailure 兜底生成错误文件）"
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/job/AsyncIoTaskXxlJobHandler.java:handleFailure"
  - from: "RUNNING"
    event: "IMPORT 正常返回但存在失败行"
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markImportFailed"
  - from: "RUNNING"
    event: "RUNNING 停留超过 timeoutMinutes（节点强杀/OOM 兜底）"
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markRunningTimeout"
```
---END FILE---

---FILE: processes/tenant_bg_color_gray.md---
---
type: process
title: 租户背景颜色灰度状态机
page_key: tenant_bg_color_gray
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [背景颜色灰度, bg_color 状态机, 彩色/灰色]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantAppliactionService.updateTenantColorGray / setColorlight / updateTenantColorNull；TenantSettingConfigController.getBgColor"
  - "db comment『背景颜色(L:彩色 G：灰色)』；Redis 灰度缓存 BGCOLOR_SWITCH_TTL"
contract_version: "0.1"
---

该状态机描述 `tenant_setting_config.bg_color` 在全局灰度窗口下的取值变化：窗口生效且租户未自定义颜色时批量置 G（灰），灰度期内租户主动选择彩色则落 L，缓存过期或走 `bgcolor/reset/light` 时置 NULL。前端展示态与落库态并不完全一致——灰度窗口内颜色为 L 时对前端返回 state=OFF 仅作展示，不回写数据库。

颜色语义与相邻颜色字段的边界见 [[bg_color]]；判定口径见 [[bg_color_gray]] 与 [[bg_color_light]]。

## 需求背景
灰度期间需要统一收敛租户主题为灰色以减少视觉变更，同时允许租户在灰度期内选择保留彩色；灰度结束后通过重置恢复默认，不做历史值回写。

## 版本演进
v0.1（本页）：首版契约，两态与四条迁移来自语义分析证据；暂无历史版本记录。

```ground:process
name: 租户背景颜色/灰度
field: tenant_setting_config.bg_color
states:
  - value: "L"
    label: 彩色
    source: code_const
  - value: "G"
    label: 灰色
    source: code_const
transitions:
  - from: ""
    event: "全局灰度窗口生效且租户未自定义颜色 → updateTenantColorGray() 批量置 G"
    to: "G"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorGray"
  - from: "G"
    event: "灰度期内租户选择彩色 setColorlight(id) 落 L"
    to: "L"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:setColorlight"
  - from: "L"
    event: "灰度窗口内租户颜色为 L 时对前端返回 state=OFF（仅展示态，不落库）"
    to: "L"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:getBgColor"
  - from: "任意"
    event: "缓存过期 / bgcolor/reset/light → updateTenantColorNull() 置 NULL"
    to: ""
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorNull"
```
---END FILE---

---FILE: calibers/enable_tenant_config.md---
---
type: caliber
title: 启用租户配置口径（enable='Y'）
page_key: enable_tenant_config
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [启用租户, enable='Y', 有效租户配置]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService.getFirstByDbTenantCode / getByTenantFlagEn / listAll / listActicveAll"
  - "db:tenant_setting_config.enable 364 行全为 Y"
contract_version: "0.1"
---

「启用租户配置」是所有租户配置读取路径的共同前置条件：无论按 `db_tenant_code`、`tenant_flg_en`、`appTenantCode` 还是 `source + sourceId` 查询，命中结果都必须满足 `enable='Y'`。当前库内该列为全量 Y，因此该口径在数据上不产生过滤差异，但在契约上必须显式保留。

它与 [[tenant_effective]]（状态口径）正交：启用是「记录是否可用」，生效是「配置是否齐备」。表结构见 [[tenant_setting_config]]。

## 需求背景
租户停用后不应再被任何业务链路读取到配置，因此把启用判断下沉到统一的读取路径，避免各调用点自行处理。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 启用租户配置
predicate: "tenant_setting_config.enable = 'Y'"
scope: "所有按 dbTenantCode/tenantFlgEn/appTenantCode/source+sourceId 的租户配置读取路径"
evidence: "code:TenantDomainService.getFirstByDbTenantCode / getByTenantFlagEn / listAll / listActicveAll；db:enable 364 行全为 Y"
```
---END FILE---

---FILE: calibers/tenant_effective.md---
---
type: caliber
title: 已生效租户口径（status='Y'）
page_key: tenant_effective
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [已生效租户, status='Y', 生效租户列表]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService.listActicveAll"
  - "db:tenant_setting_config.status Y=124 / N=240"
contract_version: "0.1"
---

「已生效租户」用于生效租户列表与导出状态展示，判定条件为 `status='Y'`。该值只由 [[tenant_status_effective]] 状态机在八项配置校验通过后回写，因此它同时是一份「配置齐备度」的代理指标。

与 [[tenant_pending_effective]] 互为补集（注意空状态不落在 N 上）。表结构见 [[tenant_setting_config]]。

## 需求背景
运营与导出场景需要一份可信的生效租户名单，直接用状态列筛选，避免每次重算配置齐备度。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 已生效租户
predicate: "tenant_setting_config.status = 'Y'"
scope: "activeList() 生效租户列表、导出状态展示"
evidence: "code:TenantDomainService.listActicveAll；db:Y=124 / N=240"
```
---END FILE---

---FILE: calibers/tenant_pending_effective.md---
---
type: caliber
title: 待生效租户口径（status='N'）
page_key: tenant_pending_effective
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [待生效租户, status='N']
oid: 1
scope:
  databases: [unknown]
sources:
  - "db:tenant_setting_config.status N=240"
contract_version: "0.1"
---

「待生效租户」指尚未通过 `effective()` 校验、状态仍为 N 的租户，迁移租户大部分落在此集合中。导出时该状态（含空值）统一展示为『待生效』，因此展示口径比 `status='N'` 略宽。

状态迁移过程见 [[tenant_status_effective]]；对比口径见 [[tenant_effective]]。

## 需求背景
存量迁移租户与新开租户都需要一个可识别的未完成态，便于运营在列表中识别并推进配置。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；空状态是否计入本口径待复核（见 REVIEW）。

```ground:caliber
name: 待生效租户
predicate: "tenant_setting_config.status = 'N'"
scope: "未通过 effective 校验的租户（含全部迁移租户）"
evidence: "db:status N=240"
```
---END FILE---

---FILE: calibers/tenant_created_pushed.md---
---
type: caliber
title: 创建事件已推送口径（pushing_status='Y'）
page_key: tenant_created_pushed
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [创建事件已推送, pushing_status='Y']
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantAppliactionService.pushTenant"
contract_version: "0.1"
---

「创建事件已推送」是租户事件推送链路的门控口径：只有 `pushing_status='Y'`（即 CREATED 事件已推送完成）的租户，才允许继续推送变更、生效等非 CREATED 事件。它保证事件顺序，避免下游先收到变更再收到创建。

表结构见 [[tenant_setting_config]]。

## 需求背景
租户事件按创建先行、变更/生效后至的顺序消费，必须有一个已推送标记做顺序门控。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 创建事件已推送
predicate: "tenant_setting_config.pushing_status = 'Y'"
scope: "pushTenant / pushTenantSync 中非 CREATED 事件的推送门控"
evidence: "code:TenantAppliactionService.pushTenant"
```
---END FILE---

---FILE: calibers/tenant_migratory_approval_placeholder.md---
---
type: caliber
title: 迁移占位审批状态口径（act_procinst_status='N'）
page_key: tenant_migratory_approval_placeholder
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [迁移占位审批状态, act_procinst_status='N']
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantAppliactionService.syncTenant#L217"
  - "db:act_procinst_status N=204"
contract_version: "0.1"
---

迁移租户落库时把审批流程实例状态写为 N，形成「占位审批」状态，用以避免触发新增 create 事件。它是迁移链路与自建链路的区分口径之一。

迁移链路整体见 [[tenant_status_effective]] 的空状态迁移；表结构见 [[tenant_setting_config]]。

## 需求背景
存量迁移不允许再次对外广播新增事件，因此需要一个可识别的占位审批状态来短路事件触发。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 迁移占位审批状态
predicate: "tenant_setting_config.act_procinst_status = 'N'"
scope: "syncTenant 迁移租户，避免触发新增 create 事件"
evidence: "code:TenantAppliactionService.syncTenant#L217；db:N=204"
```
---END FILE---

---FILE: calibers/bg_color_gray.md---
---
type: caliber
title: 灰色背景口径（bg_color='G'）
page_key: bg_color_gray
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [灰色背景, bg_color='G', GRAY]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:ColorConstants.GRAY 写值点 updateTenantColorGray / getBgColor"
  - "db comment『背景颜色(L:彩色 G：灰色)』"
contract_version: "0.1"
---

「灰色背景」是全局灰度生效期内租户的默认背景色，写值点为 `ColorConstants.GRAY`，落库值 G。批量置灰发生在灰度窗口生效且租户未自定义颜色时。

状态流转见 [[tenant_bg_color_gray]]，对照口径见 [[bg_color_light]]，语义边界见 [[bg_color]]。

## 需求背景
灰度期间需要统一视觉基线，未主动选择颜色的租户默认收敛为灰色。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 灰色背景
predicate: "tenant_setting_config.bg_color = 'G'"
scope: "全局灰度生效期内的租户默认色"
evidence: "code:ColorConstants.GRAY 写值点 updateTenantColorGray / getBgColor；db comment『背景颜色(L:彩色 G：灰色)』"
```
---END FILE---

---FILE: calibers/bg_color_light.md---
---
type: caliber
title: 彩色背景口径（bg_color='L'）
page_key: bg_color_light
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [彩色背景, bg_color='L', LIGHT]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantAppliactionService.setColorlight"
  - "db comment『背景颜色(L:彩色 G：灰色)』"
contract_version: "0.1"
---

「彩色背景」表示租户在灰度期内主动选择保留彩色，落库值 L。注意前端在窗口内可能返回 state=OFF（展示态），与落库值不一致，判断时应以库值为准。

状态流转见 [[tenant_bg_color_gray]]，对照口径见 [[bg_color_gray]]。

## 需求背景
灰度不能强制全部租户变色，需保留租户主动选择彩色的能力。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 彩色背景
predicate: "tenant_setting_config.bg_color = 'L'"
scope: "租户主动选择彩色或灰度重置"
evidence: "code:TenantAppliactionService.setColorlight；db comment"
```
---END FILE---

---FILE: calibers/operator_ai_customer_enabled.md---
---
type: caliber
title: 开启智能客服口径（operator_ai_customer='1'）
page_key: operator_ai_customer_enabled
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [开启智能客服, operator_ai_customer='1']
oid: 1
scope:
  databases: [unknown]
sources:
  - "db:tenant_setting_config.operator_ai_customer '1'=15 / '0'=108"
  - "code:TenantDomainService.updateOperationConfigById 直写"
contract_version: "0.1"
---

「开启智能客服」判定为 `operator_ai_customer='1'`。该字段是 0/1 字符口径而非 Y/N，是本表内最容易与布尔口径混淆的字段之一，引用时不可套用 enable/status 的 Y/N 判断。

表结构见 [[tenant_setting_config]]。

## 需求背景
智能客服入口按租户灰度开通，需要与智能客服按钮颜色（ai_resource_color）一起下发。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；0/1 口径已由 DB 分布证实，不再与 Y/N 混用。

```ground:caliber
name: 开启智能客服
predicate: "tenant_setting_config.operator_ai_customer = '1'"
scope: "智能客服入口开关（注意非 Y/N 口径）"
evidence: "db:'1'=15 / '0'=108；code:TenantDomainService.updateOperationConfigById 直写"
```
---END FILE---

---FILE: calibers/customer_card_type_wx_work.md---
---
type: caliber
title: 企微名片口径（customer_card_type='WX_WORK'）
page_key: customer_card_type_wx_work
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [企微名片, WX_WORK, 客服名片类型]
oid: 1
scope:
  databases: [unknown]
sources:
  - "db:tenant_setting_config.customer_card_type WX_WORK=128 / WX=6"
  - "db comment『与 operCardType 枚举一致』"
contract_version: "0.1"
---

「企微名片」指客服名片下发渠道为 WX_WORK，即发送企业微信名片；对应地 WX 表示发送微信名片。该字段的值与 operCardType 枚举一致。

表结构见 [[tenant_setting_config]]。

## 需求背景
不同租户的客服触达渠道不同，名片类型决定下发哪一种名片。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 企微名片
predicate: "tenant_setting_config.customer_card_type = 'WX_WORK'"
scope: "客服名片下发渠道"
evidence: "db:WX_WORK=128 / WX=6；db comment『与 operCardType 枚举一致』"
```
---END FILE---

---FILE: calibers/async_io_task_not_deleted.md---
---
type: caliber
title: 未删除异步任务口径（is_deleted='0'）
page_key: async_io_task_not_deleted
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [未删除异步任务, is_deleted='0', NOT_DELETED]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AsyncIoTaskManager.pageByUser / getByTaskNo / softDelete 中 NOT_DELETED='0'"
contract_version: "0.1"
---

「未删除异步任务」是所有任务查询与软删操作的可见性口径：文件管理分页、按任务号查询都以 `is_deleted='0'` 过滤，软删时置为 '1'。注意该列是字符串 0/1，不是 Y/N。

表结构见 [[async_io_task]]，状态口径见 [[async_io_task_status]]。

## 需求背景
任务记录需要保留可追溯，删除只做逻辑删除，不物理清理。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 未删除异步任务
predicate: "async_io_task.is_deleted = '0'"
scope: "文件管理分页、按任务号查询、任务号软删"
evidence: "code:AsyncIoTaskManager.pageByUser / getByTaskNo / softDelete 中 NOT_DELETED='0'"
```
---END FILE---

---FILE: calibers/async_io_task_pending.md---
---
type: caliber
title: 待执行异步任务口径（status='PENDING'）
page_key: async_io_task_pending
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [待执行异步任务, PENDING, 分片拉取]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AsyncIoTaskManager.listPendingByShard"
contract_version: "0.1"
---

「待执行异步任务」是 XXL-Job 分片拉取的扫描口径：按 `status='PENDING'` 取任务，结合 `MOD(task_no, shardTotal)` 分片后由 CAS 抢占执行。

状态流转见 [[async_io_task_status]]。

## 需求背景
多节点并发执行时需按任务号分片均衡负载，并保证同一任务只被一个节点执行。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 待执行异步任务
predicate: "async_io_task.status = 'PENDING'"
scope: "XXL-Job 分片拉取"
evidence: "code:AsyncIoTaskManager.listPendingByShard"
```
---END FILE---

---FILE: calibers/async_io_task_running.md---
---
type: caliber
title: 运行中超时异步任务口径（status='RUNNING'）
page_key: async_io_task_running
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [运行中超时任务, RUNNING, 超时清理]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AsyncIoTaskManager.markRunningTimeout"
  - "db:async_io_task.status RUNNING=3"
contract_version: "0.1"
---

「运行超时异步任务」是超时清理任务的扫描集合：处于 `status='RUNNING'` 且停留超过 timeoutMinutes 的任务会被兜底置为 FAILED。它同时是排查悬挂任务的观测口径。

状态流转见 [[async_io_task_status]]。

## 需求背景
节点强杀或 OOM 会让任务永久停留执行中，需要超时扫描将其收敛为失败以便用户重试。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 运行超时异步任务
predicate: "async_io_task.status = 'RUNNING'"
scope: "超时清理任务扫描集合"
evidence: "code:AsyncIoTaskManager.markRunningTimeout；db:RUNNING=3"
```
---END FILE---

---FILE: calibers/cust_person_enable.md---
---
type: caliber
title: 启用联系人口径（cust_person_info.enable='Y'）
page_key: cust_person_enable
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [启用联系人, 联系人 enable='Y']
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AssetOperatorSyncApplication.syncAssetOperator 中 .eq(CustPersonInfoDO::getEnable, \"Y\")"
contract_version: "0.1"
---

「启用联系人」是资产审核运营人员同步时的企业联系人筛选条件：只同步 `enable='Y'` 的联系人。它是人员侧与 [[cust_company_enable]]（企业侧）配套使用的口径。

表结构见 [[cust_person_info]]，运营人员语义边界见 [[operator_id]]。

## 需求背景
离职或停用的联系人不应再被同步为运营对接人，同步前必须按启用状态过滤。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 启用联系人
predicate: "cust_person_info.enable = 'Y'"
scope: "资产审核运营人员同步时筛选企业下联系人"
evidence: "code:AssetOperatorSyncApplication.syncAssetOperator 中 .eq(CustPersonInfoDO::getEnable, \"Y\")"
```
---END FILE---

---FILE: calibers/cust_company_enable.md---
---
type: caliber
title: 启用企业口径（cust_company_info.enable='Y'）
page_key: cust_company_enable
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [启用企业, 企业 enable='Y']
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:CustGeneralProductApplication.syncExistingPlatformOperatorToProducts 中 .eq(getEnable, BooleanEnum.Y.getDictKey())"
contract_version: "0.1"
---

「启用企业」是存量运营方推送全量扫描时的企业筛选条件，取值为 `BooleanEnum.Y.getDictKey()`，语义等同 'Y'。与 [[cust_person_enable]] 一起构成「启用企业 + 启用联系人」的同步范围。

表结构见 [[cust_company_info]]。

## 需求背景
停用企业不应继续推送运营方，全量扫描需要先按启用状态过滤。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 启用企业
predicate: "cust_company_info.enable = 'Y'"
scope: "存量运营方推送全量扫描"
evidence: "code:CustGeneralProductApplication.syncExistingPlatformOperatorToProducts 中 .eq(getEnable, BooleanEnum.Y.getDictKey())"
```
---END FILE---

---FILE: concepts/db_tenant_code.md---
---
type: concept
title: 数据租户标识
page_key: db_tenant_code
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [dbTenantCode, db_tenant_code, 数据租户标识]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService.getFirstByDbTenantCode"
  - "db:tenant_setting_config.db_tenant_code UNI 唯一"
contract_version: "0.1"
maps_to: tenant_setting_config.db_tenant_code
field_targets:
  - tenant_setting_config.db_tenant_code
adjudication: boundary
also_confused_with:
  - tenant_setting_config.app_tenant_code
  - tenant_setting_config.code
  - tenant_setting_config.apaas_tenant_code
---

「数据租户标识」（db_tenant_code）是租户级数据隔离键，在 [[tenant_setting_config]] 上为 UNI 唯一，全模块都按这一列取租户配置。它决定一条配置属于哪个数据租户，是所有读取路径（如 `getFirstByDbTenantCode`）的第一定位条件。

它常与三个近名字段混用，判断口径如下：db_tenant_code 是数据隔离键；`app_tenant_code` 是逻辑租户标识；`code` 是租户编码（UNI 唯一，保存前做唯一性校验）；`apaas_tenant_code` 是 aPaaS 侧编码。四者不可互换——`getFirstByDbTenantCode` 只按 db_tenant_code + enable='Y' 命中。

## 需求背景
同一套产研系统需要按数据租户隔离配置与数据，必须有一个稳定、唯一的隔离键贯穿读取与写入；逻辑租户与 aPaaS 编码属于不同体系，单独成列以避免语义串扰。

## 版本演进
v0.1（本页）：首版契约，语义与边界来自语义分析；暂无历史版本记录。

---END FILE---

---FILE: concepts/tenant_flg_en.md---
---
type: concept
title: 项目标识（英文）
page_key: tenant_flg_en
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [tenantFlgEn, tenant_flg_en, projectMark, 租户英文标识, 项目标识(英文)]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService.getFirstByTenantFlgEn / afterCreate 强制置为 db_tenant_code"
  - "code:TenantDomainService.existEarlyLLsTenant / doSaveTenantShare"
contract_version: "0.1"
maps_to: tenant_setting_config.tenant_flg_en
field_targets:
  - tenant_setting_config.tenant_flg_en
adjudication: boundary
also_confused_with:
  - tenant_setting_config.tenant_flag_zh
  - tenant_project.tenant_flg_en
  - cust_company_info.tenant_flg_en
---

「项目标识（英文）」是 XYC 体系下租户的唯一标识，落在 [[tenant_setting_config]].tenant_flg_en。`afterCreate` 初始化时会把它强制置为 db_tenant_code；同一 `db_tenant_code` 下可以存在多个不同 tenant_flg_en，这正是自营假租户共享落表的判定条件（见 [[rule_share_self_tenant]]）。

边界：Excel 导入的『项目标识(产融 tenant_flg_en)』实际定位的是 tenant_setting_config.tenant_flg_en（走 `getFirstByTenantFlgEn`），不是 tenant_project；`tenantFlagZh` 只是中文展示名。

## 需求背景
产融体系下同一个数据租户可承载多个项目标识，导入与查询都必须以 tenant_flg_en 作为定位键，避免误落到项目主数据表。

## 版本演进
v0.1（本页）：首版契约，语义与边界来自语义分析；暂无历史版本记录。

---END FILE---

---FILE: concepts/bg_color.md---
---
type: concept
title: 灰度颜色 / 背景颜色
page_key: bg_color
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [bgColor, bg_color, 灰色, 彩色]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantAppliactionService.updateTenantColorGray / setColorlight / updateTenantColorNull"
  - "db comment『背景颜色(L:彩色 G：灰色)』"
contract_version: "0.1"
maps_to: tenant_setting_config.bg_color
field_targets:
  - tenant_setting_config.bg_color
adjudication: boundary
also_confused_with:
  - tenant_setting_config.ai_resource_color
  - tenant_setting_config.main_theme_color
  - tenant_setting_config.adapt_colour
---

「灰度颜色 / 背景颜色」指 [[tenant_setting_config]].bg_color，取 L（彩色）/ G（灰色），其实际生效受 Redis 灰度开关缓存（BGCOLOR_SWITCH_TTL）控制。状态流转见 [[tenant_bg_color_gray]]，判定口径见 [[bg_color_gray]] 与 [[bg_color_light]]。

边界：bg_color 是灰度开关结果；`ai_resource_color` 是智能客服按钮色（HEX，DB 存在脏值）；`main_theme_color` 是主题色，并会在 ai_resource_color 为空时兜底；`adapt_colour` 是适配背景色。后三者都不参与灰度缓存判断。

## 需求背景
灰度需要全局可控又允许租户个别选择，因此颜色选择与灰度开关结果必须落在同一列并由缓存控制生效时机，同时与其他「颜色」字段明确区分。

## 版本演进
v0.1（本页）：首版契约，语义与边界来自语义分析；暂无历史版本记录。

---END FILE---

---FILE: concepts/operator_email.md---
---
type: concept
title: 运营邮件
page_key: operator_email
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [sendEmail, send_email, operator_email, 运营邮件]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService / TenantAppliactionService 运营邮件开关与收件人"
contract_version: "0.1"
maps_to: tenant_setting_config.send_email
field_targets:
  - tenant_setting_config.send_email
  - tenant_setting_config.operator_email
adjudication: boundary
also_confused_with:
  - tenant_project.send_email
  - tenant_setting_config.operator_email
---

「运营邮件」在契约上指 [[tenant_setting_config]].send_email，即「是否发送」的 Y/N 开关；与之配套的 `operator_email` 是收件地址，两者共同决定触达对象——开关为 Y 且存在收件人时才真正发送。

边界：send_email 是开关，operator_email 是地址，不可互相替代；tenant_project 与 tenant_setting_config 各有一份同名开关，分别对应项目级与租户级运营触达，引用时必须指明所属表。

## 需求背景
运营触达需要按租户（以及按项目）可开关、可指定收件人，避免全量广播。

## 版本演进
v0.1（本页）：首版契约，语义与边界来自语义分析；DB 中 operator_email 存在测试脏值（如 1198273@qq.com），投产前需清理。

---END FILE---

---FILE: concepts/operator_id.md---
---
type: concept
title: 运营人员 / 运营对接人
page_key: operator_id
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [operatorId, operator_id, opContactA, operationId, 运营人员, 运营对接人]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AssetOperatorSyncApplication.syncAssetOperator；operCustFacade.getOperatorList"
contract_version: "0.1"
maps_to: cust_person_info.operator_id
field_targets:
  - cust_person_info.operator_id
adjudication: boundary
also_confused_with:
  - operation_user.operation_id
  - tenant_setting_config.operator_id
  - cust_project_rel.op_contact_a
---

「运营人员 / 运营对接人」在联系人侧指 [[cust_person_info]].operator_id，存的是运营中台人员 id（用 `operCustFacade.getOperatorList` 返回的 OperUserDTO.id 比对），不是本地表主键。

边界：cust_person_info.operator_id 是运营中台人员 id；operation_user.operation_id 是运营中台库内主键；tenant_setting_config.operator_id 是租户级运营人员；cust_project_rel.op_contact_a 是项目/企业关联表上的对接人字段。四者分属不同层，做关联时必须先确认所查表的语义。

## 需求背景
运营人员主数据在运营中台维护，业务侧只保存其 id 引用；跨库关联不能误用本地主键或关联表对接人字段。

## 版本演进
v0.1（本页）：首版契约，语义与边界来自语义分析；暂无历史版本记录。

---END FILE---

---FILE: concepts/project_code_required.md---
---
type: concept
title: 项目码是否必填
page_key: project_code_required
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [projectCodeRequired, project_code_required, 项目码必填]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService.checkBeforeSave"
contract_version: "0.1"
maps_to: tenant_setting_config.project_code_required
field_targets:
  - tenant_setting_config.project_code_required
  - tenant_setting_config.default_project_id
adjudication: boundary
also_confused_with:
  - tenant_setting_config.default_project_id
---

「项目码是否必填」指 [[tenant_setting_config]].project_code_required（Y/N）。它是触发条件，被约束对象是 `default_project_id`：前者为 Y 时后者必填。二者是一组条件与结果，不能互换理解，联动规则见 [[rule_project_code_default_project]]。

## 需求背景
部分租户要求项目维度的成本/归属管理，必须先指定默认关联项目，否则后续单据无法定位项目。

## 版本演进
v0.1（本页）：首版契约，语义与边界来自语义分析；暂无历史版本记录。

---END FILE---

---FILE: rules/rule_project_code_default_project.md---
---
type: rule
title: 项目码必填联动默认项目
page_key: rule_project_code_default_project
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [项目码必填联动, projectCodeRequired 校验, TASK-0003]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code_path:TenantDomainService.java:checkBeforeSave（注释 TASK-0003）"
  - "reqdoc:租户管理业务规则文档"
contract_version: "0.1"
---

本规则约束 [[project_code_required]] 与 `default_project_id` 的联动：当 projectCodeRequired='Y' 时必须提供 defaultProjectId，否则抛出 COMMON_EXCEPTION『项目码为必填时，请先配置默认关联项目』，租户保存或迁移会被拦截。字段语义见 [[project_code_required]] 与 [[tenant_setting_config]]。

## 需求背景
该规则有双源证据：代码侧为 `TenantDomainService.checkBeforeSave`（源码注释标注 TASK-0003），业务侧见租户管理业务规则文档 reqdoc:租户管理业务规则文档。文档明确项目码必填的租户必须先配置默认关联项目，代码据此前置校验；两处描述一致，故作为锚点证据登记。校验失败的信息文案与代码一致，导出/保存路径共用同一拦截。

## 版本演进
v0.1（本页）：首版契约，锚点证据为代码 + 需求文档双源；暂无历史版本记录。

```ground:rule
name: 项目码必填联动默认项目
content: "projectCodeRequired='Y' 时必须提供 defaultProjectId，否则抛 COMMON_EXCEPTION『项目码为必填时，请先配置默认关联项目』"
impact: "租户保存/迁移被拦截"
field_targets:
  - tenant_setting_config.project_code_required
  - tenant_setting_config.default_project_id
evidence: "code_path:TenantDomainService.java:checkBeforeSave（注释 TASK-0003）+ reqdoc:租户管理业务规则文档"
```
---END FILE---

---FILE: rules/rule_tenant_unique_check.md---
---
type: rule
title: 租户唯一性校验
page_key: rule_tenant_unique_check
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [checkUnique, 租户唯一校验, 已存在，请确认!]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code_path:TenantDomainService.java:checkUnique"
contract_version: "0.1"
---

保存与迁移前对多列逐个做唯一性校验，任一命中即拒绝并提示『已存在，请确认!』。参与校验的列包括 uniSocialCreditCode、code、name、dbTenantCode、tenantFlgEn、devDomain、sitDomain、uatDomain、prdDomain；当 needHfive='Y' 时追加四个 H5 域名的唯一校验。

注意：bandName 的唯一校验已被注释禁用——它虽在代码中出现，但当前不产生拦截，引用时不要把它当作生效规则。

涉及字段：[[tenant_setting_config]] 的 code、db_tenant_code、tenant_flg_en、uni_social_credit_code；标识语义见 [[db_tenant_code]]、[[tenant_flg_en]]。

## 需求背景
租户标识、编码、名称与各环境域名一旦重复会导致路由与数据归属错乱，因此在写入前统一做去重校验，把冲突拦截在保存阶段。

## 版本演进
v0.1（本页）：首版契约，锚点证据来自语义分析；bandName 校验已禁用，如需恢复须复核。

```ground:rule
name: 租户唯一性校验
content: "对 uniSocialCreditCode / code / name / dbTenantCode / tenantFlgEn / devDomain / sitDomain / uatDomain / prdDomain 逐个做 count==0 校验；needHfive='Y' 时追加四个 H5 域名唯一；bandName 的唯一校验已被注释禁用"
impact: "保存/迁移去重；命中唯一约束给出『已存在，请确认!』"
field_targets:
  - tenant_setting_config.code
  - tenant_setting_config.db_tenant_code
  - tenant_setting_config.tenant_flg_en
  - tenant_setting_config.uni_social_credit_code
evidence: "code_path:TenantDomainService.java:checkUnique"
```
---END FILE---

---FILE: rules/rule_share_self_tenant.md---
---
type: rule
title: 自营假租户共享落表
page_key: rule_share_self_tenant
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [existEarlyLLsTenant, doSaveTenantShare, 自营假租户, 共享租户]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code_path:TenantDomainService.java:existEarlyLLsTenant / doSaveTenantShare"
contract_version: "0.1"
---

当同一 dbTenantCode 已存在主记录、但本次落库的 tenant_flg_en 与之不同、且既有记录 share_flag='Y' 时，判定为「自营假租户」：不新增 [[tenant_setting_config]] 主表记录，而是把 name / bandName / tenantFlgEn 写入 tenant_setting_config_share，并只在 share 表内做唯一校验，最后返回既有租户 id。

这条规则解释了为什么同一 db_tenant_code 下可以有多个 tenant_flg_en（见 [[tenant_flg_en]]），也决定了 share_flag 的语义：它是「允许挂多个项目标识」的开关。

## 需求背景
XYC 自营租户需要在一个数据租户下挂多个项目标识，但又不允许污染租户主配置（生效状态、灰度、运营邮件等应以主记录为准），因此把额外的项目标识下沉到共享表。

## 版本演进
v0.1（本页）：首版契约，锚点证据来自语义分析；共享表 tenant_setting_config_share 的字段清单未采集（见 REVIEW）。

```ground:rule
name: 自营假租户共享落表
content: "同 dbTenantCode 已存在主记录、且 tenant_flg_en 不同、且既有记录 share_flag='Y' 时判定为自营假租户：不新增主表，改写入 tenant_setting_config_share（仅对 name/bandName/tenantFlgEn 做 share 表内唯一校验），返回既有租户 id"
impact: "XYC 自营租户下可挂多个项目标识"
field_targets:
  - tenant_setting_config.db_tenant_code
  - tenant_setting_config.share_flag
  - tenant_setting_config_share.tenant_flg_en
evidence: "code_path:TenantDomainService.java:existEarlyLLsTenant / doSaveTenantShare"
```
---END FILE---

---REVIEW: rule | Excel 导入定位与写入范围---
语义分析中该规则条目被截断：content 尾部（"…project_code_requ" 处）与 evidence 字段均未采集完整，无法逐字回填 ground:rule 的 content / field_targets / evidence，因此本版暂不产出 rules/rule_tenant_config_excel_import.md。

已可确认的片段（逐字来自分析）：按 tenant_flg_en 查 tenant_setting_config（查不到报『租户不存在』）；projectCodeRequired 非空才覆盖；defaultProjectId 仅在数据库原值为 null 时写入，且只用 tenantProjectService.getById 校验存在性；空 projectMark 行在解析阶段被静默丢弃；每行异常写入错误列表并计入 failCount。待证据补全后再落页。
---END REVIEW---

---REVIEW: table | 被引用但未采集字段的表---
tenant_project / tenant_setting_config_share / operation_user / cust_project_rel 仅在概念边界（also_confused_with）与规则 field_targets 中作为引用对象出现（如 tenant_project.id、tenant_project.send_email、tenant_setting_config_share.tenant_flg_en、operation_user.operation_id、cust_project_rel.op_contact_a），语义分析未提供这些表的字段清单与证据，故本版不产出对应 table 页。
---END REVIEW---

---REVIEW: frontmatter | scope.databases 物理库名未采集---
语义分析只给出表名与代码模块（lowcode-pplatform-tenant-management、lowcode-pplatform-customer-management），未给出物理库名，所有页面 scope.databases 暂占位为 unknown，待确认后统一回填；同一表是否跨库（如租户库与客户库的关联字段）亦待确认。
---END REVIEW---