---FILE: tables/tenant_product.md ---
---
type: table
title: 租户产品表（tenant_product）
page_key: tables/tenant_product
domain: 租户产品
status: draft
aliases: [tenant_product, 租户产品表, 租户产品]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
  - code:ProductOpenStatusEnum
  - code:ProductCodeEnum
  - code:TenantProductApplication
contract_version: "0.1"
---

租户产品（tenant_product）是「租户 × 平台产品」的订购登记：一行表示某租户开通某平台产品后形成的租户产品实例，承载该实例的开通状态、产品类型、迁移标记与融资口径（金额上限、期限上限）。它是下游能力的归属锚点：[[tables/tenant_project]] 通过 ref_tenant_project_product_code 指向本表的租户产品 code；「平台产品—租户产品」两层结构见 [[concepts/platform_product_vs_tenant_product]]。开通状态的推进过程见 [[processes/tenant_product_open_status]]。

## 需求背景
本次语义分析未提供需求文档（reqdoc）主张，故本节不含 (document_claim，未证实) 条目。从可得的 DB 与代码证据看，本表要解决的是把平台级产品定义（platform_product_id）在租户维度实例化，并对每个实例单独决定是否限额、期限上限、是否迁移，以及开通状态的推进与幂等（见 [[rules/activation_idempotency]]）。

## 版本演进
- open_status：DB 实测 N/P/Y 三值，而代码 ProductOpenStatusEnum 只使用 Y/P，N 仅出现在数据侧，见 [[concepts/product_open_status]]。
- platform_product_code：代码 ProductCodeEnum 使用 ACFLOW/BEECREDIT/ORDER/RVSFACTOR_PC 等，DB 另见 DRAFT/DRAFTQA/STORAGE/VOUCHER 等代码枚举未覆盖的值。
- enable、multiple 两列 DB 实测分别为「均为 Y」「均为 0」，属历史遗留的恒定量口径。
- 未提供版本号或需求变更记录；无 (document_claim，未证实) 主张。

```ground:table
table: tenant_product
fields:
  - name: tenant_id
    meaning: 租户 id；与 platform_product_id 组成唯一键 tenant_product_id
    evidence: db
  - name: platform_product_id
    meaning: 平台产品 id；普通索引，与 tenant_id 唯一
    evidence: db
  - name: open_status
    meaning: 租户产品开通状态；DB 实测值为 N/P/Y，N 未开通，P 开通中/等待多级回调，Y 已开通；代码 ProductOpenStatusEnum 使用 Y/P
    evidence: db
  - name: platform_product_code
    meaning: 平台产品编号；DB 实测 ACFLOW/BEECREDIT/DRAFT/DRAFTQA/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER；代码 ProductCodeEnum 使用 ACFLOW/BEECREDIT/ORDER/RVSFACTOR_PC 等
    evidence: db
  - name: product_cate
    meaning: 产品类型；DB 实测 CREDIT/STRONG/WEAKLY
    evidence: db
  - name: is_migratory
    meaning: 是否迁移标识；DB 实测 Y/N，注释 N 未迁移、Y 已迁移
    evidence: db
  - name: max_financing_amount_flag
    meaning: 是否限额融资资金上线；DB 实测 Y/N/0/1 混合值，N 为不限额，Y 为限额
    evidence: db
  - name: max_financing_amount
    meaning: 融资金额上限；DB 实测 0/88888888/不限 等
    evidence: db
  - name: max_financing_period
    meaning: 融资期限上限；DB 实测 12/36/6/12个月/36个月/6个月/6-12个月/0
    evidence: db
  - name: multiple
    meaning: 是否多个；DB 实测均为 0
    evidence: db
  - name: name
    meaning: 租户产品名称；DB 实测供票、保理易融、融易单、应收易融、票据易融、国内信用证等
    evidence: db
  - name: enable
    meaning: 启用标记；DB 实测均为 Y
    evidence: db
  - name: ref_tenant_product_project_code
    meaning: 租户产品-平台产品关联编码；DB 有多个业务 code 分布
    evidence: db
  - name: ref_tenant_product_tenant_setting_config
    meaning: 租户-产品关联配置；普通索引
    evidence: db
```

口径与状态机分别见 [[calibers/financing_limit_flag]]、[[calibers/financing_period_cap]]、[[calibers/financing_amount_cap]]、[[calibers/product_enable_flag]]；唯一键约束见 [[rules/tenant_product_unique_key]]。

---END FILE---

---REVIEW: table | 租户产品表（tenant_product）---
1) scope.databases 为空：语义分析未给出物理库名，仅能确认存在该表；落库前需补物理库名。
2) open_status 的数据值域（N/P/Y）宽于代码枚举（Y/P），N 的含义「未开通/默认」来自注释与推断，需业务确认。
3) platform_product_code 的 DRAFT/DRAFTQA/STORAGE/VOUCHER 未出现在 ProductCodeEnum 证据中，是否为测试/未上线产品需确认。
---END REVIEW---

---FILE: tables/tenant_product_menu.md ---
---
type: table
title: 租户产品菜单表（tenant_product_menu）
page_key: tables/tenant_product_menu
domain: 租户产品
status: draft
aliases: [tenant_product_menu, 租户产品菜单表]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product_menu
contract_version: "0.1"
---

租户产品菜单表按「产品 code × 企业角色」登记可用的菜单项，是租户产品开通后前台可见性的配置载体。与 [[tables/tenant_product_menu_res]] 的区别在于本表按 menu_id 关联产品菜单，而后者面向数据租户维度的菜单资源。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，本表解决的是「同一产品在不同企业角色下应看到哪些菜单」的配置问题，企业角色的取值口径见 [[calibers/company_type]]。

## 版本演进
- enable 列 DB 实测均为 Y，属恒定量，未观察到关闭态样本。
- product_code 的 DB 实测值 ACCOUNT_PRODUCT/BEECREDIT/RVSFACTOR_PC 与 [[tables/tenant_product]] 的 platform_product_code 值域不完全一致，ACCOUNT_PRODUCT 未出现在该表实测值中。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:table
table: tenant_product_menu
fields:
  - name: product_code
    meaning: 产品 code；DB 实测 ACCOUNT_PRODUCT/BEECREDIT/RVSFACTOR_PC
    evidence: db
  - name: company_type
    meaning: 企业角色；DB 实测 CORE/CORE_MANAGER/CORPORATION_COMPANY/DEALER/FINANCE/PLATFORM_OPERATOR/PLATFORM_OPERATOR_COMPANY/PROJECT_COMPANY/SUPPLIER
    evidence: db
  - name: menu_id
    meaning: 菜单 id；关联产品菜单
    evidence: db
  - name: enable
    meaning: 启用标记；DB 实测均为 Y
    evidence: db
```

启用的口径统一见 [[calibers/product_enable_flag]]。

---END FILE---

---FILE: tables/tenant_product_menu_res.md ---
---
type: table
title: 租户产品菜单资源表（tenant_product_menu_res）
page_key: tables/tenant_product_menu_res
domain: 租户产品
status: draft
aliases: [tenant_product_menu_res, 租户产品菜单资源表]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product_menu_res
contract_version: "0.1"
---

租户产品菜单资源表按「产品 code × 企业角色 × 数据租户」登记菜单资源，是本主题中唯一显式带 db_tenant_code 的菜单类配置表，因而承担了菜单配置的租户隔离维度。与 [[tables/tenant_product_menu]] 配合使用。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。证据显示本表要解决的是「同一个产品与角色组合，在不同数据租户下菜单资源可以不同」的问题；数据租户标识的含义见 [[concepts/logical_vs_db_tenant_code]]。

## 版本演进
- db_tenant_code 的 DB 实测值为 LN1/beehive-scf.qhhrly.cn/ning，取值形态包含简码与域名，属于历史遗留的混合命名。
- enable 列 DB 实测均为 Y。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:table
table: tenant_product_menu_res
fields:
  - name: product_code
    meaning: 产品 code；DB 实测 ACCOUNT_PRODUCT/RVSFACTOR_PC
    evidence: db
  - name: company_type
    meaning: 企业角色；DB 实测 CORE/CORPORATION_COMPANY/PLATFORM_OPERATOR_COMPANY/SUPPLIER
    evidence: db
  - name: db_tenant_code
    meaning: 数据租户标识；DB 实测 LN1/beehive-scf.qhhrly.cn/ning
    evidence: db
  - name: enable
    meaning: 启用标记；DB 实测均为 Y
    evidence: db
```

企业角色口径见 [[calibers/company_type]]。

---END FILE---

---FILE: tables/tenant_interworking_product.md ---
---
type: table
title: 租户互通产品表（tenant_interworking_product）
page_key: tables/tenant_interworking_product
domain: 互通产品
status: draft
aliases: [tenant_interworking_product, 租户互通产品表, 互通产品]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_interworking_product
  - code:TenantInterworkingProductApplication
contract_version: "0.1"
---

租户互通产品表登记租户级互通产品的配置，除融资口径外还承载业务描述型字段（增信措施、客户群体）。与 [[tables/cust_interworking_product]] 的客户级开通状态形成「配置表—状态表」的配对关系，状态推进见 [[processes/interworking_product_open_status]]。本表同时出现逻辑租户标识与数据租户标识两列，见 [[concepts/logical_vs_db_tenant_code]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，本表要解决的是按租户描述互通产品的业务属性（增信措施、客户群体、融资上下限）并控制其启用。

## 版本演进
- credit_measures、customer_group 的 DB 实测值包含 HTCP15/ddd/sdsd 等疑似测试值，与「共同债务人增信、差额补足」「供应商、金融机构、项目公司」等业务用语混存，属自由文本字段的典型历史形态。
- max_financing_period 实测为「1-3年」这类区间文本，与 [[tables/tenant_product]] 同名字段的数值形态不同，见 [[calibers/financing_period_cap]]。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:table
table: tenant_interworking_product
fields:
  - name: app_tenant_code
    meaning: 逻辑租户标识；DB 实测 GREENTOWNAT/JHYL/base/hylg
    evidence: db
  - name: db_tenant_code
    meaning: 数据租户标识；DB 实测 ISOLATE_TAG_*/LN1/beehive-scf.qhhrly.cn/mengniu/yunyingzhongtai
    evidence: db
  - name: credit_measures
    meaning: 增信措施；DB 实测 HTCP15/ddd/共同债务人增信、差额补足
    evidence: db
  - name: customer_group
    meaning: 客户群体；DB 实测 HTCP15/sdsd/供应商/拥有优质资产并存在融资需求的企业或机构/金融机构/项目公司
    evidence: db
  - name: max_financing_amount_flag
    meaning: 是否限额融资资金上线；DB 实测 N/Y
    evidence: db
  - name: max_financing_period
    meaning: 融资期限上限；DB 实测 1-3年 等
    evidence: db
  - name: enable
    meaning: 启用标记；DB 实测均为 Y
    evidence: db
```

---END FILE---

---FILE: tables/cust_interworking_product.md ---
---
type: table
title: 客户互通产品表（cust_interworking_product）
page_key: tables/cust_interworking_product
domain: 互通产品
status: draft
aliases: [cust_interworking_product, 客户互通产品表]
oid: 1
scope:
  databases: []
sources:
  - db:cust_interworking_product
  - code:CustProductActiveConstant
contract_version: "0.1"
---

客户互通产品表记录客户维度的互通产品开通状态，是互通产品链路上「配置在前、状态在后」的状态一侧：配置见 [[tables/tenant_interworking_product]]，状态推进见 [[processes/interworking_product_open_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，本表需要回答「某客户是否已开通某互通产品」，并支撑开通/取消两类操作。

## 版本演进
- DB 对账值 OPENED 与代码常量 CustProductActiveConstant.OPENED 同名，但语义分析指出该常量未在代码枚举基线上覆盖本表取值，属代码与数据未完全对齐的遗留点，见 [[concepts/product_open_status]]。
- 本表未提供字段级明细（仅一条字段证据），字段清单待补。

```ground:table
table: cust_interworking_product
fields:
  - name: open_status
    meaning: 客户互通产品开通状态；DB 对账值 OPENED，代码侧常量 CustProductActiveConstant.OPENED 未在代码枚举基线上覆盖该表值
    evidence: db
```

---END FILE---

---REVIEW: table | 客户互通产品表（cust_interworking_product）---
open_status 的 DB 值（OPENED）与代码常量 CustProductActiveConstant.OPENED 的对应关系只在语义分析中以「未在代码枚举基线上覆盖」描述，OPENING 是否实际落库、以及是否存在其它取值，均无直接证据，需补充字段级对账。
---END REVIEW---

---FILE: tables/tenant_project.md ---
---
type: table
title: 租户项目表（tenant_project）
page_key: tables/tenant_project
domain: 租户项目
status: draft
aliases: [tenant_project, 租户项目表]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_project
  - code:TenantProjectApplication
  - code:ProjectStatusEnum
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

租户项目表是租户产品的落地载体：一个租户产品下可以建立若干项目，项目上有产品归属、渠道来源、运营/风控对接人、项目标签与配置 JSON，并通过 [[tables/tenant_project_approval]] 走上线审批。项目从「未生效」到生效、失效的闭环见 [[processes/tenant_project_status]]；有效性的判定口径见 [[calibers/project_effective]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，本表承担三件事：①记录项目归属（租户、租户产品、平台产品）；②承载项目运营信息（对接人、组别、业务部门、标签）；③通过 config_json 在不同产品线生效时驱动开户/校验（见 [[rules/project_effective_requires_config_check]]）。

## 版本演进
- source 的 DB 对账实测 ACFLOW/ORDER/RVSFACTOR_PC/STORAGE/pplatform，代码未见完整枚举声明，值域未收敛。
- op_contact_b、risk_control_contact_b 在库中以 JSON 数组字符串存储，DTO 再转为 List<String>，属字段模型与库模型不一致的遗留设计。
- project_tag 以中文（生产项目/测试项目/暂停项目）入库转枚举，见 [[concepts/project_tag]]。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:table
table: tenant_project
fields:
  - name: project_status
    meaning: 项目状态；代码使用 ProjectStatusEnum.EFFECTIVE 与 ProjectStatusEnum.INVLIAD，分别表示已生效、已失效
    evidence: code
  - name: enable
    meaning: 逻辑删除/有效标记；代码查询与导出普遍限定 enable='Y'，删除操作调用 domainService.delete
    evidence: code
  - name: source
    meaning: 项目来源/渠道；DB 对账实测 ACFLOW/ORDER/RVSFACTOR_PC/STORAGE/pplatform，代码未见完整枚举声明
    evidence: db
  - name: platform_product_code
    meaning: 平台产品编号；项目所属平台产品
    evidence: code
  - name: ref_tenant_project_product_code
    meaning: 关联租户产品 code；用于按产品查询、生效、失效、同步
    evidence: code
  - name: ref_tenant_project_tenant_code
    meaning: 关联租户 code；创建项目时校验租户存在
    evidence: code
  - name: ref_tenant_project_platform_product
    meaning: 关联平台产品 code；导出时用于查平台产品名称
    evidence: code
  - name: config_json
    meaning: 项目配置 JSON；BEECREDIT 生效前解析校验配置状态，ACFLOW/RVSFACTOR 生效时用于开户/查询业务系统配置
    evidence: code
  - name: channel_code
    meaning: 项目码/渠道码；queryByChannelCode 可按渠道码查项目
    evidence: code
  - name: is_prd
    meaning: 是否生产数据；代码导出时 Y 转“是”、N 转“否”
    evidence: code
  - name: wechat_audit_no
    meaning: 企微审批编号/立项审批编号；可由上线审批提交时回填
    evidence: code
  - name: op_contact_a
    meaning: 运营对接人A；导入导出时按运营人员姓名/ID 转换
    evidence: code
  - name: op_contact_b
    meaning: 运营对接人B；数据库以 JSON 数组字符串存储，DTO 转为 List<String>
    evidence: code
  - name: op_contact_a_group
    meaning: 运营组别；导入时按运营对接人A的组别刷新
    evidence: code
  - name: verification_contact
    meaning: 查验对接人；导入导出时按运营人员姓名/ID 转换
    evidence: code
  - name: risk_control_contact_a
    meaning: 风控对接人A；导入导出时按运营人员姓名/ID 转换
    evidence: code
  - name: risk_control_contact_b
    meaning: 风控对接人B；数据库以 JSON 数组字符串存储，DTO 转为 List<String>
    evidence: code
  - name: solution_manager
    meaning: 方案经理；可由洞察平台补全，导入时校验运营人员存在
    evidence: code
  - name: business_group
    meaning: 关联业务部门；可由洞察平台补全
    evidence: code
  - name: project_tag
    meaning: 项目标签；中文可选生产项目、测试项目、暂停项目，入库转枚举值
    evidence: code
  - name: bussiness_project_relation
    meaning: 运营项目归属；导入长度限制不超过 50
    evidence: code
  - name: invite_customer_service_words
    meaning: 邀请信息-客服话术；导入时长度限制不超过 500
    evidence: code
  - name: project_approval_id
    meaning: 项目最新上线审批 ID；创建审批后回写项目
    evidence: code
```

相关：[[rules/tenant_project_enable_filter]]、[[rules/import_length_limits]]、[[concepts/op_contact]]、[[calibers/project_effective]]。

---END FILE---

---FILE: tables/tenant_project_approval.md ---
---
type: table
title: 项目上线审批表（tenant_project_approval）
page_key: tables/tenant_project_approval
domain: 租户项目
status: draft
aliases: [tenant_project_approval, 项目上线审批表]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

项目上线审批表承载 [[tables/tenant_project]] 的上线审批实例，是项目由「审批中」走向生效的凭据；审批通过后触发项目生效（见 [[rules/effective_on_approval_finished]]）。工作流状态的完整迁移见 [[processes/project_approval_workflow_status]]，节点级状态见 [[processes/project_approval_node_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，本表要解决的是「项目上线需要审批、审批可以反复发起、草稿可暂存」这三件事，并通过复制新审批记录回到待发起态。

## 版本演进
本次语义分析未给出本表的字段级语义（field_semantics 未覆盖），仅状态机证据可用；因此本页锚点只登记 wf_status 的取值，字段清单待补。

```ground:table
table: tenant_project_approval
fields:
  - name: wf_status
    states:
      - PENDING
      - RUNNING
      - FINISHED
      - TERMINATED
    evidence: code_enum
```

---END FILE---

---REVIEW: table | 项目上线审批表（tenant_project_approval）---
该表未进入 field_semantics，本页仅依据状态机证据登记 wf_status 取值（PENDING/RUNNING/FINISHED/TERMINATED），字段级注释、索引与约束均未知。
---END REVIEW---

---FILE: tables/tenant_project_approval_flow.md ---
---
type: table
title: 项目上线审批节点表（tenant_project_approval_flow）
page_key: tables/tenant_project_approval_flow
domain: 租户项目
status: draft
aliases: [tenant_project_approval_flow, 项目上线审批节点表]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

项目上线审批节点表记录审批实例下的每个审批节点状态，是 [[tables/tenant_project_approval]] 的下级明细。节点状态迁移见 [[processes/project_approval_node_status]]，其中「业务经理节点通过」同时是后补合作协议判断的触发点（见 [[rules/back_agreement_check]]）。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，本表要解决的是审批流中各节点的处理进度落库，并驱动后续协议判断。

## 版本演进
本表未进入 field_semantics，仅节点状态机证据可用；字段清单与节点定义方式待补。

```ground:table
table: tenant_project_approval_flow
fields:
  - name: node_status
    states:
      - PENDING
      - APPROVING
      - APPROVED
    evidence: code_enum
```

---END FILE---

---FILE: processes/tenant_product_open_status.md ---
---
type: process
title: 租户产品开通状态流转
page_key: processes/tenant_product_open_status
domain: 租户产品
status: draft
aliases: [租户产品开通状态, tenant_product.open_status]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProductApplication
  - db:tenant_product
contract_version: "0.1"
---

租户产品开通是「平台产品下发到租户」的落地动作，其状态位于 [[tables/tenant_product]] 的 open_status 列。非 ACFLOW/ORDER 类产品一次置为已开通；ACFLOW/ORDER 类产品需等待多级回调，先停留在开通中。状态的三值语义见 [[concepts/product_open_status]]，其中 N 只在数据侧出现。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，该流程要解决两个问题：①不同产品线的开通是否需要多级回调；②重复开通请求的幂等（见 [[rules/activation_idempotency]]）。

## 版本演进
- 代码枚举 ProductOpenStatusEnum 只覆盖 Y/P，DB 实测还有 N，说明「未开通」态在代码基线中未显式建模。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:state_machine
name: 租户产品开通状态
field: tenant_product.open_status
states:
  - value: "N"
    label: 未开通/默认
    source: db_dist
  - value: "P"
    label: 开通中/等待多级回调
    source: code_enum
  - value: "Y"
    label: 已开通
    source: code_enum
transitions:
  - from: "N"
    event: activeAndNotify 非 ACFLOW/ORDER 产品主动开通
    to: "Y"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
  - from: "N"
    event: activeAndNotify 产品为 ACFLOW/ORDER，先置为开通中等待多级回调
    to: "P"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
  - from: "Y"
    event: activeAndNotify 幂等命中已开通直接返回
    to: "Y"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
```

---END FILE---

---FILE: processes/tenant_project_status.md ---
---
type: process
title: 租户项目启停流转
page_key: processes/tenant_project_status
domain: 租户项目
status: draft
aliases: [租户项目状态, tenant_project.project_status, 项目生效失效]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
  - code:ProjectApprovalApplication
  - code:ProjectStatusEnum
contract_version: "0.1"
---

租户项目状态记录在 [[tables/tenant_project]] 的 project_status 列，代码中只有两个值：ProjectStatusEnum.EFFECTIVE（已生效）与 ProjectStatusEnum.INVLIAD（已失效）。项目可通过 effective/invalid 双向操作，也可由上线审批完成自动回到生效，见 [[rules/effective_on_approval_finished]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，该流程要解决的是「项目建好后由谁、在什么条件下对外生效」的问题，审批链路见 [[processes/project_approval_workflow_status]]。

## 版本演进
- project_status 的枚举拼写为 INVLIAD（非 INVALID），属代码既有拼写，改动前需评估兼容。
- 「未生效」仅作为迁移起点出现，没有对应的枚举字面量。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:state_machine
name: 租户项目状态
field: tenant_project.project_status
states:
  - value: EFFECTIVE
    label: 已生效
    source: code_enum
  - value: INVLIAD
    label: 已失效
    source: code_enum
transitions:
  - from: 未生效
    event: effective 生效项目
    to: EFFECTIVE
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/TenantProjectApplication.java:effective"
  - from: EFFECTIVE
    event: invalid 失效项目
    to: INVLIAD
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/TenantProjectApplication.java:invalid"
  - from: INVLIAD
    event: 上线审批完成通过后 effectiveProjectOnApprovalFinished 调 effective
    to: EFFECTIVE
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished"
```

有效性的口径（enable 与 project_status 的组合）见 [[calibers/project_effective]]。

---END FILE---

---FILE: processes/project_approval_workflow_status.md ---
---
type: process
title: 项目上线审批工作流状态流转
page_key: processes/project_approval_workflow_status
domain: 租户项目
status: draft
aliases: [项目上线审批工作流状态, tenant_project_approval.wf_status, wf_status]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

项目上线审批工作流状态位于 [[tables/tenant_project_approval]] 的 wf_status 列，描述审批实例从待发起、审批中到完成或终止的推进过程。审批完成会反向影响项目状态（[[processes/tenant_project_status]]）。节点级的处理进度见 [[processes/project_approval_node_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，该流程要解决三件事：①发起审批并进入审批中；②审批流结束后区分「完成」与「终止」；③已结束的审批可以复制成新的待发起记录，且草稿（isDraft=Y）可暂存不回退状态。

## 版本演进
- 已结束（FINISHED/TERMINATED）的审批通过 doCreateApproval 复制新记录回到 PENDING，说明「一个项目可多次上线审批」是既有能力。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:state_machine
name: 项目上线审批工作流状态
field: tenant_project_approval.wf_status
states:
  - value: PENDING
    label: 待发起/待审批
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
    event: startWorkflowAndUpdateStatus 启动工作流
    to: RUNNING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:startWorkflowAndUpdateStatus"
  - from: RUNNING
    event: handleFlowAndNodeStatus 判断为 FINISHED
    to: FINISHED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:handleFlowAndNodeStatus"
  - from: RUNNING
    event: handleFlowAndNodeStatus 判断为 TERMINATED
    to: TERMINATED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:handleFlowAndNodeStatus"
  - from: PENDING
    event: submit 暂存 isDraft=Y
    to: PENDING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:submit"
  - from: FINISHED/TERMINATED
    event: createApproval/doCreateApproval 复制新审批记录置 PENDING
    to: PENDING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:doCreateApproval"
```

---END FILE---

---FILE: processes/project_approval_node_status.md ---
---
type: process
title: 项目上线审批节点状态流转
page_key: processes/project_approval_node_status
domain: 租户项目
status: draft
aliases: [项目上线审批节点状态, tenant_project_approval_flow.node_status, node_status]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

项目上线审批节点状态记录在 [[tables/tenant_project_approval_flow]] 的 node_status 列，随工作流推进由待处理变为审批中，节点通过后置为已通过。该状态同时是后补合作协议判断的前置条件，见 [[rules/back_agreement_check]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，节点状态的用途是：让业务在「业务经理节点通过」这一刻得知可以开始判断后补合作协议。

## 版本演进
- 状态字面量只有 PENDING/APPROVING/APPROVED 三个，未见「驳回」态，驳回后的落库方式待确认。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:state_machine
name: 项目上线审批节点状态
field: tenant_project_approval_flow.node_status
states:
  - value: PENDING
    label: 待处理
    source: code_enum
  - value: APPROVING
    label: 审批中
    source: code_enum
  - value: APPROVED
    label: 已通过
    source: code_enum
transitions:
  - from: PENDING
    event: handleFlowAndNodeStatus 写入节点状态
    to: APPROVING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:handleFlowAndNodeStatus"
  - from: APPROVING
    event: 业务经理节点通过且 is_back_agreement=Y 触发后补合作协议判断
    to: APPROVED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:isStartBackAgreement"
```

---END FILE---

---FILE: processes/interworking_product_open_status.md ---
---
type: process
title: 客户互通产品开通状态流转
page_key: processes/interworking_product_open_status
domain: 互通产品
status: draft
aliases: [互通产品开通状态, cust_interworking_product.open_status]
oid: 1
scope:
  databases: []
sources:
  - code:TenantInterworkingProductApplication
  - db:cust_interworking_product
contract_version: "0.1"
---

客户互通产品开通状态位于 [[tables/cust_interworking_product]] 的 open_status 列，配置侧在 [[tables/tenant_interworking_product]]。开通由 active 完成；取消由 cancel 完成，且一旦关联项目即不允许取消（见 [[rules/interworking_product_cancel_guard]]）。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，该流程要解决的是互通产品在客户维度的开关管理，并对取消动作加上「已关联项目」这一前置限制。

## 版本演进
- 状态值 DB 侧为 OPENED，代码侧另有 OPENING，二者命名体系与租户产品的 N/P/Y 不同，见 [[concepts/product_open_status]]。
- 语义分析中 cancel 迁移的代码路径证据被截断，本页只登记有完整证据的 active 迁移，cancel 相关约束单列于规则页并标注待复核。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:state_machine
name: 客户互通产品开通状态
field: cust_interworking_product.open_status
states:
  - value: OPENED
    label: 已开通
    source: db_dist
  - value: OPENING
    label: 开通中
    source: code_enum
transitions:
  - from: 未开通
    event: TenantInterworkingProductApplication.active 开通互通产品
    to: OPENED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantInterworkingProductApplication.java:active"
```

---END FILE---

---REVIEW: process | 客户互通产品开通状态流转---
原语义分析中 cust_interworking_product 状态机的第二条迁移（TenantInterworkingProductApplication.cancel：OPENED → 未开通，关联项目后不允许取消）的 code_path 证据被截断于 "…/product/application/p"，本页未将其写入锚点块；该迁移的业务语义已单独登记为 rules/interworking_product_cancel_guard，需补齐完整路径后复核。
---END REVIEW---

---FILE: calibers/financing_limit_flag.md ---
---
type: caliber
title: 限额融资资金口径（max_financing_amount_flag）
page_key: calibers/financing_limit_flag
domain: 租户产品
status: draft
aliases: [是否限额融资资金上线, max_financing_amount_flag, 限额口径]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
  - db:tenant_interworking_product
contract_version: "0.1"
---

本口径回答「某租户产品/互通产品是否对融资金额设上限」。[[tables/tenant_product]] 中该列 DB 实测为 Y/N/0/1 四种值，属布尔语义被多种写法混用；[[tables/tenant_interworking_product]] 中实测只有 N/Y 两值，形态更规范。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该口径被融资额度相关展示与校验复用，实际额度还要结合 [[calibers/financing_amount_cap]] 一起判断。

## 版本演进
- 0/1 与 N/Y 混存说明该列经历过布尔/字符两种表达方式的演进，统计时需先归一。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 是否限额融资资金上线口径
field: tenant_product.max_financing_amount_flag
values: ["Y", "N", "0", "1"]
definition: DB 实测 Y/N/0/1 混合值，N 为不限额，Y 为限额
evidence: db
```

---END FILE---

---FILE: calibers/financing_amount_cap.md ---
---
type: caliber
title: 融资金额上限口径（max_financing_amount）
page_key: calibers/financing_amount_cap
domain: 租户产品
status: draft
aliases: [融资金额上限, max_financing_amount]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
contract_version: "0.1"
---

本口径描述 [[tables/tenant_product]] 中融资金额上限的取值形态，用于判断「限额」时上限以什么形式表达。是否限额本身见 [[calibers/financing_limit_flag]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该列同时存在数值与中文文本，意味着读取方需要按上下文决定按数值比较还是按文本展示。

## 版本演进
- 实测出现 0、88888888、不限 三类值：0 与「不限」在语义上冲突，88888888 疑似约定的「无穷大」，属历史兼容写法。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 融资金额上限口径
field: tenant_product.max_financing_amount
values: ["0", "88888888", "不限"]
definition: DB 实测 0/88888888/不限 等
evidence: db
```

---END FILE---

---FILE: calibers/financing_period_cap.md ---
---
type: caliber
title: 融资期限上限口径（max_financing_period）
page_key: calibers/financing_period_cap
domain: 租户产品
status: draft
aliases: [融资期限上限, max_financing_period]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
  - db:tenant_interworking_product
contract_version: "0.1"
---

本口径描述融资期限上限的取值形态。[[tables/tenant_product]] 以月为单位混存纯数字与带「个月」后缀的文本，[[tables/tenant_interworking_product]] 则以「1-3年」区间形式表达，两张表的单位与粒度并不统一。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该口径影响期限展示与校验，读取前需先归一单位。

## 版本演进
- tenant_product 实测值 12/36/6/12个月/36个月/6个月/6-12个月/0 显示单位后缀与区间写法是后加的。
- tenant_interworking_product 的 1-3年 为区间语义，与数值上限不可直接比较。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 融资期限上限口径
fields:
  - table: tenant_product
    field: max_financing_period
    values: ["12", "36", "6", "12个月", "36个月", "6个月", "6-12个月", "0"]
    definition: DB 实测 12/36/6/12个月/36个月/6个月/6-12个月/0
    evidence: db
  - table: tenant_interworking_product
    field: max_financing_period
    values: ["1-3年"]
    definition: DB 实测 1-3年 等
    evidence: db
```

---END FILE---

---FILE: calibers/product_enable_flag.md ---
---
type: caliber
title: 产品启用标记口径（enable）
page_key: calibers/product_enable_flag
domain: 租户产品
status: draft
aliases: [启用标记, enable]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
  - db:tenant_product_menu
  - db:tenant_product_menu_res
  - db:tenant_interworking_product
contract_version: "0.1"
---

产品族四张表都带 enable 列，DB 实测均为 Y，出现「启用态恒定、关闭态靠删除实现」的口径特征。它与「开通状态」不是同一概念，见 [[concepts/product_open_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，查询侧默认只关心启用记录，因此 enable 更多是过滤条件而非业务状态。

## 版本演进
- 四表实测均为 Y，未观察到 N 样本，无法判断 N 是否仍在被写入。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 产品启用标记口径
fields:
  - table: tenant_product
    field: enable
    values: ["Y"]
    definition: 启用标记；DB 实测均为 Y
    evidence: db
  - table: tenant_product_menu
    field: enable
    values: ["Y"]
    definition: 启用标记；DB 实测均为 Y
    evidence: db
  - table: tenant_product_menu_res
    field: enable
    values: ["Y"]
    definition: 启用标记；DB 实测均为 Y
    evidence: db
  - table: tenant_interworking_product
    field: enable
    values: ["Y"]
    definition: 启用标记；DB 实测均为 Y
    evidence: db
```

---END FILE---

---FILE: calibers/project_effective.md ---
---
type: caliber
title: 租户项目有效口径
page_key: calibers/project_effective
domain: 租户项目
status: draft
aliases: [项目有效口径, project_status, enable='Y']
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
  - code:ProjectStatusEnum
contract_version: "0.1"
---

「项目是否有效」在本主题里由两个维度共同决定：[[tables/tenant_project]] 的 enable 表示逻辑删除（查询与导出普遍限定 enable='Y'），project_status 表示业务上的生效/失效。二者独立，判断一个项目能否被业务使用时需同时成立。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该口径支撑项目列表、导出与按产品同步等查询场景，见 [[rules/tenant_project_enable_filter]]。

## 版本演进
- 删除走 domainService.delete 而非物理删除，enable 承担历史数据过滤职责。
- project_status 的失效值拼写为 INVLIAD，见 [[processes/tenant_project_status]]。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 租户项目有效口径
fields:
  - table: tenant_project
    field: enable
    values: ["Y", "N"]
    definition: 逻辑删除/有效标记；代码查询与导出普遍限定 enable='Y'，删除操作调用 domainService.delete
    evidence: code
  - table: tenant_project
    field: project_status
    values: [EFFECTIVE, INVLIAD]
    definition: 项目状态；代码使用 ProjectStatusEnum.EFFECTIVE 与 ProjectStatusEnum.INVLIAD，分别表示已生效、已失效
    evidence: code
```

---END FILE---

---FILE: calibers/company_type.md ---
---
type: caliber
title: 企业角色口径（company_type）
page_key: calibers/company_type
domain: 租户产品
status: draft
aliases: [企业角色, company_type]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product_menu
  - db:tenant_product_menu_res
contract_version: "0.1"
---

企业角色口径描述菜单配置中「角色」维度的可选值。[[tables/tenant_product_menu]] 的实测值域为 9 类，[[tables/tenant_product_menu_res]] 只有其中 4 类，说明后者面向的角色更窄。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该口径决定同产品在不同角色下可见的菜单集合，与 [[tables/tenant_product_menu]]、[[tables/tenant_product_menu_res]] 的配置共同生效。

## 版本演进
- 两张表的角色值域不一致（CORE_MANAGER/DEALER/FINANCE/PLATFORM_OPERATOR/PROJECT_COMPANY 只出现在 menu 表），是否为业务差异需确认。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 企业角色口径
fields:
  - table: tenant_product_menu
    field: company_type
    values: [CORE, CORE_MANAGER, CORPORATION_COMPANY, DEALER, FINANCE, PLATFORM_OPERATOR, PLATFORM_OPERATOR_COMPANY, PROJECT_COMPANY, SUPPLIER]
    definition: 企业角色；DB 实测 CORE/CORE_MANAGER/CORPORATION_COMPANY/DEALER/FINANCE/PLATFORM_OPERATOR/PLATFORM_OPERATOR_COMPANY/PROJECT_COMPANY/SUPPLIER
    evidence: db
  - table: tenant_product_menu_res
    field: company_type
    values: [CORE, CORPORATION_COMPANY, PLATFORM_OPERATOR_COMPANY, SUPPLIER]
    definition: 企业角色；DB 实测 CORE/CORPORATION_COMPANY/PLATFORM_OPERATOR_COMPANY/SUPPLIER
    evidence: db
```

---END FILE---

---FILE: concepts/product_open_status.md ---
---
type: concept
title: 开通状态（产品开通）
page_key: concepts/product_open_status
domain: 租户产品
status: draft
aliases: [开通状态, open_status, 产品开通状态]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
  - db:cust_interworking_product
  - code:ProductOpenStatusEnum
  - code:CustProductActiveConstant
maps_to:
  - tenant_product.open_status
  - cust_interworking_product.open_status
field_targets:
  - table: tenant_product
    field: open_status
    values: ["N", "P", "Y"]
    process: processes/tenant_product_open_status
  - table: cust_interworking_product
    field: open_status
    values: [OPENED, OPENING]
    process: processes/interworking_product_open_status
adjudication: >
  「开通状态」指该租户/客户是否已经获得某产品能力，是推进态（含中间态），
  与「启用标记 enable」不同：enable 是配置是否生效的开关（见 calibers/product_enable_flag），
  也不等同于「项目是否生效」（见 calibers/project_effective）。
  同名字段在不同表使用不同字面量体系：租户产品用 N/P/Y，客户互通产品用 OPENED/OPENING，
  不可跨表直接比较。
also_confused_with:
  - calibers/product_enable_flag
  - calibers/project_effective
contract_version: "0.1"
---

「开通状态」是本主题最容易被串用的术语：它在产品侧（[[tables/tenant_product]]）、客户侧（[[tables/cust_interworking_product]]）各自有同名列，但取值体系不同。业务上它回答「能不能用」，而不是「配置是否打开」。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该术语桥用于避免把开通状态与启用标记、项目生效混为一谈，具体口径见 [[calibers/product_enable_flag]]。

## 版本演进
- 租户产品侧代码枚举 ProductOpenStatusEnum 仅覆盖 Y/P，DB 另有 N；客户互通产品侧 DB 值 OPENED 与代码常量 CustProductActiveConstant.OPENED 的对应关系未被枚举基线覆盖。
- 两个产品线的字面量体系未统一，是历史演进遗留。

本页按 concept 约定不设锚点块，字段目标见 frontmatter。

---END FILE---

---REVIEW: concept | 开通状态（产品开通）---
adjudication 中「同名字段不可跨表比较」的依据来自两侧取值字面量不同（N/P/Y 与 OPENED/OPENING），但两侧是否曾有过统一字面量的设计意图，无证据，需业务确认。
---END REVIEW---

---FILE: concepts/logical_vs_db_tenant_code.md ---
---
type: concept
title: 逻辑租户标识与数据租户标识
page_key: concepts/logical_vs_db_tenant_code
domain: 互通产品
status: draft
aliases: [app_tenant_code, db_tenant_code, 逻辑租户, 数据租户]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_interworking_product
  - db:tenant_product_menu_res
maps_to:
  - tenant_interworking_product.app_tenant_code
  - tenant_interworking_product.db_tenant_code
  - tenant_product_menu_res.db_tenant_code
field_targets:
  - table: tenant_interworking_product
    field: app_tenant_code
    values: [GREENTOWNAT, JHYL, base, hylg]
  - table: tenant_interworking_product
    field: db_tenant_code
    values: ["ISOLATE_TAG_*", LN1, "beehive-scf.qhhrly.cn", mengniu, yunyingzhongtai]
  - table: tenant_product_menu_res
    field: db_tenant_code
    values: [LN1, "beehive-scf.qhhrly.cn", ning]
adjudication: >
  app_tenant_code 是逻辑租户标识（应用/业务视角的租户），db_tenant_code 是数据租户标识（数据隔离视角）。
  二者在 tenant_interworking_product 上成对出现，取值集合并不相同，不能互相替代；
  菜单资源表只带 db_tenant_code，说明菜单配置按数据隔离维度下发。
also_confused_with:
  - concepts/platform_product_vs_tenant_product
contract_version: "0.1"
---

本术语桥用于区分「逻辑租户」与「数据租户」两个在库中形似而语义不同的列。前者对应业务上签约的主体，后者对应数据落库/隔离的归属；测试数据中的 ISOLATE_TAG_* 前缀进一步印证后者是隔离维度的技术标识。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该区分影响互通产品配置与菜单资源的下发范围，见 [[tables/tenant_interworking_product]]、[[tables/tenant_product_menu_res]]。

## 版本演进
- db_tenant_code 同时存在简码（LN1、ning）与域名（beehive-scf.qhhrly.cn）两种形态，命名规范未统一。
- 未提供版本记录；无 (document_claim，未证实) 主张。

本页按 concept 约定不设锚点块。

---END FILE---

---FILE: concepts/platform_product_vs_tenant_product.md ---
---
type: concept
title: 平台产品与租户产品
page_key: concepts/platform_product_vs_tenant_product
domain: 租户产品
status: draft
aliases: [平台产品, 租户产品, platform_product_code, 产品两层结构]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
  - db:tenant_project
  - db:tenant_product_menu
maps_to:
  - tenant_product.platform_product_id
  - tenant_product.platform_product_code
  - tenant_product.ref_tenant_product_project_code
  - tenant_project.ref_tenant_project_product_code
field_targets:
  - table: tenant_product
    field: platform_product_id
    note: 平台产品 id；与 tenant_id 组成唯一键
  - table: tenant_product
    field: ref_tenant_product_project_code
    note: 租户产品-平台产品关联编码
  - table: tenant_project
    field: ref_tenant_project_product_code
    note: 关联租户产品 code
adjudication: >
  平台产品是产品定义层（platform_product_id / platform_product_code），
  租户产品是定义在某租户上的实例（tenant_id + platform_product_id 唯一，见 rules/tenant_product_unique_key）。
  项目通过 ref_tenant_project_product_code 挂在租户产品下，而不是直接挂在平台产品下；
  因此在按产品统计时，应先落到租户产品再汇总，避免把平台产品 code 当作租户产品 code 使用。
also_confused_with:
  - concepts/product_open_status
contract_version: "0.1"
---

「平台产品—租户产品—项目」是三级结构：平台产品给出产品编号（ACFLOW/BEECREDIT 等），租户产品给出该租户下的实例及其融资口径，项目是实例下的具体业务载体（[[tables/tenant_project]]）。菜单配置（[[tables/tenant_product_menu]]）按产品 code 维度下发，其取值与 platform_product_code 不完全是同一套值。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该术语桥用于避免在查询与统计中混用两级产品的 code。

## 版本演进
- 产品 code 存在多套值域：platform_product_code（含 DRAFT/DRAFTQA/STORAGE/VOUCHER）与 tenant_product_menu.product_code（含 ACCOUNT_PRODUCT）并不一致。
- 未提供版本记录；无 (document_claim，未证实) 主张。

本页按 concept 约定不设锚点块。

---END FILE---

---FILE: concepts/project_tag.md ---
---
type: concept
title: 项目标签（project_tag）
page_key: concepts/project_tag
domain: 租户项目
status: draft
aliases: [项目标签, project_tag, 生产项目/测试项目/暂停项目]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
maps_to:
  - tenant_project.project_tag
field_targets:
  - table: tenant_project
    field: project_tag
    note: 中文可选生产项目、测试项目、暂停项目，入库转枚举值
adjudication: >
  项目标签是「项目性质」的分类标记（生产项目/测试项目/暂停项目），
  与 enable（是否逻辑删除，见 calibers/project_effective）、is_prd（是否生产数据，导入导出时 Y/N 转「是/否」）
  三者含义不同：is_prd 描述数据属性，project_tag 描述项目用途，enable 描述记录是否有效。
also_confused_with:
  - calibers/project_effective
contract_version: "0.1"
---

项目标签在导入侧以中文录入，落库时转成枚举值，导出侧再还原为可读文案。它解决的是「这个项目是生产、测试还是暂停」的分类问题，而 [[tables/tenant_project]] 的 is_prd 只回答数据是否来自生产。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。

## 版本演进
- 中文与枚举的双向转换说明该字段经历过「自由文本 → 受控枚举」的演进。
- 未提供版本记录；无 (document_claim，未证实) 主张。

本页按 concept 约定不设锚点块。

---END FILE---

---FILE: concepts/op_contact.md ---
---
type: concept
title: 运营对接人与组别（op_contact）
page_key: concepts/op_contact
domain: 租户项目
status: draft
aliases: [运营对接人, op_contact_a, op_contact_b, op_contact_a_group, 风控对接人, 查验对接人]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
maps_to:
  - tenant_project.op_contact_a
  - tenant_project.op_contact_b
  - tenant_project.op_contact_a_group
  - tenant_project.risk_control_contact_a
  - tenant_project.risk_control_contact_b
  - tenant_project.verification_contact
field_targets:
  - table: tenant_project
    field: op_contact_a
    note: 运营对接人A；导入导出时按运营人员姓名/ID 转换
  - table: tenant_project
    field: op_contact_b
    note: 运营对接人B；数据库以 JSON 数组字符串存储，DTO 转为 List<String>
  - table: tenant_project
    field: op_contact_a_group
    note: 运营组别；导入时按运营对接人A的组别刷新
adjudication: >
  「对接人」是一组按角色区分的字段（运营 A/B、查验、风控 A/B），
  它们共用一个转换规则：导入导出时按运营人员姓名/ID 互转（见 rules/import_length_limits 之外的导入校验）。
  其中 B 类字段（op_contact_b、risk_control_contact_b）是复数语义，库中以 JSON 数组字符串存储；
  A 类字段是单值。组别 op_contact_a_group 只跟随 A 刷新。
also_confused_with:
  - concepts/project_tag
contract_version: "0.1"
---

本术语桥把「对接人」这一族字段归并为一个概念：它们共享姓名/ID 转换与人员存在性校验，区别只在角色与是否支持多人。库中既存姓名也存 ID 的转换逻辑，要求读取时先明确当前存的是哪一侧。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该概念支撑项目导入导出与运营归属维护，见 [[tables/tenant_project]]。

## 版本演进
- B 类字段以 JSON 数组字符串入库、DTO 转 List<String>，是「单值 → 多值」扩展后留下的表达方式。
- 未提供版本记录；无 (document_claim，未证实) 主张。

本页按 concept 约定不设锚点块。

---END FILE---

---FILE: rules/tenant_product_unique_key.md ---
---
type: rule
title: 租户产品唯一键约束
page_key: rules/tenant_product_unique_key
domain: 租户产品
status: draft
aliases: [tenant_product_id, 租户产品唯一键]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
contract_version: "0.1"
---

该约束规定 [[tables/tenant_product]] 中一个租户对同一平台产品只能有一条记录，是「租户产品」这一概念的建模基础，也是 [[concepts/platform_product_vs_tenant_product]] 中三级结构成立的前提。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。唯一键决定了重复开通时是幂等返回还是新增记录，配合 [[rules/activation_idempotency]] 一起理解。

## 版本演进
platform_product_id 上另有普通索引，唯一性由 tenant_id 组合保证；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 租户产品唯一键
table: tenant_product
fields: [tenant_id, platform_product_id]
statement: 租户 id 与 platform_product_id 组成唯一键 tenant_product_id
evidence: db
```

---END FILE---

---FILE: rules/tenant_project_enable_filter.md ---
---
type: rule
title: 租户项目仅取有效记录
page_key: rules/tenant_project_enable_filter
domain: 租户项目
status: draft
aliases: [enable='Y', 租户项目逻辑删除]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
contract_version: "0.1"
---

该规则规定 [[tables/tenant_project]] 的读取一律限定 enable='Y'，删除走 domainService.delete（逻辑删除）。它决定上游看到的项目集合，是 [[calibers/project_effective]] 的实现依据。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则影响项目列表、导出与按产品同步等所有查询场景。

## 版本演进
以逻辑删除替代物理删除后，任何绕过 enable 过滤的自定义 SQL 都会读到已删除项目，属需要长期守住的约束；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 租户项目读取限定 enable='Y'
table: tenant_project
fields: [enable]
statement: 代码查询与导出普遍限定 enable='Y'，删除操作调用 domainService.delete
evidence: code
```

---END FILE---

---FILE: rules/interworking_product_cancel_guard.md ---
---
type: rule
title: 互通产品取消开通前置约束
page_key: rules/interworking_product_cancel_guard
domain: 互通产品
status: draft
aliases: [不允许取消开通, 互通产品取消]
oid: 1
scope:
  databases: []
sources:
  - code:TenantInterworkingProductApplication
contract_version: "0.1"
---

该规则约束 [[tables/cust_interworking_product]] 的取消动作：一旦互通产品已被项目关联，就不允许取消开通。它是 [[processes/interworking_product_open_status]] 中 OPENED → 未开通 迁移的前置条件。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则存在的目的是避免已投产项目失去其产品配置。

## 版本演进
本次语义分析中该迁移的代码路径证据被截断，规则文本来自迁移描述；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 互通产品关联项目后不允许取消开通
table: cust_interworking_product
fields: [open_status]
statement: TenantInterworkingProductApplication.cancel 取消开通，关联项目后不允许取消
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/[证据截断]/TenantInterworkingProductApplication.java:cancel"
```

---END FILE---

---REVIEW: rule | 互通产品取消开通前置约束---
该规则的 code_path 证据在原语义分析中被截断于 "…/product/application/p"，本页按迁移描述中给出的类名与方法名（TenantInterworkingProductApplication.cancel）登记，并在路径中标注「证据截断」。需补齐完整路径与「关联项目」的判断实现后复核。
---END REVIEW---

---FILE: rules/project_effective_requires_config_check.md ---
---
type: rule
title: 项目生效前的配置校验
page_key: rules/project_effective_requires_config_check
domain: 租户项目
status: draft
aliases: [config_json 校验, BEECREDIT 生效校验]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
contract_version: "0.1"
---

该规则规定 [[tables/tenant_project]] 的 config_json 在生效链路中的作用：BEECREDIT 类项目在生效前需解析并校验配置状态，ACFLOW/RVSFACTOR 类项目则在生效时用其完成开户或查询业务系统配置。它使「生效」成为带前置校验的动作，见 [[processes/tenant_project_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则保证项目生效时下游业务系统所需的配置已经可用。

## 版本演进
同一列对不同产品线承担「校验」与「开户/查询」两类用途，是产品线扩展后复用同一列的结果；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 项目生效前的配置校验
table: tenant_project
fields: [config_json]
statement: BEECREDIT 生效前解析校验配置状态，ACFLOW/RVSFACTOR 生效时用于开户/查询业务系统配置
evidence: code
```

---END FILE---

---FILE: rules/import_length_limits.md ---
---
type: rule
title: 项目导入字段长度限制
page_key: rules/import_length_limits
domain: 租户项目
status: draft
aliases: [导入长度限制, bussiness_project_relation 50, invite_customer_service_words 500]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
contract_version: "0.1"
---

该规则规定 [[tables/tenant_project]] 导入时两个长文本字段的上限：运营项目归属不超过 50，邀请信息-客服话术不超过 500。超出时导入应被拒绝。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则与同表的对接人转换规则一起构成导入校验集合，见 [[concepts/op_contact]]。

## 版本演进
长度上限仅在导入侧校验，库端约束未知；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 项目导入长度限制
table: tenant_project
fields: [bussiness_project_relation, invite_customer_service_words]
statement: 运营项目归属导入长度限制不超过 50；邀请信息-客服话术导入时长度限制不超过 500
evidence: code
```

---END FILE---

---FILE: rules/activation_idempotency.md ---
---
type: rule
title: 租户产品开通幂等
page_key: rules/activation_idempotency
domain: 租户产品
status: draft
aliases: [开通幂等, activeAndNotify 幂等]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProductApplication
contract_version: "0.1"
---

该规则规定 [[tables/tenant_product]] 已处于 Y（已开通）时，activeAndNotify 再次被调用直接返回，不重复推进状态、不重复通知。它是 [[processes/tenant_product_open_status]] 中 Y → Y 自环的依据，与唯一键约束 [[rules/tenant_product_unique_key]] 一致。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。多级回调场景下同一开通请求可能被重复投递，幂等是必要的保护。

## 版本演进
同一方法同时承担「非 ACFLOW/ORDER 直接开通」「ACFLOW/ORDER 置开通中」「已开通直接返回」三种分支，是产品线扩展后集中在一个入口的结果；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 租户产品开通幂等
table: tenant_product
fields: [open_status]
statement: activeAndNotify 幂等命中已开通直接返回
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
```

---END FILE---

---FILE: rules/effective_on_approval_finished.md ---
---
type: rule
title: 上线审批通过后自动生效项目
page_key: rules/effective_on_approval_finished
domain: 租户项目
status: draft
aliases: [审批完成生效项目, effectiveProjectOnApprovalFinished]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

该规则规定 [[tables/tenant_project_approval]] 的工作流完成通过后，系统调用 effective 将对应项目置为 EFFECTIVE，形成「审批完成 → 项目生效」的自动链路，连接了 [[processes/project_approval_workflow_status]] 与 [[processes/tenant_project_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则使项目生效可以不由人工直接触发，而是由审批结果驱动。

## 版本演进
项目状态因此存在两条进入 EFFECTIVE 的路径（人工 effective 与审批自动生效），需在审计时区分来源；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 上线审批完成通过后自动生效项目
table: tenant_project
fields: [project_status]
statement: 上线审批完成通过后 effectiveProjectOnApprovalFinished 调 effective
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished"
```

---END FILE---

---FILE: rules/back_agreement_check.md ---
---
type: rule
title: 后补合作协议判断触发条件
page_key: rules/back_agreement_check
domain: 租户项目
status: draft
aliases: [is_back_agreement, 后补合作协议]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

该规则规定当 [[tables/tenant_project_approval_flow]] 中业务经理节点通过且 is_back_agreement=Y 时，触发后补合作协议的判断，对应节点状态进入 APPROVED，见 [[processes/project_approval_node_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则把审批节点结果与协议补签动作绑定，是审批链路的下游分支。

## 版本演进
触发条件同时依赖节点状态与 is_back_agreement 标志，说明协议补签是后加的可选分支；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 后补合作协议判断触发条件
table: tenant_project_approval_flow
fields: [node_status]
statement: 业务经理节点通过且 is_back_agreement=Y 触发后补合作协议判断
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:isStartBackAgreement"
```

---END FILE---