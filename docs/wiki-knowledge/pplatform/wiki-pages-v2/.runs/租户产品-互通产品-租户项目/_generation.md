---FILE: tables/tenant_product.md ---
---
type: table
title: 租户产品表
page_key: tenant_product
domain: 租户产品
status: draft
aliases: [租户产品, 租户产品配置, tenant_product]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - code:ProductOpenStatusEnum
contract_version: "0.1"
---

`tenant_product` 是租户级产品开通配置表：记录某租户开通了哪个平台产品、产品类型、开通状态与迁移标记。租户产品编码 `code` 为唯一键；`platform_product_id` 与 `tenant_id` 组成唯一键 tenant_product_id。该表向下被 [[tenant_project]] 通过 `product_id`、`ref_tenant_project_product_code` 引用，与 [[tenant_product_menu]] 共同决定租户可见菜单，并与 [[platform_product]]、[[tenant_interworking_product_term]] 区分"平台产品 / 租户产品 / 互通产品"三层概念。

## 需求背景
语义分析未附带需求文档（reqdoc）锚点，本节依据字段语义与状态机归纳：平台侧提供统一产品池（`platform_product_code` 实测 ACFLOW/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER/BEECREDIT 等），租户需要按自身业务选择开通（产品名称如应收易融、订单融资、融易单），且多级产品存在异步开通过程，因此需要 [[tenant_product_open_status]] 的三态表示与 `is_migratory`、`max_financing_amount_flag`、`max_financing_period` 等开通附加配置。

## 版本演进
`open_status` 的三态 N/P/Y 与代码枚举 ProductOpenStatusEnum 一致，`enable` 在库中全为 Y；`is_migratory` 的引入说明该表承接了历史数据迁移场景，`max_financing_amount_flag`、`max_financing_period` 的混存写值提示限额融资上线策略经历过口径调整。相关待确认项见 REVIEW。

```ground:table
table: tenant_product
fields:
  - name: id
    type: ""
    desc: 租户产品配置主键
    dict: ""
  - name: code
    type: ""
    desc: 租户产品编码，唯一键
    dict: ""
  - name: name
    type: ""
    desc: 租户产品名称，如应收易融、订单融资、融易单
    dict: ""
  - name: open_status
    type: ""
    desc: 租户产品开通状态，DB 实测 N/P/Y，对应 ProductOpenStatusEnum 未开通/开通中/已开通
    dict: ProductOpenStatusEnum
  - name: platform_product_code
    type: ""
    desc: 平台产品编号，DB 实测 ACFLOW/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER/BEECREDIT 等
    dict: ""
  - name: platform_product_id
    type: ""
    desc: 平台产品主键，与 tenant_id 组成唯一键 tenant_product_id
    dict: ""
  - name: ref_tenant_product_project_code
    type: ""
    desc: 租户产品-平台产品关联 code，DB 中为 platform_product 业务 code
    dict: ""
  - name: ref_tenant_product_tenant_setting_config
    type: ""
    desc: 租户-产品关联 tenant_setting_config code
    dict: ""
  - name: tenant_id
    type: ""
    desc: 租户 id
    dict: ""
  - name: product_cate
    type: ""
    desc: 产品类型，DB 实测 STRONG/WEAKLY/CREDIT
    dict: ""
  - name: is_migratory
    type: ""
    desc: 是否迁移标识，DB 实测 Y/N，Y 代表已迁移
    dict: ""
  - name: max_financing_amount_flag
    type: ""
    desc: 是否限额融资资金上线，DB 实测 N/Y/0/1 混存
    dict: ""
  - name: max_financing_period
    type: ""
    desc: 融资期限上限，DB 中既有 6/12/36 也有 6个月/12个月 等文本
    dict: ""
  - name: enable
    type: ""
    desc: 逻辑有效标记，DB 实测全部 Y
    dict: ""
```

---REVIEW: table | 租户产品表---
1. `scope.databases` 暂用代码模块标识 `lowcode-pplatform-customer-management`，语义分析未给出物理库名，需确认后回填。
2. `max_financing_amount_flag` 混存 N/Y/0/1、`max_financing_period` 混存数值与文本（6个月/12个月），是否为历史写值差异、是否统一口径与迁移，待确认。
---END REVIEW---

---END FILE---

---FILE: tables/tenant_product_menu.md ---
---
type: table
title: 租户产品菜单表
page_key: tenant_product_menu
domain: 租户产品
status: draft
aliases: [租户产品菜单, tenant_product_menu]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product_menu
contract_version: "0.1"
---

`tenant_product_menu` 描述"某个产品在某类企业角色下可见的菜单集合"，是产品开通后前端菜单渲染的配置来源，三者组合定位一条授权：`product_code`（产品）+ `company_type`（企业角色）+ `menu_id`（菜单）。产品维度对应 [[tenant_product]] 的产品编码体系，企业角色维度与 [[cust_project_rel]] 的 `company_type` 同源。

## 需求背景
语义分析未附带需求文档锚点，依据 DB 实测值归纳：不同角色的企业（核心企业、供应商、经销商、金融机构、平台运营方、公司/项目公司）在同一产品下看到的菜单不同，因此需要按 `company_type` 差异化配置菜单。

## 版本演进
语义分析未记录该表的版本演进；`product_code` 实测值覆盖 ACCOUNT_PRODUCT/BEECREDIT/RVSFACTOR_PC，说明菜单配置随产品线扩展逐批追加。

```ground:table
table: tenant_product_menu
fields:
  - name: product_code
    type: ""
    desc: 产品 code，DB 实测 ACCOUNT_PRODUCT/BEECREDIT/RVSFACTOR_PC
    dict: ""
  - name: company_type
    type: ""
    desc: 企业角色，DB 实测 CORE/SUPPLIER/DEALER/FINANCE/PLATFORM_OPERATOR/CORPORATION_COMPANY/PROJECT_COMPANY 等
    dict: ""
  - name: menu_id
    type: ""
    desc: 菜单 id
    dict: ""
```

---END FILE---

---FILE: tables/tenant_project.md ---
---
type: table
title: 租户项目表
page_key: tenant_project
domain: 租户项目
status: draft
aliases: [租户项目, 项目, tenant_project]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_project
  - code:ProjectStatusEnum
  - code:PlatformConstant
contract_version: "0.1"
---

`tenant_project` 是项目主数据表，承载项目的状态、来源渠道、运营/查验/风控对接人、自定义字段与审批回填信息。项目通过 `product_id`／`ref_tenant_project_product_code` 关联 [[tenant_product]]，通过 `ref_tenant_project_platform_product`／`platform_product_code` 关联 [[platform_product]]，通过 `ref_tenant_project_tenant_code` 关联租户，通过 [[cust_project_rel]] 关联参与企业。状态口径见 [[project_effective]]、[[project_to_be_effective]]、[[project_invalid]]、[[valid_project]]。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：项目需支持导入（`project_code`、`custom_field_one/two/three` 500 字限制、`bussiness_project_relation` 50 字限制）、导出（`op_contact_a/b` 存 ID 导出转姓名、`is_prd` 转是/否）、企微立项审批回填（`wechat_audit_no`、`wechat_audit_pass_time`）以及项目配置版本化（`config_json`、`project_config_version`），并要求逻辑删除（`enable`）与生效/失效状态流转（[[tenant_project_status]]）。

## 版本演进
语义分析未记录该表的版本演进；`source` 的 DB 分布（pplatform 1532、ACFLOW 1255、RVSFACTOR_PC 480、ORDER 226、STORAGE 8）与 `PlatformConstant.PPLATFORM_SYSTEM=pplatform` 写值说明项目来源随产品线扩容逐步增多，`source` 字段语义由"项目来源"扩展为"产品来源"。

```ground:table
table: tenant_project
fields:
  - name: id
    type: ""
    desc: 租户项目主键
    dict: ""
  - name: name
    type: ""
    desc: 项目名称
    dict: ""
  - name: project_status
    type: ""
    desc: 项目状态，代码 ProjectStatusEnum：0 待生效、1 已生效、2 已失效；导出代码按 1 判断已生效
    dict: ProjectStatusEnum
  - name: source
    type: ""
    desc: 项目来源/产品来源，DB 实测 pplatform 1532、ACFLOW 1255、RVSFACTOR_PC 480、ORDER 226、STORAGE 8；代码存在 PlatformConstant.PPLATFORM_SYSTEM=pplatform 写值
    dict: ""
  - name: channel_code
    type: ""
    desc: 项目码/渠道码，依据 queryByChannelCode、导出 setChannelCode(project.getChannelCode())
    dict: ""
  - name: project_code
    type: ""
    desc: 项目编码，导出查询条件使用 project_code
    dict: ""
  - name: enable
    type: ""
    desc: 逻辑有效标记，导出只查 enable='Y'，删除方法走逻辑删除
    dict: ""
  - name: is_prd
    type: ""
    desc: 是否生产数据，导出判断 Y 为是、N 为否；洞察平台导出另有 1/0 兼容逻辑
    dict: ""
  - name: project_tag
    type: ""
    desc: 项目标签，导入校验可选值生产项目/测试项目/暂停项目，存枚举值
    dict: ""
  - name: op_contact_a
    type: ""
    desc: 运营对接人A，存运营人员 ID，导出转姓名；导入按姓名转 ID
    dict: ""
  - name: op_contact_b
    type: ""
    desc: 运营对接人B，存 JSON 数组字符串，导出转逗号分隔姓名
    dict: ""
  - name: op_contact_a_group
    type: ""
    desc: 运营组别，跟随运营对接人A 变化，为空时置空
    dict: ""
  - name: verification_contact
    type: ""
    desc: 查验对接人，存运营人员 ID
    dict: ""
  - name: verification_contact_group
    type: ""
    desc: 查验组别
    dict: ""
  - name: risk_control_contact_a
    type: ""
    desc: 风控对接人A，存运营人员 ID
    dict: ""
  - name: risk_control_contact_b
    type: ""
    desc: 风控对接人B，存 JSON 数组字符串
    dict: ""
  - name: risk_control_contact_a_group
    type: ""
    desc: 风控组别
    dict: ""
  - name: solution_manager
    type: ""
    desc: 方案经理
    dict: ""
  - name: business_manager
    type: ""
    desc: 业务经理
    dict: ""
  - name: business_group
    type: ""
    desc: 关联业务部门
    dict: ""
  - name: custom_field_one
    type: ""
    desc: 自定义字段一，导入限制 500 字
    dict: ""
  - name: custom_field_two
    type: ""
    desc: 自定义字段二，导入限制 500 字
    dict: ""
  - name: custom_field_three
    type: ""
    desc: 自定义字段三，导入限制 500 字
    dict: ""
  - name: bussiness_project_relation
    type: ""
    desc: 运营项目归属，导入限制 50 字
    dict: ""
  - name: wechat_audit_no
    type: ""
    desc: 企微审批编号/立项审批编号，审批提交可回填
    dict: ""
  - name: wechat_audit_pass_time
    type: ""
    desc: 项目立项审批通过时间
    dict: ""
  - name: config_json
    type: ""
    desc: 项目配置 JSON，信用证生效前校验其中项目配置状态
    dict: ""
  - name: project_config_version
    type: ""
    desc: 项目配置版本，生效项目查询按版本过滤
    dict: ""
  - name: product_id
    type: ""
    desc: 关联 tenant_product.id
    dict: ""
  - name: tenant_id
    type: ""
    desc: 租户 id
    dict: ""
  - name: ref_tenant_project_product_code
    type: ""
    desc: 关联租户产品 code，创建、失效、有效项目查询使用
    dict: ""
  - name: ref_tenant_project_tenant_code
    type: ""
    desc: 关联租户 code，创建时查租户信息
    dict: ""
  - name: ref_tenant_project_platform_product
    type: ""
    desc: 关联平台产品 code，导出产品类型、有效项目查询使用
    dict: ""
  - name: platform_product_code
    type: ""
    desc: 平台产品 code，审批与项目推送中使用
    dict: ""
  - name: db_tenant_code
    type: ""
    desc: 数据租户标识
    dict: ""
  - name: app_tenant_code
    type: ""
    desc: 逻辑租户标识
    dict: ""
```

---REVIEW: table | 租户项目表---
1. `project_tag` 字段语义写"存枚举值"，而 [[project_tag_production]] 等口径以中文值（生产项目/测试项目/暂停项目）作谓词，实际落库是枚举码还是中文文本需与写值点核对（本页按语义分析原文保留）。
2. `is_prd` 存在 Y/N 与洞察平台导出的 1/0 两套兼容逻辑，是否双写口径待确认。
---END REVIEW---

---END FILE---

---FILE: tables/cust_project_rel.md ---
---
type: table
title: 项目企业关联表
page_key: cust_project_rel
domain: 租户项目
status: draft
aliases: [项目企业关联, cust_project_rel]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:cust_project_rel
  - code:CustCompanyTypeEnum
contract_version: "0.1"
---

`cust_project_rel` 是项目与企业（客户）的多对多关联表，记录某企业在某项目下承担的角色、企业编码以及该项目-企业维度的运营/查验/风控对接人。`project_id` 对应 [[tenant_project]] 主键，`product_id` 对应 [[tenant_product]] 主键，`ref_cust_project_rel_cust_company_info` 对应 [[cust_company_info]] 的 `code`。角色口径见 [[role_core_company]]、[[role_finance_company]]，有效数据口径见 [[valid_cust_project_rel]]。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：导出关联企业时需要按角色过滤（CORE/FINANCE），且对接人信息需下沉到"项目 × 企业"维度（`op_contact_a/b`、`verification_contact`、`risk_control_contact_a/b` 及其组别），因此从项目级对接人拆出一张关联维度表。

## 版本演进
语义分析未记录该表的版本演进；查询与导出统一带 `enable='Y'`，说明该表自建立起即采用逻辑有效标记而非物理删除。

```ground:table
table: cust_project_rel
fields:
  - name: project_id
    type: ""
    desc: 项目 id，String 类型，对应 tenant_project.id
    dict: ""
  - name: product_id
    type: ""
    desc: 租户产品 id，对应 tenant_product.id
    dict: ""
  - name: company_type
    type: ""
    desc: 企业在该项目下的角色，如 CORE/FINANCE
    dict: CustCompanyTypeEnum
  - name: ref_cust_project_rel_cust_company_info
    type: ""
    desc: 企业编码，关联 cust_company_info.code
    dict: ""
  - name: op_contact_a
    type: ""
    desc: 项目企业关联维度的运营对接人A
    dict: ""
  - name: op_contact_b
    type: ""
    desc: 项目企业关联维度的运营对接人B
    dict: ""
  - name: op_contact_a_group
    type: ""
    desc: 项目企业关联维度的运营组别
    dict: ""
  - name: verification_contact
    type: ""
    desc: 项目企业关联维度的查验对接人
    dict: ""
  - name: risk_control_contact_a
    type: ""
    desc: 项目企业关联维度的风控对接人A
    dict: ""
  - name: risk_control_contact_b
    type: ""
    desc: 项目企业关联维度的风控对接人B
    dict: ""
  - name: enable
    type: ""
    desc: 逻辑有效标记，查询导出时用 enable='Y'
    dict: ""
```

---END FILE---

---FILE: tables/tenant_interworking_product.md ---
---
type: table
title: 租户互通产品表
page_key: tenant_interworking_product
domain: 互通产品
status: draft
aliases: [租户互通产品, tenant_interworking_product]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_interworking_product
  - code:ProductOpenStatusEnum
contract_version: "0.1"
---

`tenant_interworking_product` 记录租户维度的互通产品开通情况，是 [[interworking_product_term]] 在租户侧的落库表。开通状态 `open_status` 由 ProductOpenStatusEnum 写值，口径见 [[tenant_interworking_product_opened]]。与 [[tenant_product]] 的区别在于产品线：互通产品独立于租户通用产品配置。

## 需求背景
语义分析未附带需求文档锚点，依据字段语义归纳：互通产品线需要独立于通用产品记录开通过程，因此复用 ProductOpenStatusEnum 的状态语义，但独立建表。

## 版本演进
语义分析未记录该表的版本演进。

```ground:table
table: tenant_interworking_product
fields:
  - name: id
    type: ""
    desc: 租户互通产品主键
    dict: ""
  - name: open_status
    type: ""
    desc: 租户互通产品开通状态，代码写值使用 ProductOpenStatusEnum
    dict: ProductOpenStatusEnum
  - name: platform_product_code
    type: ""
    desc: 平台产品 code
    dict: ""
  - name: tenant_id
    type: ""
    desc: 租户 id
    dict: ""
```

---END FILE---

---FILE: tables/cust_interworking_product.md ---
---
type: table
title: 客户互通产品表
page_key: cust_interworking_product
domain: 互通产品
status: draft
aliases: [客户互通产品, cust_interworking_product]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:cust_interworking_product
  - code:CustProductActiveConstant
contract_version: "0.1"
---

`cust_interworking_product` 记录客户维度的互通产品开通情况，是 [[interworking_product_term]] 在客户侧的落库表。开通状态使用另一套取值 `OPENED/OPENING/NOT_OPENED`（CustProductActiveConstant），与租户侧 ProductOpenStatusEnum 的 N/P/Y 不通用，口径见 [[cust_interworking_product_opened]]，两端对照见 [[cust_product_active_constant]]。

## 需求背景
语义分析未附带需求文档锚点，依据 DB 与代码证据归纳：客户侧互通产品开通需要"带客户确认 forams"的中间态，故状态集合与租户侧不同。

## 版本演进
语义分析未记录该表的版本演进；DB 实测仅见 OPENED，其余两态由常量类定义。

```ground:table
table: cust_interworking_product
fields:
  - name: open_status
    type: ""
    desc: 客户互通产品开通状态，DB 实测 OPENED，代码使用 CustProductActiveConstant.OPENED/OPENING/NOT_OPENED
    dict: CustProductActiveConstant
```

---END FILE---

---FILE: tables/tenant_project_approval.md ---
---
type: table
title: 项目上线审批表
page_key: tenant_project_approval
domain: 租户项目
status: draft
aliases: [项目上线审批, tenant_project_approval]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

`tenant_project_approval` 承载项目正式上线的审批工作流状态（`wf_status`），是 [[project_approval_wf_status]] 状态机的落库表，审批通过的终态会驱动 [[tenant_project]] 的 `project_status` 流转。当前语义分析仅覆盖 `wf_status` 字段，其余字段未提供。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：项目上线必须先发起审批，正式发起前可暂存（PENDING 保持），审批完成/终止分别落到 FINISHED/TERMINATED。

## 版本演进
语义分析未记录该表的版本演进。

```ground:table
table: tenant_project_approval
fields:
  - name: wf_status
    type: ""
    desc: 项目上线审批工作流状态，取值 PENDING 待发起、RUNNING 审批中、FINISHED 已完成、TERMINATED 已终止
    dict: ""
```

---REVIEW: table | 项目上线审批表---
1. `wf_status` 的枚举类名与其余字段未在语义分析中给出，本页字段清单不完整（仅一个字段），需补充后回填。
2. 表名与列名来自代码引用（tenant_project_approval.wf_status），未经 DB 实测确认。
---END REVIEW---

---END FILE---

---FILE: tables/platform_product.md ---
---
type: table
title: 平台产品表
page_key: platform_product
domain: 租户产品
status: draft
aliases: [平台产品, platform_product]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:PlatformProductTypeEnum
contract_version: "0.1"
---

`platform_product` 是平台级产品定义表，被 [[tenant_product]]（`platform_product_code`、`ref_tenant_product_project_code`）与 [[tenant_project]]（`ref_tenant_project_platform_product`、`platform_product_code`）引用。产品类型 `product_type` 区分互通产品与通用产品，口径见 [[platform_product_interworking]]、[[platform_product_general]]。

## 需求背景
语义分析未附带需求文档锚点，仅依据 PlatformProductTypeEnum 的使用点归纳：产品查询需要按 `product_type` 分流（互通产品线 / 通用产品线），以支撑 [[interworking_product_term]] 与 [[tenant_product]] 的边界。

## 版本演进
语义分析未记录该表的版本演进；本页仅覆盖被证据引用的 `product_type` 字段。

```ground:table
table: platform_product
fields:
  - name: product_type
    type: ""
    desc: 平台产品类型，代码 PlatformProductTypeEnum.INTERWORKING 用于互通产品查询、GENERAL 用于通用产品查询
    dict: PlatformProductTypeEnum
```

---END FILE---

---FILE: enums/ProductOpenStatusEnum.md ---
---
type: enum
title: 开通状态枚举（ProductOpenStatusEnum）
page_key: ProductOpenStatusEnum
domain: 租户产品
status: draft
aliases: [ProductOpenStatusEnum, 开通状态, 产品开通状态]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProductOpenStatusEnum
  - db:tenant_product
  - db:tenant_interworking_product
contract_version: "0.1"
---

ProductOpenStatusEnum 表示"产品开通状态"，同时被租户通用产品（[[tenant_product]]）与租户互通产品（[[tenant_interworking_product]]）使用，状态流转见 [[tenant_product_open_status]]，口径见 [[tenant_product_opened]]、[[tenant_product_opening]]、[[tenant_product_not_opened]]、[[tenant_interworking_product_opened]]。

## 需求背景
语义分析未附带需求文档锚点；由 [[tenant_product_open_status]] 的迁移可见，枚举需要区分"未开通"与"开通中"，以承载多级产品异步开通回调（ACFLOW/ORDER）期间的中间态。

## 版本演进
DB 实测分布为 N/P/Y，与枚举取值一致；`P`（开通中）的存在说明枚举并非一次性写入的终态标记。

```ground:enum
java_name: ProductOpenStatusEnum
stored_as: tenant_product.open_status
values:
  - value: N
    label: 未开通
    note: DB 分布实测存在
  - value: P
    label: 开通中
    note: DB 分布实测存在；多级产品开通期间写入
  - value: Y
    label: 已开通
    note: DB 分布实测存在
note: 同一枚举被 tenant_product.open_status 与 tenant_interworking_product.open_status 复用；写成 N/P/Y 单字符。
```

---END FILE---

---FILE: enums/ProjectStatusEnum.md ---
---
type: enum
title: 项目状态枚举（ProjectStatusEnum）
page_key: ProjectStatusEnum
domain: 租户项目
status: draft
aliases: [ProjectStatusEnum, 项目状态]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectStatusEnum
  - code:ProjectReportApplication
contract_version: "0.1"
---

ProjectStatusEnum 表示 [[tenant_project]] 的项目状态，流转见 [[tenant_project_status]]，口径见 [[project_effective]]、[[project_to_be_effective]]、[[project_invalid]]。导出代码按 `1` 判断"已生效"，因此该枚举的取值是报表口径的直接依据。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：项目从创建到可被业务使用需要"待生效 → 已生效"的显式生效动作，失效后保留数据（`2`）以支持重新生效（见 [[project_approval_wf_status]]）。

## 版本演进
语义分析未记录该枚举的版本演进；代码常量名 `INVLIAD`（原文拼写）与 `TO_BE_EFFECTIVE` 一并保留。

```ground:enum
java_name: ProjectStatusEnum
stored_as: tenant_project.project_status
values:
  - value: "0"
    label: 待生效
  - value: "1"
    label: 已生效
    note: 导出代码按 1 判断已生效
  - value: "2"
    label: 已失效
note: 常量名 INVLIAD 为代码原文拼写。
```

---END FILE---

---FILE: enums/CustProductActiveConstant.md ---
---
type: enum
title: 客户产品开通常量（CustProductActiveConstant）
page_key: CustProductActiveConstant
domain: 互通产品
status: draft
aliases: [CustProductActiveConstant, 客户互通产品开通状态]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:CustProductActiveConstant
  - db:cust_interworking_product
contract_version: "0.1"
---

CustProductActiveConstant 定义 [[cust_interworking_product]] 的开通状态取值，口径见 [[cust_interworking_product_opened]]。其取值集合与 [[ProductOpenStatusEnum]]（N/P/Y）不同，两者不可互换。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：客户侧开通需要"带客户确认 forams"的中间态 OPENING，用以表示已发起、待客户确认的开通过程。

## 版本演进
DB 实测仅出现 OPENED；NOT_OPENED/OPENING 由常量类定义，是否有历史存量数据待确认。

```ground:enum
java_name: CustProductActiveConstant
stored_as: cust_interworking_product.open_status
values:
  - value: NOT_OPENED
    label: 未开通
  - value: OPENING
    label: 开通中：带客户确认 forams
  - value: OPENED
    label: 已开通
    note: DB 分布实测 OPENED
note: 与租户侧 ProductOpenStatusEnum 取值不同，禁止混用。
```

---END FILE---

---FILE: enums/PlatformProductTypeEnum.md ---
---
type: enum
title: 平台产品类型枚举（PlatformProductTypeEnum）
page_key: PlatformProductTypeEnum
domain: 租户产品
status: draft
aliases: [PlatformProductTypeEnum, 平台产品类型]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:PlatformProductTypeEnum
contract_version: "0.1"
---

PlatformProductTypeEnum 定义 [[platform_product]] 的产品类型，用于产品查询的分流：INTERWORKING 面向互通产品线（[[interworking_product_term]]），GENERAL 面向通用产品线。口径见 [[platform_product_interworking]]、[[platform_product_general]]。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：产品查询需要按类型区分互通与通用，避免互通产品被纳入通用产品查询结果。

## 版本演进
语义分析未记录该枚举的版本演进；本页仅覆盖被证据引用的两个取值。

```ground:enum
java_name: PlatformProductTypeEnum
stored_as: platform_product.product_type
values:
  - value: INTERWORKING
    note: 用于互通产品查询
  - value: GENERAL
    note: 用于通用产品查询
note: 中文标签在语义分析中未给出，页面标签沿用对应口径名（平台互通产品类型/平台通用产品类型）。
```

---END FILE---

---FILE: enums/CustCompanyTypeEnum.md ---
---
type: enum
title: 企业角色枚举（CustCompanyTypeEnum）
page_key: CustCompanyTypeEnum
domain: 租户项目
status: draft
aliases: [CustCompanyTypeEnum, 企业角色]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:CustCompanyTypeEnum
  - db:tenant_product_menu
contract_version: "0.1"
---

CustCompanyTypeEnum 表示企业在项目/产品下的角色，出现在 [[cust_project_rel]]（`company_type`，口径见 [[role_core_company]]、[[role_finance_company]]）与 [[tenant_product_menu]]（按角色配置菜单）。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：导出关联企业时需按角色过滤 CORE/FINANCE，菜单配置需覆盖更多角色，因此角色枚举被多张表复用。

## 版本演进
语义分析未记录该枚举的版本演进；DB 实测角色值多于代码证据中引用的两个（见 note）。

```ground:enum
java_name: CustCompanyTypeEnum
stored_as: cust_project_rel.company_type
values:
  - value: CORE
    label: 核心企业
    note: 导出关联企业时过滤
  - value: FINANCE
    label: 金融机构
    note: 导出关联企业时过滤
note: tenant_product_menu.company_type 的 DB 实测值另含 SUPPLIER/DEALER/PLATFORM_OPERATOR/CORPORATION_COMPANY/PROJECT_COMPANY 等，是否同属本枚举待核。
```

---END FILE---

---FILE: concepts/tenant_product_term.md ---
---
type: concept
title: 租户产品
page_key: tenant_product_term
domain: 租户产品
status: draft
aliases: [tenant_product, 租户产品配置, 租户产品]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - db:tenant_interworking_product
  - db:cust_interworking_product
maps_to: tenant_product.*
field_targets: [tenant_product.code, tenant_product.open_status, tenant_product.enable, tenant_product.platform_product_code]
adjudication: boundary
boundary: tenant_product 是租户级通用产品开通表；tenant_interworking_product/cust_interworking_product 是互通产品线，产品查询扩展点 scenario=INTERWORKING/GENERAL 区分。
also_confused_with: [tenant_interworking_product, cust_interworking_product]
contract_version: "0.1"
---

"租户产品"指租户开通了哪个平台产品的记录，落在 [[tenant_product]] 表；判定期（开通状态）见 [[tenant_product_open_status]]。该词容易与互通产品线混淆，判别边界见下方 frontmatter 的 boundary。注意：语义分析给出的 `maps_to` 为表级 `tenant_product`，本页按表级映射记作 `tenant_product.*`，具体字段见 `field_targets`。

## 需求背景
语义分析未附带需求文档锚点；术语桥的作用是让"租户产品/互通产品/客户互通产品"在口径与查询中不串用。

## 版本演进
语义分析未记录该术语的版本演进。

---END FILE---

---FILE: concepts/interworking_product_term.md ---
---
type: concept
title: 互通产品
page_key: interworking_product_term
domain: 互通产品
status: draft
aliases: [互联互通产品, 互通产品线]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_interworking_product
  - db:cust_interworking_product
  - code:PlatformProductTypeEnum
maps_to: tenant_interworking_product.*
field_targets: [tenant_interworking_product.open_status, cust_interworking_product.open_status]
adjudication: boundary
boundary: 互通产品分租户侧 tenant_interworking_product 与客户侧 cust_interworking_product，两端状态常量不同；与租户通用产品 tenant_product 通过产品查询扩展点 scenario=INTERWORKING/GENERAL 区分。
also_confused_with: [tenant_product]
contract_version: "0.1"
---

"互通产品"是与租户通用产品并列的产品线，租户侧落 [[tenant_interworking_product]]（状态见 [[tenant_interworking_product_opened]]），客户侧落 [[cust_interworking_product]]（状态见 [[cust_interworking_product_opened]]）。产品类型侧由 [[PlatformProductTypeEnum]] 的 INTERWORKING 标记。

## 需求背景
语义分析未附带需求文档锚点；该术语桥用于防止把互通产品误当作 [[tenant_product_term]] 处理。

## 版本演进
语义分析未记录该术语的版本演进。

---REVIEW: concept | 互通产品---
语义分析中 term_bridges 的"互通产品"条目被截断（原文止于 aliases 片段），本页 aliases/boundary 依据"租户产品"条目的 also_confused_with 与 adjudication 反向归纳，需以完整条目校正。
---END REVIEW---

---END FILE---

---FILE: processes/tenant_product_open_status.md ---
---
type: process
title: 租户产品开通状态流转
page_key: tenant_product_open_status
domain: 租户产品
status: draft
aliases: [租户产品开通状态, tenant_product.open_status 状态机]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - code:ProductOpenStatusEnum
  - code:TenantProductApplication
contract_version: "0.1"
---

描述 [[tenant_product]] 的 `open_status` 如何从"未开通"经过"开通中"到达"已开通"，以及取消开通的回退。取值定义见 [[ProductOpenStatusEnum]]，单态口径见 [[tenant_product_not_opened]]、[[tenant_product_opening]]、[[tenant_product_opened]]、[[valid_tenant_product]]。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：ACFLOW/ORDER 等产品为多级产品，开通需异步回调后置成功，因此必须有 `P`（开通中）中间态；非多级产品可直接由 N 到 Y。

## 版本演进
语义分析未记录该状态机的版本演进。

```ground:process
name: 租户产品开通状态
field: tenant_product.open_status
states:
  - value: N
    label: 未开通
    source: db_dist
  - value: P
    label: 开通中
    source: code_enum
  - value: Y
    label: 已开通
    source: db_dist
transitions:
  - from: N
    event: 开通ACFLOW/ORDER多级产品
    to: P
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:334"
  - from: P
    event: 多级回调后置成功
    to: Y
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
  - from: N
    event: 非多级产品直接生效
    to: Y
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
  - from: Y
    event: 取消开通产品
    to: N
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:cancel"
```

---END FILE---

---FILE: processes/tenant_project_status.md ---
---
type: process
title: 租户项目状态流转
page_key: tenant_project_status
domain: 租户项目
status: draft
aliases: [项目状态流转, tenant_project.project_status 状态机]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectStatusEnum
  - code:TenantProjectApplication
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

描述 [[tenant_project]] 的 `project_status` 生命周期。取值定义见 [[ProjectStatusEnum]]，单态口径见 [[project_to_be_effective]]、[[project_effective]]、[[project_invalid]]。该状态与 [[project_approval_wf_status]] 存在耦合：上线审批终态通过会驱动项目生效或重新生效，而非新增项目正式发起上线审批会使已生效项目转为已失效。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：项目创建后处于待生效，需显式生效才能被业务引用；已生效项目在再次上线审批期间会先失效，审批通过后再回到已生效。

## 版本演进
语义分析未记录该状态机的版本演进。

```ground:process
name: 租户项目状态
field: tenant_project.project_status
states:
  - value: "0"
    label: 待生效
    source: code_enum
  - value: "1"
    label: 已生效
    source: code_enum
  - value: "2"
    label: 已失效
    source: code_enum
transitions:
  - from: "0"
    event: 项目生效
    to: "1"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/TenantProjectApplication.java:effective"
  - from: "1"
    event: 项目失效
    to: "2"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/TenantProjectApplication.java:invalid"
  - from: "1"
    event: 上线审批终态通过
    to: "1"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished"
  - from: "2"
    event: 上线审批终态通过重新生效
    to: "1"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished"
  - from: "1"
    event: 非新增项目正式发起上线审批
    to: "2"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:663"
```

---END FILE---

---FILE: processes/project_approval_wf_status.md ---
---
type: process
title: 项目上线审批工作流状态流转
page_key: project_approval_wf_status
domain: 租户项目
status: draft
aliases: [项目上线审批状态, tenant_project_approval.wf_status 状态机]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

描述 [[tenant_project_approval]] 的 `wf_status` 流转：待发起 → 审批中 → 已完成/已终止，暂存保持待发起。审批完成会触发 [[tenant_project_status]] 的生效/重新生效，口径见 [[approval_running]]。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：项目上线必须先走审批，允许暂存（不进入 RUNNING），正式提交才启动工作流；终止与完成是两个不同终态。

## 版本演进
语义分析未记录该状态机的版本演进。

```ground:process
name: 项目上线审批工作流状态
field: tenant_project_approval.wf_status
states:
  - value: PENDING
    label: 待发起
    source: code_enum
  - value: RUNNING
    label: 审批中
    source: code_enum
  - value: FINISHED
    label: 已完成
    source: code_enum
  - value: TERMINATED
    label: 已终止
    source: code_enum
transitions:
  - from: PENDING
    event: 正式提交并启动工作流
    to: RUNNING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:startWorkflowAndUpdateStatus"
  - from: PENDING
    event: 暂存
    to: PENDING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:submit"
  - from: RUNNING
    event: 审批完成
    to: FINISHED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:handleFlowAndNodeStatus"
  - from: RUNNING
    event: 审批终止
    to: TERMINATED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:handleFlowAndNodeStatus"
```

---REVIEW: process | 项目上线审批工作流状态流转---
语义分析未给出 `wf_status` 的枚举类名与表字段清单（仅给出字段引用），枚举页暂缺；需补充枚举类与完整取值后建 [[enums]] 页。
---END REVIEW---

---END FILE---

---FILE: processes/cust_interworking_product_open_status.md ---
---
type: process
title: 客户互通产品开通状态
page_key: cust_interworking_product_open_status
domain: 互通产品
status: draft
aliases: [客户互通产品开通状态, cust_interworking_product.open_status 状态机]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:CustProductActiveConstant
  - db:cust_interworking_product
contract_version: "0.1"
---

描述 [[cust_interworking_product]] 的 `open_status` 取值集合（NOT_OPENED/OPENING/OPENED，见 [[CustProductActiveConstant]]）。语义分析未提供迁移事件，故本页只固化状态集合，口径见 [[cust_interworking_product_opened]]。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：客户侧开通存在"带客户确认 forams"的 OPENING 中间态。

## 版本演进
语义分析未记录该状态机的版本演进；DB 仅有 OPENED 分布。

```ground:process
name: 客户互通产品开通状态
field: cust_interworking_product.open_status
states:
  - value: NOT_OPENED
    label: 未开通
    source: code_enum
  - value: OPENING
    label: 开通中：带客户确认 forams
    source: code_enum
  - value: OPENED
    label: 已开通
    source: db_dist
transitions: []
```

---END FILE---

---FILE: calibers/tenant_product_opened.md ---
---
type: caliber
title: 口径：租户产品已开通
page_key: tenant_product_opened
domain: 租户产品
status: draft
aliases: [租户产品已开通, 产品已开通]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - code:ProductOpenStatusEnum
contract_version: "0.1"
---

判定 [[tenant_product]] 中"已开通"的租户产品，是 [[tenant_product_open_status]] 的终态，对应枚举 [[ProductOpenStatusEnum]] 的 Y。与开通中（[[tenant_product_opening]]）、未开通（[[tenant_product_not_opened]]）互斥。

## 需求背景
语义分析未附带需求文档锚点；该口径用于产品开通情况统计与下游产品校验，避免把开通中的租户误判为已开通。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 租户产品已开通
predicate: "tenant_product.open_status = 'Y'"
scope: tenant_product
evidence: "db+code:ProductOpenStatusEnum.Y 与 DB 分布 Y"
```

---END FILE---

---FILE: calibers/tenant_product_opening.md ---
---
type: caliber
title: 口径：租户产品开通中
page_key: tenant_product_opening
domain: 租户产品
status: draft
aliases: [租户产品开通中, 产品开通中]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - code:ProductOpenStatusEnum
contract_version: "0.1"
---

判定 [[tenant_product]] 中处于"开通中"的记录，对应 [[ProductOpenStatusEnum]] 的 P，由多级产品开通回调期间的中间态产生，见 [[tenant_product_open_status]]。

## 需求背景
语义分析未附带需求文档锚点；该口径用于识别已发起但尚未回调成功的产品开通，避免误计为已开通（[[tenant_product_opened]]）。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 租户产品开通中
predicate: "tenant_product.open_status = 'P'"
scope: tenant_product
evidence: "db+code:ProductOpenStatusEnum.P 与 DB 分布 P"
```

---END FILE---

---FILE: calibers/tenant_product_not_opened.md ---
---
type: caliber
title: 口径：租户产品未开通
page_key: tenant_product_not_opened
domain: 租户产品
status: draft
aliases: [租户产品未开通, 产品未开通]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - code:ProductOpenStatusEnum
contract_version: "0.1"
---

判定 [[tenant_product]] 中"未开通"的记录，对应 [[ProductOpenStatusEnum]] 的 N；取消开通会回退到该态（见 [[tenant_product_open_status]]）。

## 需求背景
语义分析未附带需求文档锚点；该口径是产品开通引导与权限判定的默认态。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 租户产品未开通
predicate: "tenant_product.open_status = 'N'"
scope: tenant_product
evidence: "db+code:ProductOpenStatusEnum.N 与 DB 分布 N"
```

---END FILE---

---FILE: calibers/valid_tenant_product.md ---
---
type: caliber
title: 口径：有效租户产品
page_key: valid_tenant_product
domain: 租户产品
status: draft
aliases: [有效租户产品]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
contract_version: "0.1"
---

判定 [[tenant_product]] 中未被逻辑删除的记录。该口径与开通状态口径（[[tenant_product_opened]] 等）正交，是查询 [[tenant_project]] 产品维度时的前置过滤。

## 需求背景
语义分析未附带需求文档锚点；`enable` 为全表逻辑有效标记，用于统一逻辑删除语义。

## 版本演进
语义分析未记录该口径的版本演进；DB 实测 `enable` 全为 Y，暂无 N 的实测样本。

```ground:caliber
name: 有效租户产品
predicate: "tenant_product.enable = 'Y'"
scope: tenant_product
evidence: "db:enable 全为 Y"
```

---END FILE---

---FILE: calibers/project_effective.md ---
---
type: caliber
title: 口径：项目已生效
page_key: project_effective
domain: 租户项目
status: draft
aliases: [项目已生效, 已生效项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectStatusEnum
  - code:ProjectReportApplication
contract_version: "0.1"
---

判定 [[tenant_project]] 中已生效的项目，对应 [[ProjectStatusEnum]] 的 1。导出侧按 1 直接转"已生效"，因此该口径同时是报表口径，流转见 [[tenant_project_status]]。

## 需求背景
语义分析未附带需求文档锚点；只有已生效项目才允许被业务单据引用。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 项目已生效
predicate: "tenant_project.project_status = '1'"
scope: tenant_project
evidence: "code:ProjectStatusEnum.EFFECTIVE; ProjectReportApplication 按 1 转已生效"
```

---END FILE---

---FILE: calibers/project_to_be_effective.md ---
---
type: caliber
title: 口径：项目待生效
page_key: project_to_be_effective
domain: 租户项目
status: draft
aliases: [项目待生效, 待生效项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectStatusEnum
contract_version: "0.1"
---

判定 [[tenant_project]] 中已创建但尚未生效的项目，对应 [[ProjectStatusEnum]] 的 0，流转见 [[tenant_project_status]]。

## 需求背景
语义分析未附带需求文档锚点；待生效项目需经生效动作或上线审批通过后才进入 [[project_effective]]。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 项目待生效
predicate: "tenant_project.project_status = '0'"
scope: tenant_project
evidence: "code:ProjectStatusEnum.TO_BE_EFFECTIVE"
```

---END FILE---

---FILE: calibers/project_invalid.md ---
---
type: caliber
title: 口径：项目已失效
page_key: project_invalid
domain: 租户项目
status: draft
aliases: [项目已失效, 已失效项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectStatusEnum
contract_version: "0.1"
---

判定 [[tenant_project]] 中已失效的项目，对应 [[ProjectStatusEnum]] 的 2（常量名 INVLIAD 为代码原文拼写）。失效项目在上线审批终态通过后可重新生效，见 [[tenant_project_status]]。

## 需求背景
语义分析未附带需求文档锚点；项目失效采用状态标记而非删除，以支持重新生效与历史追溯。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 项目已失效
predicate: "tenant_project.project_status = '2'"
scope: tenant_project
evidence: "code:ProjectStatusEnum.INVLIAD"
```

---END FILE---

---FILE: calibers/valid_project.md ---
---
type: caliber
title: 口径：有效项目
page_key: valid_project
domain: 租户项目
status: draft
aliases: [有效项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:exportProjectInfo
  - code:updateProjectData
contract_version: "0.1"
---

判定 [[tenant_project]] 中未被逻辑删除的项目（`enable='Y'`）。导出与更新任务均以此为准，是 [[project_effective]] 之外的另一层过滤。

## 需求背景
语义分析未附带需求文档锚点；项目删除走逻辑删除，查询与导出必须显式带上有效标记。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 有效项目
predicate: "tenant_project.enable = 'Y'"
scope: tenant_project
evidence: "code:exportProjectInfo/updateProjectData 均按 enable='Y' 查询"
```

---END FILE---

---FILE: calibers/project_production_data.md ---
---
type: caliber
title: 口径：项目生产数据
page_key: project_production_data
domain: 租户项目
status: draft
aliases: [项目生产数据, 是否生产数据]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:exportProjectInfo
contract_version: "0.1"
---

判定 [[tenant_project]] 中属于生产数据的项目（`is_prd='Y'`）。导出时 Y 转"是"、N 转"否"；洞察平台导出另有 1/0 兼容逻辑。

## 需求背景
语义分析未附带需求文档锚点；项目数据需要区分生产与测试，避免测试项目进入生产统计。

## 版本演进
语义分析未记录该口径的版本演进；1/0 兼容逻辑提示历史写值口径不一致。

```ground:caliber
name: 项目生产数据
predicate: "tenant_project.is_prd = 'Y'"
scope: tenant_project
evidence: "code:导出判断 Y 为是，N 为否"
```

---END FILE---

---FILE: calibers/valid_cust_project_rel.md ---
---
type: caliber
title: 口径：有效项目企业关联
page_key: valid_cust_project_rel
domain: 租户项目
status: draft
aliases: [有效项目企业关联]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:queryRelatedCompanies
contract_version: "0.1"
---

判定 [[cust_project_rel]] 中有效的项目-企业关联记录，是所有按企业维度查询/导出的前置过滤。

## 需求背景
语义分析未附带需求文档锚点；关联关系采用逻辑删除，查询关联公司时必须带 `enable='Y'`。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 有效项目企业关联
predicate: "cust_project_rel.enable = 'Y'"
scope: cust_project_rel
evidence: "code:queryRelatedCompanies 按 enable='Y' 查询"
```

---END FILE---

---FILE: calibers/role_core_company.md ---
---
type: caliber
title: 口径：核心企业角色
page_key: role_core_company
domain: 租户项目
status: draft
aliases: [核心企业角色, CORE]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:CustCompanyTypeEnum
contract_version: "0.1"
---

判定 [[cust_project_rel]] 中企业在项目下承担"核心企业"角色，对应 [[CustCompanyTypeEnum]] 的 CORE；导出关联企业时与 [[role_finance_company]] 一起作为过滤条件。

## 需求背景
语义分析未附带需求文档锚点；导出关联企业需按角色收敛（CORE/FINANCE）。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 核心企业角色
predicate: "cust_project_rel.company_type = 'CORE'"
scope: cust_project_rel
evidence: "code:CustCompanyTypeEnum.CORE，导出关联企业时过滤 CORE/FINANCE"
```

---END FILE---

---FILE: calibers/role_finance_company.md ---
---
type: caliber
title: 口径：金融机构角色
page_key: role_finance_company
domain: 租户项目
status: draft
aliases: [金融机构角色, FINANCE]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:CustCompanyTypeEnum
contract_version: "0.1"
---

判定 [[cust_project_rel]] 中企业在项目下承担"金融机构"角色，对应 [[CustCompanyTypeEnum]] 的 FINANCE；与 [[role_core_company]] 同属导出关联企业的过滤集合。

## 需求背景
语义分析未附带需求文档锚点；导出关联企业需按角色收敛（CORE/FINANCE）。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 金融机构角色
predicate: "cust_project_rel.company_type = 'FINANCE'"
scope: cust_project_rel
evidence: "code:CustCompanyTypeEnum.FINANCE，导出关联企业时过滤 CORE/FINANCE"
```

---END FILE---

---FILE: calibers/tenant_interworking_product_opened.md ---
---
type: caliber
title: 口径：租户互通产品已开通
page_key: tenant_interworking_product_opened
domain: 互通产品
status: draft
aliases: [租户互通产品已开通]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProductOpenStatusEnum
contract_version: "0.1"
---

判定 [[tenant_interworking_product]] 中已开通的记录，写值复用 [[ProductOpenStatusEnum]] 的 Y，因此口径形态与 [[tenant_product_opened]] 一致，但作用对象是互通产品线。

## 需求背景
语义分析未附带需求文档锚点；互通产品线需要独立的"已开通"判定以驱动互通业务。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 租户互通产品已开通
predicate: "tenant_interworking_product.open_status = 'Y'"
scope: tenant_interworking_product
evidence: "code:ProductOpenStatusEnum 写值绑定"
```

---END FILE---

---FILE: calibers/cust_interworking_product_opened.md ---
---
type: caliber
title: 口径：客户互通产品已开通
page_key: cust_interworking_product_opened
domain: 互通产品
status: draft
aliases: [客户互通产品已开通]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:cust_interworking_product
  - code:CustProductActiveConstant
contract_version: "0.1"
---

判定 [[cust_interworking_product]] 中已开通的记录，取值为字符串 `OPENED`（[[CustProductActiveConstant]]），与租户侧的 `Y` 不通用，注意与 [[tenant_interworking_product_opened]] 区分。

## 需求背景
语义分析未附带需求文档锚点；客户侧开通完成以 OPENED 标记。

## 版本演进
语义分析未记录该口径的版本演进；DB 分布仅有 OPENED。

```ground:caliber
name: 客户互通产品已开通
predicate: "cust_interworking_product.open_status = 'OPENED'"
scope: cust_interworking_product
evidence: "db:CustProductActiveConstant.OPENED；DB 分布 OPENED"
```

---END FILE---

---FILE: calibers/platform_product_interworking.md ---
---
type: caliber
title: 口径：平台互通产品类型
page_key: platform_product_interworking
domain: 租户产品
status: draft
aliases: [平台互通产品类型]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:PlatformProductTypeEnum
contract_version: "0.1"
---

判定 [[platform_product]] 中属于互通产品线的产品，对应 [[PlatformProductTypeEnum]] 的 INTERWORKING，用于互通产品查询；与 [[platform_product_general]] 互斥。

## 需求背景
语义分析未附带需求文档锚点；产品查询需按类型分流，避免互通产品混入通用产品查询。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 平台互通产品类型
predicate: "platform_product.product_type = 'INTERWORKING'"
scope: platform_product
evidence: "code:PlatformProductTypeEnum.INTERWORKING 用于互通产品查询"
```

---END FILE---

---FILE: calibers/platform_product_general.md ---
---
type: caliber
title: 口径：平台通用产品类型
page_key: platform_product_general
domain: 租户产品
status: draft
aliases: [平台通用产品类型]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:PlatformProductTypeEnum
contract_version: "0.1"
---

判定 [[platform_product]] 中属于通用产品线的产品，对应 [[PlatformProductTypeEnum]] 的 GENERAL，用于通用产品查询；与 [[platform_product_interworking]] 互斥。

## 需求背景
语义分析未附带需求文档锚点；产品查询按类型分流是 [[tenant_product_term]] 与 [[interworking_product_term]] 边界的技术实现。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 平台通用产品类型
predicate: "platform_product.product_type = 'GENERAL'"
scope: platform_product
evidence: "code:PlatformProductTypeEnum.GENERAL 用于通用产品查询"
```

---END FILE---

---FILE: calibers/project_tag_production.md ---
---
type: caliber
title: 口径：项目标签-生产项目
page_key: project_tag_production
domain: 租户项目
status: draft
aliases: [项目标签生产项目, 生产项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:convertProjectTagFromChinese
contract_version: "0.1"
---

判定 [[tenant_project]] 中标签为"生产项目"的记录，取值由导入校验的可选值集合限定（另见 [[project_tag_test]]、[[project_tag_paused]]）。

## 需求背景
语义分析未附带需求文档锚点；项目标签用于区分生产/测试/暂停项目，导入时需校验取值。

## 版本演进
语义分析未记录该口径的版本演进；标签落库形态（枚举码或中文）与字段语义描述不一致，已在 [[tenant_project]] 的 REVIEW 中记录。

```ground:caliber
name: 项目标签生产项目
predicate: "tenant_project.project_tag = '生产项目'"
scope: tenant_project
evidence: "code:convertProjectTagFromChinese 校验可选值"
```

---END FILE---

---FILE: calibers/project_tag_test.md ---
---
type: caliber
title: 口径：项目标签-测试项目
page_key: project_tag_test
domain: 租户项目
status: draft
aliases: [项目标签测试项目, 测试项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:convertProjectTagFromChinese
contract_version: "0.1"
---

判定 [[tenant_project]] 中标签为"测试项目"的记录，取值由导入校验的可选值集合限定（另见 [[project_tag_production]]、[[project_tag_paused]]）。

## 需求背景
语义分析未附带需求文档锚点；测试项目需与生产数据（[[project_production_data]]）区分。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 项目标签测试项目
predicate: "tenant_project.project_tag = '测试项目'"
scope: tenant_project
evidence: "code:convertProjectTagFromChinese 校验可选值"
```

---END FILE---

---FILE: calibers/project_tag_paused.md ---
---
type: caliber
title: 口径：项目标签-暂停项目
page_key: project_tag_paused
domain: 租户项目
status: draft
aliases: [项目标签暂停项目, 暂停项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:convertProjectTagFromChinese
contract_version: "0.1"
---

判定 [[tenant_project]] 中标签为"暂停项目"的记录，取值由导入校验的可选值集合限定（另见 [[project_tag_production]]、[[project_tag_test]]）。

## 需求背景
语义分析未附带需求文档锚点；暂停项目用于标记业务上暂不推进的项目。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 项目标签暂停项目
predicate: "tenant_project.project_tag = '暂停项目'"
scope: tenant_project
evidence: "code:convertProjectTagFromChinese 校验可选值"
```

---END FILE---

---FILE: calibers/approval_running.md ---
---
type: caliber
title: 口径：上线审批中
page_key: approval_running
domain: 租户项目
status: draft
aliases: [上线审批中]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectBusinessConfigApplication
contract_version: "0.1"
---

判定 [[tenant_project_approval]] 中处于审批中的记录，取值为 RUNNING（见 [[project_approval_wf_status]]）。业务配置处理只处理该口径的数据。

## 需求背景
语义分析未附带需求文档锚点；只有审批中的项目才需要同步处理业务配置。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 上线审批中
predicate: "tenant_project_approval.wf_status = 'RUNNING'"
scope: tenant_project_approval
evidence: "code:ProjectBusinessConfigApplication 只处理 RUNNING"
```

---END FILE---

---FILE: rules/enable_validity_filter.md ---
---
type: rule
title: 规则：逻辑有效标记过滤（enable='Y'）
page_key: enable_validity_filter
domain: 租户项目
status: draft
aliases: [逻辑有效标记过滤, enable 过滤规则]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - code:exportProjectInfo
  - code:queryRelatedCompanies
contract_version: "0.1"
---

规定凡涉及 [[tenant_product]]、[[tenant_project]]、[[cust_project_rel]] 的查询与导出，必须显式带 `enable='Y'`；删除一律走逻辑删除。该规则由三条独立证据归纳而成（见下方锚点与各表口径 [[valid_tenant_product]]、[[valid_project]]、[[valid_cust_project_rel]]）。

## 需求背景
语义分析未附带需求文档锚点，本节依据代码证据归纳：多张表统一使用 `enable` 作为逻辑有效标记，避免物理删除破坏关联关系（项目-产品-企业）。

## 版本演进
语义分析未记录该规则的版本演进；[[tenant_product]] 的 `enable` 在 DB 实测全为 Y。

```ground:rule
name: 逻辑有效标记过滤规则
statement: 查询与导出涉及 tenant_product / tenant_project / cust_project_rel 时必须附加 enable = 'Y'；删除采用逻辑删除，不物理删除。
predicate: "enable = 'Y'"
scope: tenant_product, tenant_project, cust_project_rel
evidence: "code:exportProjectInfo/updateProjectData 按 enable='Y'；code:queryRelatedCompanies 按 enable='Y'；db:tenant_product.enable 全为 Y"
```

---REVIEW: rule | 逻辑有效标记过滤---
语义分析在 term_bridges 处被截断，规则（rules）段落未随分析结果提供；本页是依据 caliber 与字段语义证据归纳出的唯一一条规则，其余规则待补充分析后回填。
---END REVIEW---

---END FILE---