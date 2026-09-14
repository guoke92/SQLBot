---FILE: tables/cust_project_rel.md---
---
type: table
title: 产融项目关联企业表
page_key: cust_project_rel
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_rel
  - 产融项目企业关联表
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:ProjectReportApplication.java:getCompaniesByProjectId
  - code_path:TenantProjectApplication.java:syncProjectContactToCustRel
  - code_path:CustProjectController.java:updateRelPrjStatus
  - code_path:CustProjectRelDO.java
  - code_path:CustCompanyInfoApplication.java
  - code_path:CustProjectRelEnhanceService.java
contract_version: "0.1"
---

cust_project_rel 是[[concepts/chanrong|产融]]侧的落库表，记录项目（tenant_project）与企业（cust_company_info）的关联关系，并承载运营对接人、风控对接人、查验对接人等联系信息。项目报表中「产融项目下的关联企业」查询即以本表为入口，再反查企业主数据，因此它是[[calibers/project_ledger_company_query|产融项目台账企业查询口径]]的事实来源。

## 需求背景

需求文档主张：cust_project_rel 表存储项目与企业关联关系及运营对接人信息。该主张经代码确认（ProjectReportApplication.java:getCompaniesByProjectId），锚点块 evidence 采用双源写法。

## 版本演进

v0 契约首版。当前由代码与 DB 证据确认的字段含运营/风控/查验三类联系人、逻辑删除标志 enable 与项目开通状态 project_open_status；status 字段（0/1）另有 [[enums/cust_project_rel_status|cust_project_rel.status 值点]] 记录。关系审计中的非确认项（product_id 直连 tenant_product.platform_product_id、product_id 直连 cust_change_cfg.id）已判为 reject，不在契约中断言。

```ground:table
table: cust_project_rel
fields:
  - name: company_type
    type: unknown
    desc: 客户角色（只取一个），如 CORE/SUPPLIER/FINANCE 等
    dict: ""
  - name: op_contact_a
    type: unknown
    desc: 运营对接人A的运营人员ID
    dict: ""
  - name: op_contact_b
    type: unknown
    desc: 运营对接人B的运营人员ID列表，JSON数组字符串
    dict: ""
  - name: op_contact_a_group
    type: unknown
    desc: 运营对接人A所属组别
    dict: ""
  - name: verification_contact
    type: unknown
    desc: 查验对接人
    dict: ""
  - name: risk_control_contact_a
    type: unknown
    desc: 风控对接人A
    dict: ""
  - name: risk_control_contact_b
    type: unknown
    desc: 风控对接人B列表，JSON数组字符串
    dict: ""
  - name: enable
    type: unknown
    desc: 逻辑删除标志，Y有效
    dict: ""
  - name: project_open_status
    type: unknown
    desc: 项目开通状态，NOT_OPEN/OPENED
    dict: ""
  - name: status
    type: unknown
    desc: 状态，0=未生效，1=已生效
    dict: ""
evidence: "db + code_path:ProjectReportApplication.java:getCompaniesByProjectId + reqdoc:cust-project-rel-company-relation"
```

关系锚点（来自关系审计，供下游 JOIN 参考）：

- cust_project_rel.project_id → tenant_project.id（FK，confirm，ProjectReportApplication.getCompaniesByProjectId）
- cust_project_rel.product_id → tenant_product.id（FK，confirm，CustProjectController.updateRelPrjStatus）
- cust_project_rel.ref_cust_project_rel_cust_company_info → cust_company_info.code（FK，confirm，ProjectReportApplication.getCompaniesByProjectId）
- cust_project_rel.ref_cust_project_rel_platform_product → platform_product.code（FK，confirm，CustProjectRelDO.java）
- cust_project_rel.channel_code ↔ tenant_project.channel_code（SHARED_KEY，derived：DTO 展示拷贝，非 JOIN 条件，CustCompanyInfoApplication.java）
- cust_project_rel.op_contact_a ↔ tenant_project.op_contact_a（SHARED_KEY，derived：TenantProjectApplication.syncProjectContactToCustRel 数据同步，将项目对接人同步到关联企业）
- cust_project_rel.company_id ← cust_project_code_record.company_id → cust_company_info.id（FK，confirm，CustProjectRelEnhanceService.java）

相关：[[tables/tenant_project]]、[[tables/cust_project_code_record]]、[[concepts/project_ledger|项目台账]]。

---END FILE---

---FILE: tables/cust_project_pushcust.md---
---
type: table
title: 客户项目推送客户SSO渠道表
page_key: cust_project_pushcust
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_pushcust
  - 项目推送渠道表
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
---

cust_project_pushcust 描述从一个系统跳转到另一个系统时所使用的 SSO 渠道配置，字段以「起始系统」与「跳转系统」两侧成对出现，供免登跳转链路读取。它是项目报表/统计主题中唯一与 SSO 渠道相关的落库表，因此需求文档中关于登录改造的主张被挂在[[concepts/project_ledger|项目台账]]之外的此处做边界澄清。

## 需求背景

本次语义分析中，本表仅有 DB 证据（字段语义），无代码路径证据；SSO 渠道的具体取值集合未在分析中给出，契约不发明字典值。

## 版本演进

v0 契约首版，仅登记两个渠道字段。需求文档中「SSO 验证码登录改造」相关主张经判定与本主题（项目报表/统计/上报）无关，未证实，见下方 REVIEW。

```ground:table
table: cust_project_pushcust
fields:
  - name: source_sso_channel
    type: unknown
    desc: 起始系统的SSO渠道
    dict: ""
  - name: target_sso_channel
    type: unknown
    desc: 跳转系统的SSO渠道
    dict: ""
evidence: db
```

---REVIEW: table | 客户项目推送客户SSO渠道表---
需求文档主张「SSO 验证码登录改造」与项目报表/统计/上报主题无关（code_status=uncovered，action=review）。当前无代码证据可判断该主张与 cust_project_pushcust 的 source_sso_channel/target_sso_channel 是否存在隐性耦合：本表两个渠道字段的取值域、由谁写入、是否受登录改造影响均未确认。需业务方与代码 owner 确认后再决定是否将本表纳入本主题契约或移出至登录域。
---END REVIEW---

---END FILE---

---FILE: tables/cust_project_code_record.md---
---
type: table
title: 项目编码记录表
page_key: cust_project_code_record
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_code_record
  - 项目编码记录
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CustProjectRelEnhanceService.java
contract_version: "0.1"
---

cust_project_code_record 记录企业/项目编码类数据的写入与校验结果，type 区分产生记录的场景（如 userCompanyRegister、产品中心等），status 表示该次编码是否正确。它与[[tables/cust_project_rel|cust_project_rel]]通过 company_id 关联企业主数据（FK，confirm，CustProjectRelEnhanceService.java）。

## 需求背景

本表在本次分析中只有 DB 证据，未出现需求文档主张；字段语义以 DB 值为准。

## 版本演进

v0 契约首版。status 的 DB 实际取值域为 Y/N，与代码枚举 StatusEnum.EFFECTIVE/INVALID 的存储值不一致（enum_audit verdict=reject），详见 [[enums/cust_project_code_record_status|cust_project_code_record.status 值点]]。

```ground:table
table: cust_project_code_record
fields:
  - name: type
    type: unknown
    desc: 类型（如userCompanyRegister、产品中心等）
    dict: ""
  - name: status
    type: unknown
    desc: 是否正确状态，Y/N
    dict: ""
evidence: db
```

---END FILE---

---FILE: tables/wechat_project_approval_apply.md---
---
type: table
title: 企微项目审批申请表
page_key: wechat_project_approval_apply
domain: 项目报表/统计/上报
status: draft
aliases:
  - wechat_project_approval_apply
  - 企微立项审批申请
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.buildPageWrapper
  - code_path:ProjectStatisticsApplication.update
  - code_path:ProjectStatisticsApplication.applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
  - code_path:ProjectStatisticsApplication.listApprovedMissingSolutionManagerForRemind
  - code_path:ProjectStatisticsApplication.validateBatchChangePlanMgrRows
  - code_path:ProjectStatisticsApplication.dataSourceToChinese
  - code_path:ProjectStatisticsApplication.kaWhiteLabelToCode
contract_version: "0.1"
---

wechat_project_approval_apply 是项目立项统计页的主表，既承载来自企微审批的真实立项数据，也承载手工录入的[[concepts/simulated_project|模拟立项]]数据。列表、导出、提醒 Job 与批量变更都围绕本表展开，字段分为三类：审批来源标识（sp_type、system_delivery、act_procinst_status）、项目属性（project_type、project_phase、data_source、ka_white_label）、以及人员与产品信息（方案经理、运营对接人、产品类型、首笔落地时间）。

## 需求背景

需求文档未就本表单独提出主张；本次分析的全部字段语义均来自代码。项目阶段、企微审批状态、数据来源三个状态机分别见 [[processes/project_phase]]、[[processes/act_procinst_status]]、[[processes/data_source]]。

## 版本演进

v0 契约首版。人员字段采用「中文姓名字段 + 企微 userId 列表字段」的双轨存储：solution_manager 为姓名 CSV，solution_manager_wxid 为企微 userId 的 JSON 数组字符串，改人时由 [[rules/solution_manager_change_linkage|方案经理变更联动]] 保证两者一致，并把原值合并进 old_solution_manager。product_type_arr（编码 JSON）与 product_type（中文 CSV）同样成对。

```ground:table
table: wechat_project_approval_apply
fields:
  - name: sp_type
    type: unknown
    desc: 审批类型，固定为'金融科技业务'
    dict: ""
  - name: system_delivery
    type: unknown
    desc: 系统交付方式，SaaS/Saas+本地化
    dict: ""
  - name: act_procinst_status
    type: unknown
    desc: 企微审批状态，'2'表示审批通过
    dict: ""
  - name: project_type
    type: unknown
    desc: 项目类型，MAIN=主项目，SUB=子项目
    dict: ""
  - name: project_phase
    type: unknown
    desc: 项目阶段，IMPLEMENTATION/OPERATION/HANG等
    dict: ""
  - name: data_source
    type: unknown
    desc: 数据来源，MANUAL=模拟立项，WECHAT=真实立项
    dict: ""
  - name: ka_white_label
    type: unknown
    desc: KA是否贴牌，Y/N
    dict: ""
  - name: solution_manager
    type: unknown
    desc: 方案经理姓名CSV
    dict: ""
  - name: solution_manager_wxid
    type: unknown
    desc: 方案经理企微userId列表的JSON数组字符串
    dict: ""
  - name: old_solution_manager
    type: unknown
    desc: 前方案经理姓名CSV
    dict: ""
  - name: product_type_arr
    type: unknown
    desc: 产品类型编码的JSON数组，如["1","9"]
    dict: ""
  - name: product_type
    type: unknown
    desc: 产品类型中文CSV
    dict: ""
  - name: first_settlement_time
    type: unknown
    desc: 首笔落地时间
    dict: ""
  - name: op_contact
    type: unknown
    desc: 运营对接人（单个）
    dict: ""
  - name: op_contact_group
    type: unknown
    desc: 运营组别
    dict: ""
evidence: code_path:ProjectStatisticsApplication.buildPageWrapper
```

相关：[[calibers/project_statistics_list_scope|项目立项统计列表基础范围]]、[[calibers/missing_solution_manager_remind|缺方案经理提醒范围]]、[[rules/project_phase_linkage|项目阶段联动]]、[[concepts/solution_manager|方案经理]]。

---END FILE---

---FILE: tables/tenant_project.md---
---
type: table
title: 项目台账主表
page_key: tenant_project
domain: 项目报表/统计/上报
status: draft
aliases:
  - tenant_project
  - 项目运营配置
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectReportController.generateTextForProjectReport
  - code_path:CustProjectController.java:syncCustInfo
  - code_path:ProjectReportApplication.exportProjectReport
contract_version: "0.1"
---

tenant_project 是[[concepts/project_ledger|项目台账]]的主表，导出时所见的「项目运营配置」即本表。它同时是[[tables/cust_project_rel|cust_project_rel]] 的关联主体（project_id → tenant_project.id，FK confirm），并通过 tenant_project.channel 区分企业数据来源（'产融平台' → 产融，其余 → 讯易链）。

## 需求背景

需求文档主张：tenant_project 表包含 op_contact_a/b、solution_manager、business_group、custom_field_one/two/three、project_tag、bussiness_project_relation 等字段，经代码确认（CustProjectController.java:syncCustInfo），锚点块 evidence 采用双源写法。这些字段的中文语义本次分析未给出，故 ground:table 仅登记有字段级语义证据的三个字段，其余以本段文字记录。

## 版本演进

v0 契约首版。已确认字段中，text 由[[rules/departed_contact_tip|已离职运营人员提示]]规则写入，is_prd 区分生产数据（1/Y）与非生产数据（0/N），project_status='1' 表示项目已生效。tenant_project.channel 作为导出 source 判定依据见 [[calibers/project_ledger_export_source|项目台账导出企业source判定]]。

```ground:table
table: tenant_project
fields:
  - name: text
    type: unknown
    desc: 提示文本，记录离职人员信息
    dict: ""
  - name: project_status
    type: unknown
    desc: 项目状态，'1'表示已生效
    dict: ""
  - name: is_prd
    type: unknown
    desc: 是否生产数据，1/Y=是，0/N=否
    dict: ""
evidence: "code_path:ProjectReportController.generateTextForProjectReport + code_path:CustProjectController.java:syncCustInfo + reqdoc:tenant-project-field-list"
```

---END FILE---

---FILE: processes/project_phase.md---
---
type: process
title: 项目阶段状态机
page_key: project_phase
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目阶段
  - project_phase
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
  - code_path:ProjectStatisticsApplication.java:normalizeLegacyProjectPhaseCode
contract_version: "0.1"
---

项目阶段描述一个立项申请从立项到实施、再到持续运营或挂起的生命周期位置，落库字段为 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]].project_phase。阶段推进不是纯人工操作：审批通过与首笔落地时间写入会触发自动流转，历史遗留值在查询时被规范化。

## 需求背景

需求文档未单独描述该状态机；本次分析的状态与迁移均来自代码常量与方法名证据。

## 版本演进

v0 契约首版。当前有两条迁移规则：一是审批通过且首笔落地时间更新时的自动置为 OPERATION（见 [[rules/project_phase_linkage|项目阶段联动]]），二是查询期把历史值 TERMINATION 规范化为 HANG。INITIATION 为立项起点，尚未观察到由代码写入的入边与出边。

```ground:process
name: 项目阶段
field: wechat_project_approval_apply.project_phase
states:
  - value: INITIATION
    label: 立项阶段
    source: code_const
  - value: IMPLEMENTATION
    label: 实施阶段
    source: code_const
  - value: OPERATION
    label: 持续运营
    source: code_const
  - value: HANG
    label: 挂起
    source: code_const
transitions:
  - from: "*"
    event: 首笔落地时间更新且审批通过
    to: OPERATION
    evidence: code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
  - from: TERMINATION
    event: 查询时规范化
    to: HANG
    evidence: code_path:ProjectStatisticsApplication.java:normalizeLegacyProjectPhaseCode
evidence: code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
```

---END FILE---

---FILE: processes/act_procinst_status.md---
---
type: process
title: 企微审批状态状态机
page_key: act_procinst_status
domain: 项目报表/统计/上报
status: draft
aliases:
  - 企微审批状态
  - act_procinst_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:ACT_PROCINST_APPROVED
contract_version: "0.1"
---

act_procinst_status 表示企微审批流实例的当前状态，落在 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]] 上。在本主题中它主要作为筛选条件使用：只有审批通过（'2'）的立项才进入提醒范围与阶段自动流转的判定。

## 需求背景

需求文档未单独描述该状态机；分析中仅有「审批通过」一个值点与其常量名。

## 版本演进

v0 契约首版，只登记已确认的 '2'（审批通过）。其余状态值（如审批中、驳回）在本次分析中无证据，契约不发明；待补证后再扩展本页。值点明细见 [[enums/wechat_project_approval_apply_act_procinst_status|act_procinst_status 值点]]（如与基线写值点不一致以写值点与 DB 为准）。

```ground:process
name: 企微审批状态
field: wechat_project_approval_apply.act_procinst_status
states:
  - value: "2"
    label: 审批通过
    source: code_const
transitions: []
evidence: code_path:ProjectStatisticsApplication.java:ACT_PROCINST_APPROVED
```

---END FILE---

---FILE: processes/data_source.md---
---
type: process
title: 数据来源状态机
page_key: data_source
domain: 项目报表/统计/上报
status: draft
aliases:
  - 数据来源
  - data_source
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:DATA_SOURCE_MANUAL
  - code_path:ProjectStatisticsApplication.java:dataSourceToChinese
contract_version: "0.1"
---

data_source 区分 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]] 中的记录是企微审批回流的真实数据，还是页面手工制造的模拟数据。它是[[concepts/simulated_project|模拟立项]]与[[concepts/real_project|真实立项]]两个术语的分界字段，也是统计口径中判断数据可信度的入口。

## 需求背景

需求文档未单独描述该状态机；两个值点及其中文映射均由代码常量与转换方法确认。

## 版本演进

v0 契约首版。MANUAL 记录通常与模拟单号前缀（MN）配套出现，WECHAT 记录来自企微审批。该字段非流程型状态，无迁移边。

```ground:process
name: 数据来源
field: wechat_project_approval_apply.data_source
states:
  - value: MANUAL
    label: 模拟立项
    source: code_const
  - value: WECHAT
    label: 真实立项
    source: code_const
transitions: []
evidence: code_path:ProjectStatisticsApplication.java:dataSourceToChinese
```

---END FILE---

---FILE: calibers/project_statistics_list_scope.md---
---
type: caliber
title: 项目立项统计列表基础范围
page_key: project_statistics_list_scope
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目立项统计列表基础范围
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.buildPageWrapper
contract_version: "0.1"
---

这是项目立项统计页列表的基线过滤条件：只看审批类型为「金融科技业务」且交付方式属于 SaaS 与 Saas+本地化的记录。该条件由 buildPageWrapper 统一拼装，页面上任何二次筛选都建立在此范围之上，因此统计口径的分子分母都以它为先决条件。

## 需求背景

需求文档未单独给出该口径描述；口径内容逐字来自代码构建的分页条件。

## 版本演进

v0 契约首版。注意 system_delivery 的两个取值大小写敏感（'SaaS' 与 'Saas+本地化'），后续若新增交付方式需同步本口径，否则会从统计范围中静默丢失。相关：[[tables/wechat_project_approval_apply]]、[[calibers/missing_solution_manager_remind]]。

```ground:caliber
name: 项目立项统计列表基础范围
predicate: "wechat_project_approval_apply.sp_type = '金融科技业务' AND wechat_project_approval_apply.system_delivery IN ('SaaS','Saas+本地化')"
scope: 项目立项统计页列表
evidence: code_path:ProjectStatisticsApplication.buildPageWrapper
```

---END FILE---

---FILE: calibers/project_ledger_company_query.md---
---
type: caliber
title: 产融项目台账企业查询口径
page_key: project_ledger_company_query
domain: 项目报表/统计/上报
status: draft
aliases:
  - 产融项目台账企业查询口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectReportApplication.getCompaniesByProjectId
contract_version: "0.1"
---

查询某个项目下挂的关联企业时的标准口径：以 project_id 定位 [[tables/cust_project_rel|cust_project_rel]]，并要求 enable='Y'（逻辑有效）。enable 的过滤不可省略，否则会带出被逻辑删除的历史关联企业，污染企业数量与联系人信息。

## 需求背景

需求文档主张 cust_project_rel 存储项目与企业关联关系及运营对接人信息，该口径正是其取数落地方式。

## 版本演进

v0 契约首版。口径只覆盖 [[concepts/chanrong|产融]]侧数据；讯易链侧走洞察平台/wec_project_cust_operation_rel，两者不可混用，边界见 [[concepts/chanrong]]。

```ground:caliber
name: 产融项目台账企业查询口径
predicate: "cust_project_rel.project_id = ? AND cust_project_rel.enable = 'Y'"
scope: 产融项目下的关联企业
evidence: code_path:ProjectReportApplication.getCompaniesByProjectId
```

---END FILE---

---FILE: calibers/project_ledger_export_source.md---
---
type: caliber
title: 项目台账导出企业source判定
page_key: project_ledger_export_source
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目台账导出企业source判定
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectReportApplication.exportProjectReport
contract_version: "0.1"
---

导出项目台账时，企业行的「数据来源」列由 [[tables/tenant_project|tenant_project]].channel 三分法判定：等于 '产融平台' 输出「产融」，其余一律输出「讯易链」。这是一个兜底式二分，值域中不存在第三类展示文案。

## 需求背景

需求文档未单独描述该判定；口径逐字来自导出方法中的三元表达式。

## 版本演进

v0 契约首版。该口径与 [[concepts/chanrong|产融]]/讯易链的数据来源边界直接对应：产融走本地表 cust_project_rel，讯易链走洞察平台。若未来新增渠道，需先改造本判定再新增来源文案。

```ground:caliber
name: 项目台账导出企业source判定
predicate: "tenant_project.channel = '产融平台' ? '产融' : '讯易链'"
scope: 导出时企业数据来源
evidence: code_path:ProjectReportApplication.exportProjectReport
```

---END FILE---

---FILE: calibers/missing_solution_manager_remind.md---
---
type: caliber
title: 缺方案经理提醒范围
page_key: missing_solution_manager_remind
domain: 项目报表/统计/上报
status: draft
aliases:
  - 缺方案经理提醒范围
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.listApprovedMissingSolutionManagerForRemind
contract_version: "0.1"
---

提醒 Job 的取数范围：审批已通过（act_procinst_status='2'）但方案经理为空（solution_manager IS NULL）的立项记录。它是[[concepts/solution_manager|方案经理]]责任人缺失的唯一监控口径，也是[[rules/batch_change_plan_mgr_limit|批量变更方案经理限制]]之外的人员数据质量兜底。

## 需求背景

需求文档未单独描述该提醒口径；范围逐字来自 Job 查询方法。

## 版本演进

v0 契约首版。口径只判 NULL，对空字符串 CSV 不敏感；如需覆盖空串需另行确认。相关：[[processes/act_procinst_status]]、[[tables/wechat_project_approval_apply]]。

```ground:caliber
name: 缺方案经理提醒范围
predicate: "wechat_project_approval_apply.act_procinst_status = '2' AND wechat_project_approval_apply.solution_manager IS NULL"
scope: 提醒Job
evidence: code_path:ProjectStatisticsApplication.listApprovedMissingSolutionManagerForRemind
```

---END FILE---

---FILE: concepts/chanrong.md---
---
type: concept
title: 产融
page_key: chanrong
domain: 项目报表/统计/上报
status: draft
aliases:
  - 产融
  - 产融平台
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectReportApplication.getCompaniesByProjectId
  - code_path:ProjectReportApplication.exportProjectReport
contract_version: "0.1"
maps_to: cust_project_rel
field_targets:
  - cust_project_rel.project_id
adjudication: boundary
also_confused_with:
  - 讯易链
---

「产融」在本主题中首先是一个数据来源标识，而不是泛指金融业务：它的落库位置是本地的 [[tables/cust_project_rel|cust_project_rel]] 及其关联的项目主体。做企业清单、对接人、联系人统计时，凡标注来源为产融的数据都应从本地表取，走 [[calibers/project_ledger_company_query|产融项目台账企业查询口径]]。

## 需求背景

需求文档中「产融平台」与「产融」交替出现，本页判定二者为同义（synonym 侧的同义词由 aliases 承载），但「产融」与「讯易链」之间是边界（adjudication=boundary），不可互换。

## 版本演进

v0 契约首版。边界说明：产融走本地表 cust_project_rel，讯易链走洞察平台/wec_project_cust_operation_rel；导出时的来源文案由 [[calibers/project_ledger_export_source|项目台账导出企业source判定]] 从 tenant_project.channel 反推。易混项：讯易链。

---END FILE---

---FILE: concepts/project_ledger.md---
---
type: concept
title: 项目台账
page_key: project_ledger
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目台账
  - 项目运营配置
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectReportController.generateTextForProjectReport
  - code_path:ProjectReportApplication.exportProjectReport
contract_version: "0.1"
maps_to: tenant_project
field_targets: []
adjudication: synonym
also_confused_with: []
---

「项目台账」是业务口头的模块名，其物理承载是 [[tables/tenant_project|tenant_project]]。台账视角关注的是项目的运营配置与责任人健康度：项目状态是否生效、是否生产数据、对接人是否离职（写入 text 提示文本），以及导出时企业行的来源归属。

## 需求背景

需求文档与导出功能对该模块使用两个名字：「项目台账」与「项目运营配置」——导出文件名使用「项目运营配置」。本页判定二者为同义（adjudication=synonym），不做语义切分。

## 版本演进

v0 契约首版。相关规则与口径：[[rules/departed_contact_tip|已离职运营人员提示]]、[[calibers/project_ledger_export_source|项目台账导出企业source判定]]、[[calibers/project_ledger_company_query|产融项目台账企业查询口径]]。

---END FILE---

---FILE: concepts/simulated_project.md---
---
type: concept
title: 模拟立项
page_key: simulated_project
domain: 项目报表/统计/上报
status: draft
aliases:
  - 模拟立项
  - MANUAL
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:DATA_SOURCE_MANUAL
contract_version: "0.1"
maps_to: "wechat_project_approval_apply.data_source='MANUAL'"
field_targets:
  - wechat_project_approval_apply.data_source
adjudication: boundary
also_confused_with:
  - 真实立项
---

「模拟立项」指不经过企微审批、由页面手工制造出来的立项数据，其判定字段是 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]].data_source='MANUAL'，并常伴随以 MN 开头的 spNo。统计与提醒若不加区分，会把模拟数据算进真实业务量，因此在分析、导出与提醒场景都要求显式声明是否包含模拟立项。

## 需求背景

需求文档中出现「模拟立项」与「MANUAL」两种称法，本页判定为同一概念；它与[[concepts/real_project|真实立项]]之间是边界关系（adjudication=boundary），由 data_source 字段值区分，而非由单号前缀单独决定。

## 版本演进

v0 契约首版。边界：模拟立项 spNo 以 MN 开头、data_source=MANUAL；真实立项 data_source=WECHAT。见 [[processes/data_source|数据来源状态机]]。

---END FILE---

---FILE: concepts/real_project.md---
---
type: concept
title: 真实立项
page_key: real_project
domain: 项目报表/统计/上报
status: draft
aliases:
  - 真实立项
  - WECHAT
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:dataSourceToChinese
contract_version: "0.1"
maps_to: "wechat_project_approval_apply.data_source='WECHAT'"
field_targets:
  - wechat_project_approval_apply.data_source
adjudication: boundary
also_confused_with:
  - 模拟立项
---

「真实立项」指经企微审批流回流、具备真实审批实例的立项数据，判定字段为 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]].data_source='WECHAT'。只有真实立项才具备可信的审批状态（act_procinst_status）与阶段流转语义，[[rules/project_phase_linkage|项目阶段联动]] 等自动流转也建立在这一前提上。

## 需求背景

需求文档以「真实立项」与「WECHAT」指代同一概念；与[[concepts/simulated_project|模拟立项]]之间为边界关系，边界由 data_source 取值确定。

## 版本演进

v0 契约首版。边界：来自企微审批的真实数据（data_source=WECHAT），可与审批通过状态（act_procinst_status='2'）联合使用，见 [[processes/act_procinst_status|企微审批状态状态机]]。

---END FILE---

---FILE: concepts/solution_manager.md---
---
type: concept
title: 方案经理
page_key: solution_manager
domain: 项目报表/统计/上报
status: draft
aliases:
  - 方案经理
  - solutionManager
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.update
  - code_path:ProjectStatisticsApplication.listApprovedMissingSolutionManagerForRemind
  - code_path:ProjectStatisticsApplication.validateBatchChangePlanMgrRows
contract_version: "0.1"
maps_to: wechat_project_approval_apply.solution_manager
field_targets:
  - wechat_project_approval_apply.solution_manager
  - wechat_project_approval_apply.solution_manager_wxid
  - wechat_project_approval_apply.old_solution_manager
adjudication: boundary
also_confused_with:
  - 业务经理
---

方案经理是立项申请上的方案责任人，落库在三联字段上：solution_manager（姓名 CSV）、solution_manager_wxid（企微 userId 的 JSON 数组字符串，用于通讯录校验与消息触达）、old_solution_manager（原方案经理姓名 CSV，用于留痕）。本页区分的是「谁是方案经理」这一问题：人员必须在企微通讯录中存在，且属 Saas 方案部。

## 需求背景

需求文档使用「方案经理」与「solutionManager」两种称法，属同一概念。它与「业务经理」之间为边界关系（adjudication=boundary）：方案经理属 Saas 方案部，业务经理属客户营销部，两者不可互相代入校验。

## 版本演进

v0 契约首版。变更与校验分别见 [[rules/solution_manager_change_linkage|方案经理变更联动]]、[[rules/batch_change_plan_mgr_limit|批量变更方案经理限制]]，缺失监控见 [[calibers/missing_solution_manager_remind|缺方案经理提醒范围]]。易混项：业务经理。

---END FILE---

---FILE: rules/project_phase_linkage.md---
---
type: rule
title: 项目阶段联动
page_key: project_phase_linkage
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目阶段联动
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
contract_version: "0.1"
---

当一条立项记录的审批已通过、且首笔落地时间被更新为非空时，系统把项目阶段自动置为持续运营（OPERATION）。这是一次由数据变更触发的写动作，而非页面上的显式操作，因此导入与编辑两条入口都会命中。

## 需求背景

需求文档未单列此规则；规则内容来自代码方法语义。

## 版本演进

v0 契约首版。影响面：更新/导入时触发。注意与查询期规范化（TERMINATION → HANG）的区别：后者只影响读取结果，见 [[processes/project_phase|项目阶段状态机]]。字段目标：wechat_project_approval_apply.project_phase。

```ground:rule
name: 项目阶段联动
content: 审批通过且首笔落地时间变更为非空时，项目阶段自动置为持续运营(OPERATION)
impact: 更新/导入时触发
field_targets:
  - wechat_project_approval_apply.project_phase
evidence: code_path:ProjectStatisticsApplication.applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
```

---END FILE---

---FILE: rules/solution_manager_change_linkage.md---
---
type: rule
title: 方案经理变更联动
page_key: solution_manager_change_linkage
domain: 项目报表/统计/上报
status: draft
aliases:
  - 方案经理变更联动
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.update
contract_version: "0.1"
---

修改方案经理时，系统同步更新 solution_manager_wxid（企微 userId 列表），并把改动前的方案经理合并进 old_solution_manager。三个字段必须一致变更，否则会出现「有姓名无 userId」导致消息触达失败，或丢失前手责任人的情况。

## 需求背景

需求文档未单列此规则；规则内容来自 update 方法语义，服务于[[concepts/solution_manager|方案经理]]责任人可追溯。

## 版本演进

v0 契约首版。影响面：编辑/导入/批量变更三条入口；批量变更另受[[rules/batch_change_plan_mgr_limit|批量变更方案经理限制]]约束。字段目标：solution_manager、solution_manager_wxid、old_solution_manager。

```ground:rule
name: 方案经理变更联动
content: 修改方案经理时，同步更新solution_manager_wxid，并将原方案经理合并到old_solution_manager
impact: 编辑/导入/批量变更
field_targets:
  - wechat_project_approval_apply.solution_manager
  - wechat_project_approval_apply.solution_manager_wxid
  - wechat_project_approval_apply.old_solution_manager
evidence: code_path:ProjectStatisticsApplication.update
```

---END FILE---

---FILE: rules/import_batch_validation.md---
---
type: rule
title: 导入整批校验
page_key: import_batch_validation
domain: 项目报表/统计/上报
status: draft
aliases:
  - 导入整批校验
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.validateAndApply
contract_version: "0.1"
---

项目台账导入与项目立项统计导入都采用整批事务式校验：只要任意一行校验失败，整批数据都不落库。这保证了导入结果的原子性，代价是用户必须修完所有错误行才能重新提交。

## 需求背景

需求文档未单列此规则；规则内容来自导入校验方法语义。

## 版本演进

v0 契约首版。影响面：导入操作。本规则无字段级目标（field_targets 为空），其约束体现在事务边界而非某个列上；与其他导入期规则（如[[rules/project_phase_linkage|项目阶段联动]]、[[rules/batch_change_plan_mgr_limit|批量变更方案经理限制]]）叠加生效。

```ground:rule
name: 导入整批校验
content: 项目台账导入和项目立项统计导入均整批校验，任一行错误则整批不落库
impact: 导入操作
field_targets: []
evidence: code_path:ProjectStatisticsApplication.validateAndApply
```

---END FILE---

---FILE: rules/departed_contact_tip.md---
---
type: rule
title: 已离职运营人员提示
page_key: departed_contact_tip
domain: 项目报表/统计/上报
status: draft
aliases:
  - 已离职运营人员提示
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectReportController.generateTextForProjectReport
contract_version: "0.1"
---

对 top_flag=1 的项目/企业，系统检查其对接人是否已离职（operation_user.deleted='Y' 且 enable='Y'）；命中时生成提示文本并写入记录（项目台账写 [[tables/tenant_project|tenant_project]].text，企业侧写 wec_project_operation_rel.text）。该提示在列表与详情两处都可读到。

## 需求背景

需求文档未单列此规则；规则内容来自 ProjectReportController 的文本生成方法。

## 版本演进

v0 契约首版。影响面：项目台账列表/详情。提示文本是派生结果，每次读取前刷新；operation_user 表本身不在本主题契约范围内，仅作为判定输入被引用。字段目标：tenant_project.text、wec_project_operation_rel.text。

```ground:rule
name: 已离职运营人员提示
content: top_flag=1的项目/企业，若对接人已离职（operation_user.deleted='Y'且enable='Y'），生成提示文本并更新到text字段
impact: 项目台账列表/详情
field_targets:
  - tenant_project.text
  - wec_project_operation_rel.text
evidence: code_path:ProjectReportController.generateTextForProjectReport
```

---END FILE---

---FILE: rules/batch_change_plan_mgr_limit.md---
---
type: rule
title: 批量变更方案经理限制
page_key: batch_change_plan_mgr_limit
domain: 项目报表/统计/上报
status: draft
aliases:
  - 批量变更方案经理限制
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.validateBatchChangePlanMgrRows
contract_version: "0.1"
---

批量变更方案经理时，新方案经理的姓名必须在企微通讯录中存在，且必须属于 Saas 方案部，否则该行校验不通过。该校验把[[concepts/solution_manager|方案经理]]的部门归属从口头约定变成了硬约束，也解释了为什么方案经理与业务经理不能互换。

## 需求背景

需求文档未单列此规则；规则内容来自批量变更校验方法语义。

## 版本演进

v0 契约首版。影响面：批量变更导入；与[[rules/solution_manager_change_linkage|方案经理变更联动]]的联动写入顺序需保证「先校验、后联动」，否则联动会写入不合规人员。字段目标：wechat_project_approval_apply.solution_manager。

```ground:rule
name: 批量变更方案经理限制
content: 批量变更方案经理时，新方案经理姓名必须在企微通讯录存在且属于Saas方案部
impact: 批量变更导入
field_targets:
  - wechat_project_approval_apply.solution_manager
evidence: code_path:ProjectStatisticsApplication.validateBatchChangePlanMgrRows
```

---END FILE---

---FILE: enums/project_type.md---
---
type: enum
title: 项目类型值点
page_key: project_type
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目类型
  - project_type
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:PROJECT_TYPE_MAIN
  - code_path:ProjectStatisticsApplication.java:PROJECT_TYPE_SUB
contract_version: "0.1"
---

项目类型区分 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]] 中的主项目与子项目，用于父子项目归并展示与统计。字面值存储，无字典表参与。

## 需求背景

需求文档未单列该枚举；值点来自代码常量。

## 版本演进

v0 契约首版，两个值点均为 confirm。

```ground:enum
field: wechat_project_approval_apply.project_type
values:
  - value: MAIN
    label: 主项目
    java_name: PROJECT_TYPE_MAIN
    stored_as: literal
    verdict: confirm
  - value: SUB
    label: 子项目
    java_name: PROJECT_TYPE_SUB
    stored_as: literal
    verdict: confirm
evidence: code_path:ProjectStatisticsApplication.java:PROJECT_TYPE_MAIN
```

---END FILE---

---FILE: enums/ka_white_label.md---
---
type: enum
title: KA是否贴牌值点
page_key: ka_white_label
domain: 项目报表/统计/上报
status: draft
aliases:
  - KA是否贴牌
  - ka_white_label
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:kaWhiteLabelToCode
contract_version: "0.1"
---

KA 是否贴牌，落在 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]].ka_white_label，取 Y/N 字面值，由代码做中文与编码的双向转换。

## 需求背景

需求文档未单列该枚举；值点来自代码转换方法。

## 版本演进

v0 契约首版。无 Java 枚举类承载，java_name 为空，务必以 Y/N 字面值为准。

```ground:enum
field: wechat_project_approval_apply.ka_white_label
values:
  - value: Y
    label: 是
    java_name: null
    stored_as: literal
    verdict: confirm
  - value: N
    label: 否
    java_name: null
    stored_as: literal
    verdict: confirm
evidence: code_path:ProjectStatisticsApplication.java:kaWhiteLabelToCode
```

---END FILE---

---FILE: enums/project_open_status.md---
---
type: enum
title: 项目开通状态值点
page_key: project_open_status
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目开通状态
  - project_open_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
---

[[tables/cust_project_rel|cust_project_rel]].project_open_status 表示关联企业维度上的项目开通状态，DB 中实际分布有 NOT_OPEN 与 OPENED 两个字面值。

## 需求背景

需求文档未单列该枚举；值点来自 DB 分布。

## 版本演进

v0 契约首版，两个值点 verdict=correct，无 Java 枚举类承载。

```ground:enum
field: cust_project_rel.project_open_status
values:
  - value: NOT_OPEN
    label: 未开通
    java_name: null
    stored_as: literal
    verdict: correct
    note: DB分布有NOT_OPEN和OPENED
  - value: OPENED
    label: 已开通
    java_name: null
    stored_as: literal
    verdict: correct
    note: DB分布有NOT_OPEN和OPENED
evidence: db
```

---END FILE---

---FILE: enums/cust_project_rel_status.md---
---
type: enum
title: 关联企业状态值点
page_key: cust_project_rel_status
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_rel.status
  - 关联企业状态
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
---

[[tables/cust_project_rel|cust_project_rel]].status 表示关联关系是否生效，DB 实际分布为 '0'（未生效）与 '1'（已生效），字面值存储。

## 需求背景

需求文档未单列该枚举；值点来自 DB 分布。

## 版本演进

v0 契约首版。注意与同表的 enable 字段（逻辑删除标志，Y有效）职责不同：status 表示业务生效状态，enable 表示记录是否有效，查询时二者常需同时约束。

```ground:enum
field: cust_project_rel.status
values:
  - value: "0"
    label: 未生效
    java_name: null
    stored_as: literal
    verdict: correct
    note: DB分布有'0'和'1'
  - value: "1"
    label: 已生效
    java_name: null
    stored_as: literal
    verdict: correct
    note: DB分布有'1'
evidence: db
```

---END FILE---

---FILE: enums/cust_project_code_record_status.md---
---
type: enum
title: 项目编码记录状态值点
page_key: cust_project_code_record_status
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_code_record.status
  - 编码记录状态
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
---

[[tables/cust_project_code_record|cust_project_code_record]].status 表示该次编码是否正确，DB 实际值为 Y/N。

## 需求背景

需求文档未单列该枚举；值点来自 DB 分布，并以代码枚举作对照审计。

## 版本演进

v0 契约首版。审计结论为 reject：代码 StatusEnum 的 EFFECTIVE/INVALID 与被判为「同值存储」，与 DB 实际的 Y/N 不匹配，存在读写两侧语义漂移风险，详见下方 REVIEW。以写值点与 DB 为准，本页 value 保留 Y/N。

```ground:enum
field: cust_project_code_record.status
values:
  - value: Y
    label: 有效
    java_name: EFFECTIVE
    stored_as: same
    verdict: reject
    note: DB实际值为Y/N，StatusEnum.EFFECTIVE存为EFFECTIVE，不匹配
  - value: N
    label: 无效
    java_name: INVALID
    stored_as: same
    verdict: reject
    note: DB实际值为Y/N
evidence: db
```

---REVIEW: enum | 项目编码记录状态值点---
enum_audit 对 cust_project_code_record.status 的判定为 reject：DB 值域为 Y/N，而 StatusEnum.EFFECTIVE / INVALID 被记录为 stored_as=same（同值存储），两者不一致。需确认是枚举定义已废弃、还是存在写路径将 EFFECTIVE/INVALID 写入该列。在确认前，本页以写值点与 DB 的实际值 Y/N 为准，保留 Y/N 两个 value 键。
---END REVIEW---

---END FILE---