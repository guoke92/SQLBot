---FILE: tables/cust_role_info.md ---
---
type: table
title: cust_role_info（客户角色表）
page_key: table.cust_role_info
domain: 客户角色与端口
status: draft
aliases:
  - 客户角色表
  - 企业角色表
  - 客户企业角色关联表
oid: 1
scope:
  databases:
    - db_dist
sources:
  - db_dist: cust_role_info
  - code_path:CustRoleApplication.java#addRoleInfo
  - code_path:CustRoleApplication.java#operatorCustRoleStatus
  - code_path:CustRoleApplication.java#getCompanyTypeByCompanyCode
  - code_path:CustRoleApplication.java#updateStatusByCustCompany
  - code_path:CustCompanyIfoEnchanceService.java
  - reqdoc:cust-role-port
contract_version: "0.1"
---

# cust_role_info（客户角色表）

cust_role_info 是「某企业在客户（租户）下已经拿到哪些业务角色」的事实表：一个企业可以在这张表里拥有多条角色记录，每条记录由 [[concepts/company-role]] 描述的枚举名刻画。注意 role_type 存的是**枚举名而非 JSON 数组**——写入前由 addRoleInfo 做 `role.replace("\"","")` 去引号，因此正常值形如 CORE／SUPPLIER；DB 中残留的 `'"CORE"'`、`'"SUPPLIER"'` 是历史脏值，读取侧需容忍。ref_cust_company_info 关联企业编码（取值来自 cust_company_info.code），字段注释写作「客户类型」属注释与实现不符，它实际是外键引用而非类型枚举，不要当成枚举使用。

本表与 [[tables/platform_product_cust_role]] 的关系是**实例授权 vs 模板定义**：本表记录企业实际获得的角色，后者配置某产品下允许哪些角色接入（即「端口」）。

## 需求背景

需求文档主张 companyType 企业角色典型值为 CORE / SUPPLIER / DEALER / FINANCE，该主张已由代码使用点与 DB 实测双向证实，构成本表 role_type 的基础取值域（见下方锚点块）。文档未覆盖的部分：企业在同一产品下的多角色组合校验（见页面末 REVIEW）。

## 版本演进

- 写入侧去引号处理（`role.replace("\"","")`）是后置修复，历史数据未回刷，故 DB 中同时存在带引号与不带引号两种形态。
- platform_cust_id 在企业被拒后重新提交流程时由 updateCustRolePlatCustId 清空，说明「平台侧企业 ID」与本地角色记录是弱绑定、可重算的。
- 角色状态不再随业务动作物理删除，统一由 [[processes/cust-role-status]] 的逻辑状态流转承载。

```ground:table
table: cust_role_info
fields:
  - role_type
  - status
  - ref_cust_company_info
  - enable
  - code
  - db_tenant_code
  - platform_cust_id
```

```ground:field
fields:
  - name: role_type
    meaning: |
      企业在客户下的业务角色类型，存储枚举名（非 JSON 数组）；写入前由 addRoleInfo 去除引号 role.replace("\"","")，故正常值为 CORE/SUPPLIER/DEALER/FINANCE/PLATFORM_OPERATOR_COMPANY/PROJECT_COMPANY/CORPORATION_COMPANY/FACTOR_COMPANY/CORE_MANAGER 等。DB 中仍残留 '"CORE"'、'"SUPPLIER"' 带引号的历史脏值。
    evidence: code_path:CustCompanyIfoEnchanceService.java（CustCompanyTypeEnum.CORE/SUPPLIER/DEALER/FINANCE 使用点） + reqdoc:cust-role-port
  - name: status
    meaning: |
      角色关联状态；DB 默认值 ADD，可能值 ADD(新增/待生效)、EFFECT(生效)、FREEZE(冻结)、WRITEOFF(注销)，由 CustRoleStatusConstant 提供的 FREEZE/EFFECT/WRITEOFF 常量驱动。
    evidence: db_dist
  - name: ref_cust_company_info
    meaning: |
      关联的企业编码，取值来自 cust_company_info.code（addRoleInfo 中 relateCompany.getCode()）；字段注释标注为『客户类型』属注释与实现不符，实际是外键引用而非类型枚举。
    evidence: code_path:CustRoleApplication.java#addRoleInfo
  - name: enable
    meaning: |
      逻辑启用标志，有效角色查询口径依赖 enable='Y'。
    evidence: db_dist
  - name: code
    meaning: |
      角色记录业务编码，新增时由 DataModelUtils.uuid() 生成。
    evidence: code_path:CustRoleApplication.java#addRoleInfo
  - name: db_tenant_code
    meaning: |
      数据租户标识，新增时取企业 cust_company_info.db_tenant_code。
    evidence: code_path:CustRoleApplication.java#addRoleInfo
  - name: platform_cust_id
    meaning: |
      关联的运营中台企业ID，企业被拒后重新提交流程时会被清空（updateCustRolePlatCustId）。
    evidence: code_path:CustRoleApplication.java#addRoleInfo
```

## 关联

- [[concepts/company-role]]
- [[tables/platform_product_cust_role]]
- [[calibers/effective-company-role]]
- [[calibers/non-writeoff-role]]
- [[processes/cust-role-status]]
- [[rules/role-overwrite-add]]
- [[rules/role-status-only-update]]

---END FILE---

---FILE: tables/platform_product_cust_role.md ---
---
type: table
title: platform_product_cust_role（产品企业角色/端口表）
page_key: table.platform_product_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - 产品端口表
  - 产品企业角色配置表
  - platform_product_cust_role
oid: 1
scope:
  databases:
    - db_dist
sources:
  - db_dist: platform_product_cust_role
  - code_path:LocalTypeMenuService.java#listTenantProductMenuConfig
  - code_path:LocalTypeRoleController.java#listResourceAuthByProductCode
  - reqdoc:cust-role-port
contract_version: "0.1"
---

# platform_product_cust_role（产品企业角色/端口表）

> (document_claim，未证实)：本文档对产品编码的枚举描述与代码/DB 实测不一致，详见「版本演进」，相关内容不得用作口径。

platform_product_cust_role 是**产品维度的角色模板表**：一行代表「某平台产品（product_code）允许某类企业角色（company_type_code）接入」，业务口语称这一行为一个**端口**（见 [[concepts/port]]）。它是菜单/资源权限配置的维度来源——listTenantProductMenuConfig 正是按 product_code 取出该产品下全部端口，再逐端口配置可见菜单与按钮资源（见 [[rules/menu-port-config]]）。

与 [[tables/cust_role_info]] 的区别：本表是**产品配置模板**（允许谁接入），cust_role_info 是**租户内实例授权**（这家企业实际是什么角色）。

## 需求背景

需求文档用 companyType / productCode 两个维度描述端口配置。companyType 侧已由代码与 DB 证实；productCode 侧文档枚举未获证实（见下）。菜单资源列表还存在按 code 过滤的内置行为（见 [[rules/menu-resource-code-filter]]）。

## 版本演进

- (document_claim，未证实)：文档声称 productCode 典型值为 SCF / AMS / RVSFACTOR。DB 实测 platform_product_cust_role.product_code 为 ACCOUNT_PRODUCT/AMS/BEECREDIT/CROSSBORDER/DEALER/DRAFT/DRAFTQA/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER，未见 SCF；RVSFACTOR 实际以 RVSFACTOR_PC 出现。产品编码应以代码 ProductCodeEnum 与 DB 实测为准。
- 启用标志 enable 的引入使端口支持「下线但保留配置」，取有效端口时必须带 enable='Y'（见 [[calibers/effective-product-port]]）。

```ground:table
table: platform_product_cust_role
fields:
  - company_type_code
  - company_type_name
  - product_code
  - name
  - enable
```

```ground:field
fields:
  - name: company_type_code
    meaning: |
      平台产品下的企业角色编码，业务上也称『端口』；作为菜单/资源权限配置的维度。
    evidence: db_dist
  - name: company_type_name
    meaning: |
      企业角色中文名（供应商/核心企业/金融机构/平台运营方/集团企业/项目公司等）。
    evidence: db_dist
  - name: product_code
    meaning: |
      所属平台产品编码（ACCOUNT_PRODUCT/AMS/DRAFT/ORDER/CROSSBORDER/STORAGE/VOUCHER/ACFLOW/RVSFACTOR_PC 等）。
    evidence: db_dist
  - name: name
    meaning: |
      产品名称（产融平台/国内信用证/应收易融/融易单等），用于展示。
    evidence: db_dist
  - name: enable
    meaning: |
      启用标志 Y/N，配置菜单端口时用于过滤有效端口。
    evidence: db_dist
```

## 关联

- [[concepts/port]]
- [[concepts/company-role]]
- [[tables/cust_role_info]]
- [[calibers/effective-product-port]]
- [[rules/menu-port-config]]
- [[rules/menu-resource-code-filter]]

---END FILE---

---FILE: processes/cust-role-status.md ---
---
type: process
title: 客户角色状态流转
page_key: process.cust-role-status
domain: 客户角色与端口
status: draft
aliases:
  - 客户角色状态机
  - 角色冻结解冻注销
  - cust_role_info.status 状态机
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleInfoController.java#freeze
  - code_path:CustRoleInfoController.java#unFreeze
  - code_path:CustRoleInfoController.java#logout
  - code_path:CustRoleApplication.java#operatorCustRoleStatus
  - code_path:CustCompanyInfoApplication.java#custStatusOperator
  - code_path:CustRoleApplication.java#updateStatusByCustCompany
contract_version: "0.1"
---

# 客户角色状态流转

[[tables/cust_role_info]] 的 status 是一个四态逻辑状态机：ADD（新增/待生效，DB 默认值）→ EFFECT（生效）→ FREEZE（冻结）→ WRITEOFF（注销）。冻结/解冻/注销三个动作都由 CustRoleInfoController 暴露入口，统一收敛到 CustRoleApplication#operatorCustRoleStatus 做单字段更新，不物理删除（见 [[rules/role-status-only-update]]）。

除人工动作外，本状态机还有一条**被动联动路径**：企业状态变更时角色状态跟随企业 cust_status 同值变化，且已是 WRITEOFF 的角色被跳过（见 [[rules/cust-status-role-cascade]]）。因此排查角色状态时，必须同时确认企业侧状态。

## 需求背景

需求文档主张企业状态流转为「已通过→已冻结(违规冻结)→正常(解冻)；不支持物理删除，只支持逻辑删除（冻结/注销）」。该主张与代码实现一致：企业状态变更经 custStatusOperator 联动到角色状态（FREEZE/EFFECT/WRITEOFF），角色无删除动作。

## 版本演进

- 注销（WRITEOFF）作为终态：updateStatusByCustCompany 显式跳过已是 WRITEOFF 的角色，说明注销后不再被企业状态回写「复活」。
- 状态更新由早期可能的整行更新收敛为 `CustRoleInfoDO.builder().id(x).status(y)` 的单字段 updateById，降低并发覆盖风险。

```ground:state_machine
name: 客户角色状态机
field: cust_role_info.status
states:
  - value: ADD
    label: 新增/待生效
    source: db_dist
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
transitions:
  - from: "*"
    event: freeze()
    to: FREEZE
    evidence: code_path:CustRoleInfoController.java#freeze → CustRoleApplication.java#freeze/#operatorCustRoleStatus
  - from: FREEZE
    event: unFreeze()
    to: EFFECT
    evidence: code_path:CustRoleInfoController.java#unFreeze → CustRoleApplication.java#unFreeze/#operatorCustRoleStatus
  - from: ADD|EFFECT|FREEZE
    event: logout()
    to: WRITEOFF
    evidence: code_path:CustRoleInfoController.java#logout → CustRoleApplication.java#logout/#operatorCustRoleStatus
  - from: 非WRITEOFF
    event: 企业状态变更联动(冻结/解冻/注销)
    to: FREEZE|EFFECT|WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java#custStatusOperator → CustRoleApplication.java#updateStatusByCustCompany（跳过已是 WRITEOFF 的角色）
```

## 关联

- [[tables/cust_role_info]]
- [[rules/role-status-only-update]]
- [[rules/cust-status-role-cascade]]
- [[calibers/non-writeoff-role]]
- [[calibers/effective-company-role]]

---END FILE---

---FILE: calibers/effective-company-role.md ---
---
type: caliber
title: 有效企业角色口径
page_key: caliber.effective-company-role
domain: 客户角色与端口
status: draft
aliases:
  - 有效角色口径
  - enable=Y 角色
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleApplication.java#getCompanyTypeByCompanyCode
  - code_path:CustRoleApplication.java#getCompanyTypeByCompanyCodeAndType
  - db_dist: cust_role_info.enable
contract_version: "0.1"
---

# 有效企业角色口径

查询「某企业具备哪些业务角色」时，必须以 enable='Y' 过滤 [[tables/cust_role_info]]。getCompanyTypeByCompanyCode 与 getCompanyTypeByCompanyCodeAndType 都附加了该条件，因此对外的角色判断结果天然不含停用记录。

注意与 [[calibers/non-writeoff-role]] 的区别：enable 是**配置态是否启用**，status 是**生命周期状态**。两个条件作用点不同、不可互相替代——前者用于「读角色」，后者用于「批量改状态时跳过终态」。

## 需求背景

需求文档描述角色鉴权时只讲角色枚举，未提启用标志；实现侧以 enable='Y' 作为有效角色的统一前置条件。

## 版本演进

- enable 列作为逻辑启用标志引入后，删除角色改为「置 enable='N' + 状态流转」的组合，读侧口径固定为 enable='Y'。

```ground:caliber
name: 有效企业角色口径
predicate: cust_role_info.enable = 'Y'
scope: CustRoleApplication#getCompanyTypeByCompanyCode / getCompanyTypeByCompanyCodeAndType 查询该企业角色时附加的过滤条件
evidence: code_path:CustRoleApplication.java#getCompanyTypeByCompanyCode
```

## 关联

- [[tables/cust_role_info]]
- [[calibers/non-writeoff-role]]
- [[concepts/company-role]]

---END FILE---

---FILE: calibers/non-writeoff-role.md ---
---
type: caliber
title: 未注销角色口径
page_key: caliber.non-writeoff-role
domain: 客户角色与端口
status: draft
aliases:
  - 非 WRITEOFF 角色
  - 排除注销角色
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleApplication.java#updateStatusByCustCompany
  - db_dist: cust_role_info.status
contract_version: "0.1"
---

# 未注销角色口径

在企业状态变更联动场景中，可被批量改写状态的角色集合限定为 `status <> 'WRITEOFF'`。updateStatusByCustCompany 把企业下所有非 WRITEOFF 的角色批量置为与企业 cust_status 同值，注销角色被显式跳过。

这一口径使 WRITEOFF 成为**不可逆终态**：企业解冻不会让已注销角色回到 EFFECT。它与 [[calibers/effective-company-role]] 的 enable 过滤属于不同维度，排查「角色为何没被联动」时应先看该角色是否已是 WRITEOFF。

## 需求背景

需求文档强调「不支持物理删除，只支持逻辑删除（冻结/注销）」，该口径即逻辑删除语义的落地：注销即终态，不再参与后续状态回写。

## 版本演进

- 联动逻辑增加 WRITEOFF 跳过判断后，注销与冻结在语义上彻底分离（此前二者都只是状态位）。

```ground:caliber
name: 未注销角色口径
predicate: cust_role_info.status <> 'WRITEOFF'
scope: CustRoleApplication#updateStatusByCustCompany 批量更新企业下角色状态时对 WRITEOFF 角色跳过
evidence: code_path:CustRoleApplication.java#updateStatusByCustCompany
```

## 关联

- [[tables/cust_role_info]]
- [[processes/cust-role-status]]
- [[rules/cust-status-role-cascade]]
- [[calibers/effective-company-role]]

---END FILE---

---FILE: calibers/effective-product-port.md ---
---
type: caliber
title: 有效产品端口口径
page_key: caliber.effective-product-port
domain: 客户角色与端口
status: draft
aliases:
  - 有效端口口径
  - enable=Y 端口
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:LocalTypeMenuService.java#listTenantProductMenuConfig
  - db_dist: platform_product_cust_role.enable
contract_version: "0.1"
---

# 有效产品端口口径

配置菜单权限时，可取端口集合限定为 platform_product_cust_role 中 enable='Y' 的记录。listTenantProductMenuConfig 按 product_code 取该产品全部端口（企业角色）用于菜单配置，停用端口不进入配置面。

该口径决定了「某产品下能看到哪些端口 tab」，与 [[calibers/effective-company-role]] 属于不同表、不同层级：前者是产品配置维度（模板），后者是租户授权维度（实例）。

## 需求背景

需求文档要求菜单按产品与端口维护可配置项；实现侧以 enable='Y' 过滤有效端口，停用端口不展示也不可配。

## 版本演进

- 端口 enable 标志使产品可下线部分端口而保留历史菜单配置；配置保存为覆盖式重建（见 [[rules/menu-port-config]]）。

```ground:caliber
name: 有效产品端口口径
predicate: platform_product_cust_role.enable = 'Y'
scope: LocalTypeMenuService#listTenantProductMenuConfig 按 product_code 取该产品全部端口（企业角色）用于菜单配置
evidence: code_path:LocalTypeMenuService.java#listTenantProductMenuConfig
```

## 关联

- [[tables/platform_product_cust_role]]
- [[concepts/port]]
- [[rules/menu-port-config]]

---END FILE---

---FILE: concepts/port.md ---
---
type: concept
title: 端口
page_key: concept.port
domain: 客户角色与端口
status: draft
aliases:
  - 产品端口
  - 企业角色端口
oid: 1
scope:
  databases:
    - db_dist
sources:
  - db_dist: platform_product_cust_role
  - code_path:LocalTypeMenuService.java#listTenantProductMenuConfig
maps_to: platform_product_cust_role 记录，即 product_code + company_type_code 组合（如 AMS+SUPPLIER、DRAFT+CORE）
also_confused_with:
  - cust_role_info.role_type
  - platform_product_cust_role.company_type_code
adjudication: boundary
boundary: 『端口』是产品配置维度（某产品下允许某企业角色接入），落在 platform_product_cust_role；cust_role_info.role_type 是某具体企业在租户下已获得的角色，二者是模板定义与实例授权的关系。
field_targets:
  - platform_product_cust_role.company_type_code
  - platform_product_cust_role.product_code
contract_version: "0.1"
---

# 端口

「端口」（又称产品端口、企业角色端口）是业务口语，其落点是 [[tables/platform_product_cust_role]] 的一行记录，键为 product_code + company_type_code 组合，例如 AMS+SUPPLIER、DRAFT+CORE。它的语义是**某产品下允许某类企业角色接入**，因此天然是菜单/资源权限的配置粒度——[[calibers/effective-product-port]] 用它来枚举可配端口，[[rules/menu-port-config]] 以它为维度维护菜单配置。

## 需求背景

需求与界面语言统一使用「端口」一词描述产品下的角色配置项；该词在数据模型中没有独立表，需要折算为产品编码与企业角色编码的组合。使用文档时，凡见「端口」应理解为配置维度而非某企业的实际角色。

## 版本演进

- 「端口」一词逐渐从界面文案沉淀为配置模型口径：配置对象由菜单树转向 product_code + company_type_code 组合，保存方式为覆盖式重建。

## 关联

- [[tables/platform_product_cust_role]]
- [[concepts/company-role]]
- [[calibers/effective-product-port]]
- [[rules/menu-port-config]]

---END FILE---

---FILE: concepts/company-role.md ---
---
type: concept
title: 企业角色
page_key: concept.company-role
domain: 客户角色与端口
status: draft
aliases:
  - 客户角色
  - companyType
  - custCompanyType
  - roleType
oid: 1
scope:
  databases:
    - db_dist
sources:
  - db_dist: cust_role_info.role_type
  - code_path:CustCompanyIfoEnchanceService.java
  - code_path:CustRoleApplication.java#addRoleInfo
maps_to: 企业业务角色枚举 CORE/SUPPLIER/DEALER/FINANCE/PLATFORM_OPERATOR_COMPANY/PROJECT_COMPANY/CORPORATION_COMPANY/FACTOR_COMPANY/CORE_MANAGER 等
also_confused_with:
  - sys_role(系统权限角色，如 accountNormal/accountGuest)
  - userType(admin/operator/guest，用户在企业内的身份)
adjudication: boundary
boundary: 企业角色=企业身份维度；用户类型=企业内用户身份维度；sys_role=权限维度角色，三者不可混用。
field_targets:
  - cust_role_info.role_type
contract_version: "0.1"
---

# 企业角色

「企业角色」（文档与代码中亦称客户角色、companyType、custCompanyType、roleType）描述**企业在业务网络中的身份**，取值是 CORE / SUPPLIER / DEALER / FINANCE / PLATFORM_OPERATOR_COMPANY / PROJECT_COMPANY / CORPORATION_COMPANY / FACTOR_COMPANY / CORE_MANAGER 一类的枚举名，落地在 [[tables/cust_role_info]] 的 role_type。与之相对，[[tables/platform_product_cust_role]] 的 company_type_code 是同一套枚举在**产品配置维度**上的表达（即 [[concepts/port]]）。

三个「角色」概念必须在文档中严格区分：企业角色（企业身份）、userType（用户在企业内的身份：admin/operator/guest）、sys_role（权限角色，如 accountNormal/accountGuest）。三者分属不同维度，不可混用。

## 需求背景

需求文档使用 companyType 表述企业角色，并把它与菜单端口、角色组合校验绑定。企业角色的枚举取值已有代码与 DB 双向证实；而「同一产品下多角色组合合法性校验」在文档中被要求，代码侧暂未找到实现（见 REVIEW）。

## 版本演进

- role_type 的写入形态经历过一次去引号修正，历史数据仍含带引号值，读取侧需做归一化。
- 企业角色与产品端口的解耦：角色枚举同时服务于「企业身份判定」与「产品接入配置」两个场景，二者不再共用同一张表。

## 关联

- [[tables/cust_role_info]]
- [[tables/platform_product_cust_role]]
- [[concepts/port]]
- [[concepts/role-class]]
- [[processes/cust-role-status]]

---END FILE---

---FILE: concepts/role-class.md ---
---
type: concept
title: roleClass
page_key: concept.role-class
domain: 客户角色与端口
status: draft
aliases:
  - SysRoleDO.roleClass
  - 权限角色归属标识
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:RoleFacade#generateRoleClass
  - code_path:ClientCustRoleSyncService
also_confused_with:
  - cust_role_info.role_type
adjudication: boundary
boundary: roleClass 是权限角色的归属标识（企业类型+企业ID），ClientCustRoleSyncService 按最后一个下划线拆分出 companyType 与 companyId 后再同步；不等同于 cust_role_info 角色记录。
contract_version: "0.1"
---

# roleClass

roleClass 是权限侧（SysRoleDO）的**归属标识**，格式为 `{custType}_{custId}`，由 RoleFacade#generateRoleClass 拼接。ClientCustRoleSyncService 拿到 roleClass 后，按**最后一个下划线**拆分出 companyType 与 companyId，再据此做角色同步。

它与 [[concepts/company-role]] 的 role_type 长得像但不是一回事：roleClass 是字符串拼装的定位键（谁的角色），role_type 是枚举身份（是什么角色）。因为拆分规则依赖「最后一个下划线」，当 custType 本身含下划线时解析会退化为把前面全部当作 custType，这是使用该字段时最需要留意的隐式约束。

## 需求背景

需求文档在讲「企业角色同步」时混用了 roleClass 与 companyType 两个词；实现侧以 roleClass 作为同步入口参数，再反解出 companyType/companyId。

## 版本演进

- 由「按固定分隔解析」演进为「按最后一个下划线解析」，以兼容 custType 中出现的下划线。

## 关联

- [[concepts/company-role]]
- [[tables/cust_role_info]]

---END FILE---

---FILE: rules/role-status-only-update.md ---
---
type: rule
title: 角色操作仅更新状态字段
page_key: rule.role-status-only-update
domain: 客户角色与端口
status: draft
aliases:
  - 角色冻结解冻注销只改状态
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleApplication.java#operatorCustRoleStatus
  - code_path:CustRoleInfoController.java#freeze
  - code_path:CustRoleInfoController.java#unFreeze
  - code_path:CustRoleInfoController.java#logout
contract_version: "0.1"
---

# 角色操作仅更新状态字段

冻结、解冻、注销三个动作的实现路径一致：先按 id 回查角色，再用 `CustRoleInfoDO.builder().id(x).status(y)` 走 updateById 做**单字段更新**，不做物理删除，也不顺手改写其他字段。这保证了角色记录始终可追溯。

对使用者的影响：任何「删除角色」的需求都应翻译为「置 [[processes/cust-role-status]] 中的某个状态位」，而不是 DELETE；同时因为只更新 status，其它列的陈旧值不会被自动纠正。

## 需求背景

需求文档要求企业角色「不支持物理删除，只支持逻辑删除」，本规则是其实现侧约束。

## 版本演进

- 从可能的整行更新收敛为单字段 updateById，减少并发下的字段覆盖。

```ground:rule
name: 角色操作仅更新状态字段
content: 冻结/解冻/注销均先按 id 回查角色，再用 CustRoleInfoDO.builder().id(x).status(y) 走 updateById 单字段更新，不做物理删除。
impact: 角色只有逻辑状态变化，无覆盖/删除动作
field_targets:
  - cust_role_info.status
evidence: code_path:CustRoleApplication.java#operatorCustRoleStatus
```

## 关联

- [[processes/cust-role-status]]
- [[tables/cust_role_info]]
- [[rules/cust-status-role-cascade]]

---END FILE---

---FILE: rules/cust-status-role-cascade.md ---
---
type: rule
title: 企业状态变更联动角色状态
page_key: rule.cust-status-role-cascade
domain: 客户角色与端口
status: draft
aliases:
  - 企业冻结解冻注销联动角色
  - updateStatusByCustCompany
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustCompanyInfoApplication.java#custStatusOperator
  - code_path:CustRoleApplication.java#updateStatusByCustCompany
  - reqdoc:cust-role-port
contract_version: "0.1"
---

# 企业状态变更联动角色状态

企业冻结/解冻/注销时，custStatusOperator 调用 updateStatusByCustCompany，把该企业下所有非 WRITEOFF 角色 status **批量置为与企业 cust_status 同值**（FREEZE/EFFECT/WRITEOFF）。因此角色状态不是独立演化的，它被企业状态驱动。

排查要点：角色状态与预期不符时，先看企业侧状态是否为最近一次改写的来源；注销企业会连带把角色置为 WRITEOFF，且因 [[calibers/non-writeoff-role]] 的跳过逻辑不可回退。角色自身的冻结不以企业状态变更来源为准，二者会互相覆盖，以最后一次写入为准。

## 需求背景

需求文档主张企业状态流转为「已通过→已冻结(违规冻结)→正常(解冻)；不支持物理删除，只支持逻辑删除（冻结/注销）」。该主张已由代码证实——企业状态变更正是通过本规则联动到角色状态（FREEZE/EFFECT/WRITEOFF）。

## 版本演进

- 联动范围从「生效/冻结」扩展到注销（WRITEOFF），并增加对已是 WRITEOFF 角色的跳过判断。

```ground:rule
name: 企业状态变更联动角色状态
content: 企业冻结/解冻/注销时，custStatusOperator 调用 updateStatusByCustCompany，把该企业下所有非 WRITEOFF 角色 status 批量置为与企业 cust_status 同值（FREEZE/EFFECT/WRITEOFF）。
impact: 角色状态与企业状态保持一致，注销企业会连带把角色置为 WRITEOFF
field_targets:
  - cust_role_info.status
  - cust_company_info.cust_status
evidence: code_path:CustCompanyInfoApplication.java#custStatusOperator + CustRoleApplication.java#updateStatusByCustCompany + reqdoc:cust-role-port
```

## 关联

- [[processes/cust-role-status]]
- [[calibers/non-writeoff-role]]
- [[rules/role-status-only-update]]
- [[tables/cust_role_info]]

---END FILE---

---FILE: rules/role-overwrite-add.md ---
---
type: rule
title: 角色为覆盖式新增
page_key: rule.role-overwrite-add
domain: 客户角色与端口
status: draft
aliases:
  - addRoleInfo 覆盖式重建
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleApplication.java#addRoleInfo
contract_version: "0.1"
---

# 角色为覆盖式新增

addRoleInfo 是**覆盖式**的：先按 ref_cust_company_info 删除该企业已有角色，再按传入 roleType 的 JSON 数组逐项 saveBatch 重建。新记录 code 由 uuid 生成，db_tenant_code 取企业租户。

影响：同一企业重复调用会整体重建角色集合，不做增量合并；任何依赖「原有角色记录 id/编码稳定」的逻辑都会失效。重建还会重置 status（回到 DB 默认 ADD 的新增态语义），因此调用前需确认是否会打断正在生效的角色。

## 需求背景

需求文档以「提交企业角色信息」描述该动作，未强调其覆盖语义；实现侧是「先删后建」，与增量 upsert 的直觉不同，需在对接文档中显式说明。

## 版本演进

- 由可能的逐条增量维护收敛为先删后批量重建，简化了角色集合的一致性维护。

```ground:rule
name: 角色为覆盖式新增
content: addRoleInfo 先按 ref_cust_company_info 删除该企业已有角色，再按传入 roleType 的 JSON 数组逐项 saveBatch 重建；新记录 code 由 uuid 生成，db_tenant_code 取企业租户。
impact: 同一企业重复调用会整体重建角色集合，不做增量合并
field_targets:
  - cust_role_info.role_type
  - cust_role_info.code
  - cust_role_info.db_tenant_code
evidence: code_path:CustRoleApplication.java#addRoleInfo
```

## 关联

- [[tables/cust_role_info]]
- [[concepts/company-role]]
- [[rules/rejected-cust-clear-role]]

---END FILE---

---FILE: rules/rejected-cust-clear-role.md ---
---
type: rule
title: 拒绝态企业清角色关联
page_key: rule.rejected-cust-clear-role
domain: 客户角色与端口
status: draft
aliases:
  - BUILD_FAIL 清用户角色绑定
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleApplication.java#addRoleInfo
contract_version: "0.1"
---

# 拒绝态企业清角色关联

当企业 cust_build_status=BUILD_FAIL（拒绝）时，addRoleInfo 会调用 userInfoFacade.delCustUserRole 清掉该企业的用户-角色绑定。也就是说：被拒企业重新提交角色信息时，历史授权会被主动清理，而不是被继承。

这条规则与 [[rules/role-overwrite-add]] 配合，构成「重建」的完整语义：角色集合先删后建，用户-角色绑定在拒绝态下再额外清空。排查「重新提交后用户权限丢失」时，应先确认企业是否处于 BUILD_FAIL。

## 需求背景

需求文档要求「被拒企业重新提交需重新授权」，本规则是其实现侧的清关联动作。

## 版本演进

- 在 BUILD_FAIL 分支增加 delCustUserRole 调用，避免被拒企业的陈旧用户-角色绑定被沿用。

```ground:rule
name: 拒绝态企业清角色关联
content: 当企业 cust_build_status=BUILD_FAIL（拒绝）时，addRoleInfo 会调用 userInfoFacade.delCustUserRole 清掉该企业的用户-角色绑定。
impact: 被拒企业重新提交时会清理历史角色授权
field_targets:
  - cust_role_info.role_type
evidence: code_path:CustRoleApplication.java#addRoleInfo（CustBuildStatusEnum.BUILD_FAIL 分支）
```

## 关联

- [[rules/role-overwrite-add]]
- [[tables/cust_role_info]]
- [[processes/cust-role-status]]

---END FILE---

---FILE: rules/menu-port-config.md ---
---
type: rule
title: 菜单端口配置按企业角色维护
page_key: rule.menu-port-config
domain: 客户角色与端口
status: draft
aliases:
  - listTenantProductMenuConfig 端口配置
  - saveTenantProductMenuConfig
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:LocalTypeMenuService.java#listTenantProductMenuConfig
  - code_path:LocalTypeMenuService.java#saveTenantProductMenuConfig
contract_version: "0.1"
---

# 菜单端口配置按企业角色维护

listTenantProductMenuConfig 以 [[tables/platform_product_cust_role]] 的 company_type_code（即 [[concepts/port]]）为维度，为每个端口列出可配置菜单（listProductCustMenu）与按钮资源（listProductCustMenuResource）；保存时先删除该租户该产品下已配菜单与资源，再批量重建。配置是**覆盖式**的。

影响：端口是菜单权限配置的粒度——同产品不同端口可以有完全不同的菜单集；保存动作不是增量合并，部分保存会导致未提交的配置被删除。取端口集合时须遵守 [[calibers/effective-product-port]]。

## 需求背景

需求文档要求「按产品与端口为租户配置可见菜单与按钮资源」，本规则是该诉求的实现口径，并明确了配置粒度为 company_type_code。

## 版本演进

- 保存由增量维护改为先删后建，简化冲突处理，代价是必须整表单提交。
- 端口列表读取增加 enable 过滤，使停用端口不再进入可配面。

```ground:rule
name: 菜单端口配置按企业角色维护
content: listTenantProductMenuConfig 以 platform_product_cust_role 的 company_type_code 为维度，为每个端口列出可配置菜单(listProductCustMenu)与按钮资源(listProductCustMenuResource)，保存时先删除该租户该产品下已配菜单与资源再批量重建。
impact: 『端口』是菜单权限配置的粒度，配置为覆盖式
field_targets:
  - platform_product_cust_role.company_type_code
  - platform_product_cust_role.product_code
evidence: code_path:LocalTypeMenuService.java#listTenantProductMenuConfig/#saveTenantProductMenuConfig
```

## 关联

- [[concepts/port]]
- [[tables/platform_product_cust_role]]
- [[calibers/effective-product-port]]
- [[rules/menu-resource-code-filter]]

---END FILE---

---FILE: rules/menu-resource-code-filter.md ---
---
type: rule
title: 菜单资源列表自动过滤指定 code
page_key: rule.menu-resource-code-filter
domain: 客户角色与端口
status: draft
aliases:
  - filterMenuByCode
  - 菜单 code 过滤
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:LocalTypeRoleController.java#listResourceAuthByProductCode
  - reqdoc:cust-role-port
contract_version: "0.1"
---

# 菜单资源列表自动过滤指定 code

配置端口菜单资源时，列表会对若干内置菜单 code 做自动剔除，使它们不出现在可配置列表中。文档只描述了其中一个 code，代码中实际剔除三个。

使用要点：这些 code 属**内置保留项**，不要试图通过菜单配置为其开权限，也不要期望在列表中看到它们；需求文档与实现存在数量差异，以代码为准。

## 需求背景

需求文档主张「菜单 code='0891344a3a4442179e98819cbe926ced' 的记录在列表中自动过滤」，该主张已由代码证实，但代码实际剔除三个 code（见锚点块），文档列举不全。

## 版本演进

- 过滤清单由 1 个扩展到 3 个 code，文档未同步更新，形成文档与实现的枚举落差。

```ground:rule
name: 菜单资源列表自动过滤指定 code
content: 菜单 code='0891344a3a4442179e98819cbe926ced' 的记录在列表中自动过滤
impact: 被过滤的内置菜单不进入可配置资源列表，不应为其配置端口权限
evidence: code_path:LocalTypeRoleController.java#listResourceAuthByProductCode（filterMenuByCode 实际剔除 3 个 code: 0891344a3a4442179e98819cbe926ced、81b9d705e8a14d6088bcf341884e70d8、16bcb2ed1daf4b739a5aad6e791aefa4，文档仅列出 1 个） + reqdoc:cust-role-port
```

## 关联

- [[rules/menu-port-config]]
- [[tables/platform_product_cust_role]]
- [[concepts/port]]

---END FILE---

---REVIEW: process | 客户角色组合校验---
诉求（document_claim）：客户加入产品项目时进行企业角色组合校验——企业在同一产品下存在 2+ 角色时读取 PlatformProductDO.custRoleCombine 合法组合，非法组合抛 BaseException『系统暂不支持该角色组合』。

状态：code_status = uncovered。未在给定代码片段中找到 TenantProductApplication#checkProjectProductByCustType / checkCustRoleCombine 的实现体，故本主题下不产出对应 process/rule 页。

待确认：
1) 校验落点究竟在租户产品应用、平台产品配置还是前端；
2) custRoleCombine 的存储形态（分隔串/JSON）与合法组合的判定单元（是否以 [[concepts/port]] 的 product_code + company_type_code 组合为键）；
3) 校验失败信息文案是否与文档一致。
确认后可升格为 rule 页并补 ground:rule 锚点。
---END REVIEW---

---REVIEW: concept | 用户角色与权限并集---
诉求（document_claim）：用户角色规则为平台管理员/企业管理员/普通用户，一个用户可拥有多个角色，角色权限取并集。

状态：code_status = uncovered。给定代码中 UserInfoFacade 使用 sys 侧固定角色 accountGuest/accountNormal，未见『一用户多角色并集』的并集计算实现。

待确认：
1) 多角色并集是在权限服务侧计算还是在下游各自判断；
2) accountGuest/accountNormal 与文档三类用户（平台管理员/企业管理员/普通用户）的映射关系；
3) 该规则与 [[concepts/company-role]]（企业身份）是否在同一鉴权链路中参与判定。
在确证前不得据此页产出 concept 页面锚点（concept 无锚点块，仅登记待确认语义）。
---END REVIEW---