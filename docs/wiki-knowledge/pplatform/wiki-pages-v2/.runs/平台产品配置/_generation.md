---FILE: tables/platform_product.md ---
---
type: table
title: platform_product 平台产品表
page_key: tables/platform_product
domain: 平台产品配置
status: draft
aliases: [平台产品表, 平台产品配置表, platform_product]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:platform_product
contract_version: "0.1"
---

platform_product 是平台产品配置域的核心主表，承载平台侧「可被开通、可使用」的产品定义。它向上承接平台运营方的产品目录维护，向下被租户产品（[[tables/tenant_product]]）与客户产品（[[tables/cust_auth_application]]）引用为开通依据。产品的类型（通用/互通）、是否平台、是否多企业角色、是否多项目等布尔与枚举标识，共同决定了后续开通流程、进入产品校验以及角色组合校验的分支走向。

字段值域上，`product_type` 区分通用产品与互通产品，是 [[calibers/general-product-scope]] 口径成立的唯一依据；`cust_role_combine` 是 [[rules/cust-role-combine-check]] 的配置来源；`db_tenant_code` 与 `app_tenant_code` 构成数据隔离与逻辑隔离的两层租户语义，参见 [[concepts/tenantCode]]。产品前端接入形态由 [[tables/platform_product_client]] 描述。

## 需求背景

当前语义分析未提供该表的 reqdoc 主张（reqdoc_claims 为空），故本页需求背景不做需求文档层面的断言，仅依据库表结构与代码语义整理产品定义字段的含义与上下游关系。

## 版本演进

v0 契约首次建档，19 个字段的语义均来自库表结构证据，尚无业务主张需要标注为未证实。

```ground:table
table: platform_product
fields:
  - name: product_code
    meaning: "平台产品编码，唯一标识一个平台产品"
    evidence: db
  - name: name
    meaning: "平台产品名称"
    evidence: db
  - name: product_type
    meaning: "产品类型，GENERAL=通用产品，INTERWORKING=互通产品"
    evidence: db
  - name: platform_code
    meaning: "平台编码"
    evidence: db
  - name: platform_flag
    meaning: "是否平台标识，Y/N"
    evidence: db
  - name: multiple_cust_role_flag
    meaning: "是否有多企业角色，Y/N"
    evidence: db
  - name: multiple_project_flag
    meaning: "是否有多项目，Y/N"
    evidence: db
  - name: cust_role_combine
    meaning: "支持的企业角色组合，文本格式解析为 Set<Set<String>>"
    evidence: code
  - name: product_status
    meaning: "产品状态，DB 值 '1' 表示生效"
    evidence: db
  - name: enable
    meaning: "启用标识，Y/N"
    evidence: db
  - name: general_flag
    meaning: "通用产品标识，Y/N"
    evidence: db
  - name: product_construction_status
    meaning: "产品建设情况，Y/N"
    evidence: db
  - name: default_menu_code
    meaning: "默认菜单编号"
    evidence: db
  - name: logo_icon_url
    meaning: "产品 logo 地址"
    evidence: db
  - name: transaction_structure
    meaning: "交易结构 JSON 字符串"
    evidence: db
  - name: project_config
    meaning: "项目配置 JSON 字符串"
    evidence: db
  - name: wkfl_flag
    meaning: "产品工作流启用开关，Y/N"
    evidence: db
  - name: db_tenant_code
    meaning: "数据租户标识"
    evidence: db
  - name: app_tenant_code
    meaning: "逻辑租户标识"
    evidence: db
```

## 关联

- 主键语义：[[concepts/productCode]]
- 角色组合配置：[[concepts/custRoleCombine]]
- 数据/逻辑租户：[[concepts/tenantCode]]
- 前端接入：[[tables/platform_product_client]]
- 租户侧开通：[[tables/tenant_product]]、[[processes/tenant-product-open-status]]
- 客户侧开通：[[tables/cust_auth_application]]、[[processes/cust-product-open-status]]
- 相关口径与规则：[[calibers/general-product-scope]]、[[rules/platform-product-save-check]]、[[rules/platform-product-list-filter]]

---END FILE---

---FILE: tables/platform_product_client.md ---
---
type: table
title: platform_product_client 平台产品客户端配置表
page_key: tables/platform_product_client
domain: 平台产品配置
status: draft
aliases: [平台产品客户端表, platform_product_client]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:platform_product_client
contract_version: "0.1"
---

platform_product_client 描述平台产品在不同客户端上的接入配置。一个产品可以对应多种客户端类型与多种链接方式，链接类型（iframe/redirect/forward）决定产品入口的跳转方式，`ext_config` 承载各客户端差异化的扩展配置，`multiple_type` 用于按类型做过滤。

本表与 [[tables/platform_product]] 是配置与接入的关系：产品定义决定「能不能用」，客户端配置决定「从哪儿、以什么方式进入」。

## 需求背景

语义分析未提供本表的 reqdoc 主张，需求背景暂不展开需求文档层面的叙述，仅按库表结构整理字段含义。

## 版本演进

v0 契约首次建档，4 个字段语义均来自库表结构证据。

```ground:table
table: platform_product_client
fields:
  - name: client_type
    meaning: "客户端类型"
    evidence: db
  - name: link_type
    meaning: "链接类型(iframe/redirect/forward)"
    evidence: db
  - name: multiple_type
    meaning: "过滤类型"
    evidence: db
  - name: ext_config
    meaning: "扩展配置信息"
    evidence: db
```

## 关联

- 产品主表：[[tables/platform_product]]
- 产品编码语义：[[concepts/productCode]]
- 产品列表过滤：[[rules/platform-product-list-filter]]

---END FILE---

---FILE: tables/tenant_product.md ---
---
type: table
title: tenant_product 租户产品表
page_key: tables/tenant_product
domain: 平台产品配置
status: draft
aliases: [租户产品表, tenant_product]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:tenant_product.open_status
  - code:tenant_product.platform_product_code
  - code:tenant_product.tenant_id
contract_version: "0.1"
---

tenant_product 记录某一租户与某一平台产品之间的开通关系，是租户维度「已开通/开通中/未开通」状态的载体。它以 `platform_product_code` 指向 [[tables/platform_product]]，以 `tenant_id` 标识归属租户，并以 `open_status` 承载 [[processes/tenant-product-open-status]] 状态机的全部状态。

该表是 [[calibers/tenant-open-product]] 口径的直接来源：查询租户已开通产品时，过滤条件即为 `open_status = 'Y'`。

## 需求背景

语义分析未提供本表的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档。本表字段语义来自代码证据，其中 `open_status` 的取值与迁移由状态机页面承载。

```ground:table
table: tenant_product
fields:
  - name: open_status
    meaning: "租户产品开通状态，Y=已开通/P=开通中/N=未开通或取消"
    evidence: code
  - name: platform_product_code
    meaning: "平台产品编码"
    evidence: code
  - name: tenant_id
    meaning: "租户ID"
    evidence: code
```

## 关联

- 产品主表：[[tables/platform_product]]
- 状态机：[[processes/tenant-product-open-status]]
- 状态术语辨析：[[concepts/openStatus]]
- 口径：[[calibers/tenant-open-product]]、[[calibers/platform-product-whitelist]]
- 规则：[[rules/tenant-product-on-the-way-check]]

---END FILE---

---FILE: tables/cust_auth_application.md ---
---
type: table
title: cust_auth_application 客户产品开通申请表
page_key: tables/cust_auth_application
domain: 平台产品配置
status: draft
aliases: [客户产品开通表, cust_auth_application]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:cust_auth_application.open_status
  - code:cust_auth_application.platform_product_code
  - code:cust_auth_application.ref_cust_company_info
  - code:cust_auth_application.ref_cust_auth_application_tenant_product
contract_version: "0.1"
---

cust_auth_application 承载客户（企业）维度的产品开通申请与开通结果。它通过 `platform_product_code` 关联平台产品，通过 `ref_cust_company_info` 关联企业（[[tables/cust_company_info]]），并通过 `ref_cust_auth_application_tenant_product` 关联到租户产品记录（[[tables/tenant_product]]），从而把「租户开通」与「客户开通」两层关系串联起来。

`open_status` 驱动 [[processes/cust-product-open-status]] 状态机，也是 [[calibers/cust-open-product]] 口径的判定字段。

## 需求背景

语义分析未提供本表的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档。字段语义来自代码证据，状态取值与迁移见状态机页面。

```ground:table
table: cust_auth_application
fields:
  - name: open_status
    meaning: "客户产品开通状态，OPENED=已开通/OPENING=开通中/NOT_OPENED=未开通"
    evidence: code
  - name: platform_product_code
    meaning: "平台产品编码"
    evidence: code
  - name: ref_cust_company_info
    meaning: "客户企业编码"
    evidence: code
  - name: ref_cust_auth_application_tenant_product
    meaning: "关联的租户产品编码"
    evidence: code
```

## 关联

- 状态机：[[processes/cust-product-open-status]]
- 状态术语辨析：[[concepts/openStatus]]
- 口径：[[calibers/cust-open-product]]
- 规则：[[rules/product-agreement-activate]]
- 企业表：[[tables/cust_company_info]]、[[tables/tenant_product]]

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info 客户企业信息表
page_key: tables/cust_company_info
domain: 平台产品配置
status: draft
aliases: [客户企业信息表, cust_company_info]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:cust_company_info.cust_company_type
  - code:cust_company_info.db_tenant_code
  - code:cust_company_info.need_register_ca
contract_version: "0.1"
---

cust_company_info 记录客户企业的基础信息与角色属性。`cust_company_type` 是企业角色类型（如 CORE/SUPPLIER/DEALER/FINANCE 等），它既是 [[concepts/companyType]] 的落点，也是 [[rules/cust-role-combine-check]] 与 [[rules/goto-product-company-type-check]] 的校验对象；`db_tenant_code` 承担数据租户隔离；`need_register_ca` 标识该企业是否需要开通电子签章，与产品协议签署后的激活流程（[[rules/product-agreement-activate]]）相关。

## 需求背景

语义分析未提供本表的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，字段语义来自代码证据。

```ground:table
table: cust_company_info
fields:
  - name: cust_company_type
    meaning: "企业角色类型，如 CORE/SUPPLIER/DEALER/FINANCE 等"
    evidence: code
  - name: db_tenant_code
    meaning: "数据租户标识"
    evidence: code
  - name: need_register_ca
    meaning: "是否需要开通电子签章，Y/N"
    evidence: code
```

## 关联

- 角色术语：[[concepts/companyType]]
- 租户术语：[[concepts/tenantCode]]
- 规则：[[rules/goto-product-company-type-check]]、[[rules/cust-role-combine-check]]、[[rules/product-agreement-activate]]
- 人员与企业项目：[[tables/cust_person_info]]、[[tables/cust_project_rel]]

---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info 客户人员信息表
page_key: tables/cust_person_info
domain: 平台产品配置
status: draft
aliases: [客户人员信息表, cust_person_info]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:cust_person_info.user_type
  - code:cust_person_info.company_type
contract_version: "0.1"
---

cust_person_info 记录客户企业下的用户信息。`user_type` 区分管理员（admin）与经办人（operator），`company_type` 标注该用户所属的企业角色类型，与 [[tables/cust_company_info]] 的 `cust_company_type`、[[tables/cust_project_rel]] 的 `company_type` 使用同一套角色语义（[[concepts/companyType]]）。

## 需求背景

语义分析未提供本表的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，字段语义来自代码证据。

```ground:table
table: cust_person_info
fields:
  - name: user_type
    meaning: "用户类型，admin=管理员/operator=经办人"
    evidence: code
  - name: company_type
    meaning: "企业角色类型"
    evidence: code
```

## 关联

- 角色术语：[[concepts/companyType]]
- 企业表：[[tables/cust_company_info]]
- 企业项目关系：[[tables/cust_project_rel]]

---END FILE---

---FILE: tables/cust_project_rel.md ---
---
type: table
title: cust_project_rel 企业项目关系表
page_key: tables/cust_project_rel
domain: 平台产品配置
status: draft
aliases: [企业项目关系表, cust_project_rel]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:cust_project_rel.company_type
  - code:cust_project_rel.product_id
  - code:cust_project_rel.project_id
contract_version: "0.1"
---

cust_project_rel 描述企业、产品与项目之间的关联关系。`company_type` 标注企业在关系中的角色（[[concepts/companyType]]），`product_id` 指向产品，`project_id` 指向项目。

该表是 [[rules/cust-role-combine-check]] 的角色来源之一（同一企业在同一产品下可能拥有多个角色），也是 [[rules/goto-product-project-status-check]] 中「检查企业关联项目是否生效」的关联依据。

## 需求背景

语义分析未提供本表的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，字段语义来自代码证据。

```ground:table
table: cust_project_rel
fields:
  - name: company_type
    meaning: "企业角色类型"
    evidence: code
  - name: product_id
    meaning: "产品ID"
    evidence: code
  - name: project_id
    meaning: "项目ID"
    evidence: code
```

## 关联

- 角色术语：[[concepts/companyType]]
- 规则：[[rules/cust-role-combine-check]]、[[rules/goto-product-project-status-check]]
- 产品与人员：[[tables/platform_product]]、[[tables/cust_person_info]]

---END FILE---

---FILE: processes/tenant-product-open-status.md ---
---
type: process
title: 租户产品开通状态
page_key: processes/tenant-product-open-status
domain: 平台产品配置
status: draft
aliases: [租户产品开通状态机, tenant_product.open_status]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:TenantProductApplication.activeAndNotify
  - code:TenantProductApplication.cancel
contract_version: "0.1"
---

租户产品开通状态描述 [[tables/tenant_product]] 中 `open_status` 的生命周期，取值为 Y/P/N 三态。租户产品从「开通中」经激活动作进入「已开通」，已开通产品可被取消回到「未开通/取消」。该状态是租户侧产品可见性的判定基础，也是 [[calibers/tenant-open-product]] 口径的过滤字段。

激活前存在在途校验约束，见 [[rules/tenant-product-on-the-way-check]]；与客户侧状态枚举的差异辨析见 [[concepts/openStatus]]。

## 需求背景

语义分析未提供该状态机的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档。两个迁移动作 `activeAndNotify`、`cancel` 均来自代码证据。

```ground:state_machine
name: 租户产品开通状态
field: tenant_product.open_status
states:
  - value: "Y"
    label: "已开通"
    source: code_enum
  - value: "P"
    label: "开通中"
    source: code_enum
  - value: "N"
    label: "未开通/取消"
    source: code_enum
transitions:
  - from: "P"
    event: activeAndNotify
    to: "Y"
    evidence: TenantProductApplication.activeAndNotify
  - from: "Y"
    event: cancel
    to: "N"
    evidence: TenantProductApplication.cancel
```

## 关联

- 承载表：[[tables/tenant_product]]
- 客户侧对应状态机：[[processes/cust-product-open-status]]
- 口径：[[calibers/tenant-open-product]]
- 规则：[[rules/tenant-product-on-the-way-check]]
- 术语：[[concepts/openStatus]]

---END FILE---

---FILE: processes/cust-product-open-status.md ---
---
type: process
title: 客户产品开通状态
page_key: processes/cust-product-open-status
domain: 平台产品配置
status: draft
aliases: [客户产品开通状态机, cust_auth_application.open_status]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustProductDomainService.initProduct
  - code:CustProductDomainService.doActiveProduct
contract_version: "0.1"
---

客户产品开通状态描述 [[tables/cust_auth_application]] 中 `open_status` 的生命周期，取值为 OPENED/OPENING/NOT_OPENED 三态。初始化产品开通将状态置为「开通中」，激活动作既可从「开通中」进入「已开通」，也可从「未开通」直接进入「已开通」；「已开通」是 [[calibers/cust-open-product]] 口径的过滤条件。

激活动作与产品协议签署流程耦合，见 [[rules/product-agreement-activate]]。注意与租户侧三态枚举不可混用，辨析见 [[concepts/openStatus]]。

## 需求背景

语义分析未提供该状态机的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档。三条迁移均来自代码证据，其中 `activeProduct` 存在两条入边。

```ground:state_machine
name: 客户产品开通状态
field: cust_auth_application.open_status
states:
  - value: "OPENED"
    label: "已开通"
    source: code_enum
  - value: "OPENING"
    label: "开通中"
    source: code_enum
  - value: "NOT_OPENED"
    label: "未开通"
    source: code_enum
transitions:
  - from: "NOT_OPENED"
    event: initProduct
    to: "OPENING"
    evidence: CustProductDomainService.initProduct
  - from: "OPENING"
    event: activeProduct
    to: "OPENED"
    evidence: CustProductDomainService.doActiveProduct
  - from: "NOT_OPENED"
    event: activeProduct
    to: "OPENED"
    evidence: CustProductDomainService.doActiveProduct
```

## 关联

- 承载表：[[tables/cust_auth_application]]
- 租户侧对应状态机：[[processes/tenant-product-open-status]]
- 口径：[[calibers/cust-open-product]]
- 规则：[[rules/product-agreement-activate]]
- 术语：[[concepts/openStatus]]

---END FILE---

---FILE: calibers/general-product-scope.md ---
---
type: caliber
title: 通用产品范围
page_key: calibers/general-product-scope
domain: 平台产品配置
status: draft
aliases: [通用产品口径, GENERAL 产品范围]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductController.listPlatformProduct
contract_version: "0.1"
---

「通用产品范围」定义平台产品列表查询中如何界定通用产品。其判定条件为 [[tables/platform_product]] 的 `product_type = 'GENERAL'`，与 INTERWORKING（互通产品）相对。

该口径是后续多条规则的共同前提：只有「多项目 + 通用产品」才会触发 [[rules/goto-product-project-status-check]]，只有「多角色 + 通用产品」才会触发 [[rules/goto-product-company-type-check]]。

## 需求背景

语义分析未提供该口径的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，口径内容来自 `PlatformProductController.listPlatformProduct` 的代码证据。

```ground:caliber
name: 通用产品范围
predicate: "platform_product.product_type = 'GENERAL'"
scope: "查询平台产品列表"
evidence: PlatformProductController.listPlatformProduct
```

## 关联

- 表：[[tables/platform_product]]
- 术语：[[concepts/productCode]]、[[concepts/custRoleCombine]]
- 规则：[[rules/goto-product-project-status-check]]、[[rules/goto-product-company-type-check]]

---END FILE---

---FILE: calibers/platform-product-whitelist.md ---
---
type: caliber
title: 平台产品白名单过滤
page_key: calibers/platform-product-whitelist
domain: 平台产品配置
status: draft
aliases: [白名单过滤口径, platformLimitProductSupport]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductController.filterLimitProduct
  - code:ClientAppController.listOpenProductByCompanyId
contract_version: "0.1"
---

「平台产品白名单过滤」定义产品列表对外返回时的收口方式：以白名单集合 `platformLimitProductSupport` 判断产品编码是否放行（`platformLimitProductSupport.contains(productCode)`）。该口径作用于租户产品列表与已开通产品列表，属于配置驱动的过滤而非数据状态过滤。

相关实现见 [[rules/platform-product-list-filter]]。

## 需求背景

语义分析未提供该口径的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，口径内容来自 `PlatformProductController.filterLimitProduct` 与 `ClientAppController.listOpenProductByCompanyId` 的代码证据。

```ground:caliber
name: 平台产品白名单过滤
predicate: "platformLimitProductSupport.contains(productCode)"
scope: "租户产品列表、已开通产品列表"
evidence: PlatformProductController.filterLimitProduct, ClientAppController.listOpenProductByCompanyId
```

## 关联

- 产品编码术语：[[concepts/productCode]]
- 规则：[[rules/platform-product-list-filter]]
- 表：[[tables/platform_product]]、[[tables/tenant_product]]

---END FILE---

---FILE: calibers/cust-open-product.md ---
---
type: caliber
title: 客户已开通产品
page_key: calibers/cust-open-product
domain: 平台产品配置
status: draft
aliases: [客户已开通产品口径, cust_auth_application OPENED]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustProductDomainService.doActiveProduct
  - code:CustGeneralProductApplication.listOpenProduct
contract_version: "0.1"
---

「客户已开通产品」定义客户维度「已开通」的判定口径：`cust_auth_application.open_status = 'OPENED'`。该口径适用于查询企业已开通产品的所有场景，是客户侧产品可见性的统一收口条件。

对应状态机的迁移终点见 [[processes/cust-product-open-status]]；与租户侧同名概念的区别见 [[concepts/openStatus]]。

## 需求背景

语义分析未提供该口径的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，口径内容来自 `CustProductDomainService.doActiveProduct` 与 `CustGeneralProductApplication.listOpenProduct` 的代码证据。

```ground:caliber
name: 客户已开通产品
predicate: "cust_auth_application.open_status = 'OPENED'"
scope: "查询企业已开通产品"
evidence: CustProductDomainService.doActiveProduct, CustGeneralProductApplication.listOpenProduct
```

## 关联

- 表：[[tables/cust_auth_application]]、[[tables/cust_company_info]]
- 状态机：[[processes/cust-product-open-status]]
- 术语：[[concepts/openStatus]]

---END FILE---

---FILE: calibers/tenant-open-product.md ---
---
type: caliber
title: 租户已开通产品
page_key: calibers/tenant-open-product
domain: 平台产品配置
status: draft
aliases: [租户已开通产品口径, tenant_product open_status=Y]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:TenantProductApplication.listOpenByTenant
  - code:TenantProductDao.listOpenByTenant
contract_version: "0.1"
---

「租户已开通产品」定义租户维度「已开通」的判定口径：`tenant_product.open_status = 'Y'`。该口径适用于查询租户已开通产品的场景，是租户产品列表过滤（[[rules/platform-product-list-filter]]）的前置数据范围。

对应状态机的终态见 [[processes/tenant-product-open-status]]；与客户侧口径（[[calibers/cust-open-product]]）枚举值不同，注意区分。

## 需求背景

语义分析未提供该口径的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，口径内容来自 `TenantProductApplication.listOpenByTenant` 与 `TenantProductDao.listOpenByTenant` 的代码证据。

```ground:caliber
name: 租户已开通产品
predicate: "tenant_product.open_status = 'Y'"
scope: "查询租户已开通产品"
evidence: TenantProductApplication.listOpenByTenant, TenantProductDao.listOpenByTenant
```

## 关联

- 表：[[tables/tenant_product]]
- 状态机：[[processes/tenant-product-open-status]]
- 术语：[[concepts/openStatus]]
- 相关口径：[[calibers/cust-open-product]]

---END FILE---

---FILE: calibers/cust-role-combine-check.md ---
---
type: caliber
title: 角色组合校验条件
page_key: calibers/cust-role-combine-check
domain: 平台产品配置
status: draft
aliases: [角色组合校验口径, checkCustRoleCombine 条件]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:TenantProductApplication.checkCustRoleCombine
contract_version: "0.1"
---

「角色组合校验条件」定义角色组合是否放行的判定方式：将平台产品配置的 `custRoleCombine` 解析为角色集合集合后，判断其是否包含当前角色集合（`custRoleCombine 解析后包含当前角色集合`）。该口径是 [[rules/cust-role-combine-check]] 的判定基准。

配置字段语义见 [[concepts/custRoleCombine]]，角色取值语义见 [[concepts/companyType]]。

## 需求背景

语义分析未提供该口径的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，口径内容来自 `TenantProductApplication.checkCustRoleCombine` 的代码证据。

```ground:caliber
name: 角色组合校验条件
predicate: "custRoleCombine 解析后包含当前角色集合"
scope: "校验企业角色组合"
evidence: TenantProductApplication.checkCustRoleCombine
```

## 关联

- 术语：[[concepts/custRoleCombine]]、[[concepts/companyType]]
- 规则：[[rules/cust-role-combine-check]]
- 表：[[tables/platform_product]]、[[tables/cust_project_rel]]

---END FILE---

---FILE: rules/platform-product-save-check.md ---
---
type: rule
title: 平台产品保存前置校验
page_key: rules/platform-product-save-check
domain: 平台产品配置
status: draft
aliases: [产品保存校验, checkBeforeSave]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductApplication.checkBeforeSave
  - code:PlatformProductDomainService.checkBeforeSave
contract_version: "0.1"
---

保存或更新平台产品前，系统执行前置校验：产品基本信息合法性、产品 code 唯一性、产品类型枚举有效性等。校验失败抛出 BaseException 阻断保存。

该规则的字段落点为 [[tables/platform_product]] 的 `product_code` 与 `product_type`；编码术语见 [[concepts/productCode]]，类型口径见 [[calibers/general-product-scope]]。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `PlatformProductApplication.checkBeforeSave` → `PlatformProductDomainService.checkBeforeSave` 的调用链证据。

```ground:rule
name: 平台产品保存前置校验
content: "保存或更新平台产品前，校验产品基本信息合法性、产品 code 唯一性、产品类型枚举有效性等。"
impact: "校验失败抛出 BaseException 阻断保存。"
field_targets:
  - platform_product.product_code
  - platform_product.product_type
evidence: PlatformProductApplication.checkBeforeSave -> PlatformProductDomainService.checkBeforeSave
```

## 关联

- 表：[[tables/platform_product]]
- 术语：[[concepts/productCode]]
- 口径：[[calibers/general-product-scope]]

---END FILE---

---FILE: rules/tenant-product-on-the-way-check.md ---
---
type: rule
title: 租户产品在途校验
page_key: rules/tenant-product-on-the-way-check
domain: 平台产品配置
status: draft
aliases: [在途校验, checkOnTheWay]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:TenantProductApplication.checkOnTheWay
  - code:TenantProductDomainService.checkOnTheWay
contract_version: "0.1"
---

检查租户产品是否存在在途变更，如有则抛出异常，禁止激活。该规则是 [[processes/tenant-product-open-status]] 状态迁移（P→Y）的前置约束，字段落点为 [[tables/tenant_product]] 的 `open_status`。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `TenantProductApplication.checkOnTheWay` → `TenantProductDomainService.checkOnTheWay` 的调用链证据。

```ground:rule
name: 租户产品在途校验
content: "检查租户产品是否存在在途变更，如有则抛出异常，禁止激活。"
impact: "阻止激活操作。"
field_targets:
  - tenant_product.open_status
evidence: TenantProductApplication.checkOnTheWay -> TenantProductDomainService.checkOnTheWay
```

## 关联

- 表：[[tables/tenant_product]]
- 状态机：[[processes/tenant-product-open-status]]

---END FILE---

---FILE: rules/cust-role-combine-check.md ---
---
type: rule
title: 企业角色组合校验
page_key: rules/cust-role-combine-check
domain: 平台产品配置
status: draft
aliases: [角色组合校验, checkCustRoleCombine]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:TenantProductApplication.checkCustRoleCombine
contract_version: "0.1"
---

同一企业在同一产品下拥有多个角色时，系统校验该角色组合是否在平台产品配置的 `custRoleCombine` 允许范围内，不在范围内则抛出异常，阻止不合法的角色组合。

字段落点为 [[tables/platform_product]] 的 `cust_role_combine` 与 [[tables/cust_project_rel]] 的 `company_type`；判定口径见 [[calibers/cust-role-combine-check]]，术语见 [[concepts/custRoleCombine]] 与 [[concepts/companyType]]。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `TenantProductApplication.checkCustRoleCombine` 的代码证据。

```ground:rule
name: 企业角色组合校验
content: "同一企业在同一产品下拥有多个角色时，校验角色组合是否在平台产品配置的 custRoleCombine 中，不在则抛出异常。"
impact: "阻止不合法的角色组合。"
field_targets:
  - platform_product.cust_role_combine
  - cust_project_rel.company_type
evidence: TenantProductApplication.checkCustRoleCombine
```

## 关联

- 表：[[tables/platform_product]]、[[tables/cust_project_rel]]、[[tables/cust_company_info]]
- 口径：[[calibers/cust-role-combine-check]]
- 术语：[[concepts/custRoleCombine]]、[[concepts/companyType]]

---END FILE---

---FILE: rules/goto-product-project-status-check.md ---
---
type: rule
title: 进入产品前项目状态检查
page_key: rules/goto-product-project-status-check
domain: 平台产品配置
status: draft
aliases: [项目状态检查, gotoProductSupplierFirstRelatedProject]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductApplication.gotoProductSupplierFirstRelatedProject
contract_version: "0.1"
---

多项目产品且产品为通用产品时，进入产品前检查企业关联项目是否生效，未生效则禁止进入。该规则以「多项目 + 通用产品」为前提条件，通用产品的判定见 [[calibers/general-product-scope]]；字段落点为 `tenant_project.project_status` 与 [[tables/cust_project_rel]]。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `PlatformProductApplication.gotoProductSupplierFirstRelatedProject` 的代码证据。规则 field_targets 中出现的 `tenant_project` 表本次语义分析未提供字段级证据，暂不在表目录建档。

```ground:rule
name: 进入产品前项目状态检查
content: "多项目产品且产品为通用产品时，检查企业关联项目是否生效，未生效则禁止进入。"
impact: "阻止进入产品。"
field_targets:
  - tenant_project.project_status
  - cust_project_rel
evidence: PlatformProductApplication.gotoProductSupplierFirstRelatedProject
```

## 关联

- 表：[[tables/cust_project_rel]]、[[tables/platform_product]]
- 口径：[[calibers/general-product-scope]]
- 同类校验：[[rules/goto-product-company-type-check]]

---END FILE---

---FILE: rules/goto-product-company-type-check.md ---
---
type: rule
title: 进入产品前企业角色检查
page_key: rules/goto-product-company-type-check
domain: 平台产品配置
status: draft
aliases: [企业角色检查, gotoProductSupplierByCompanyType]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductApplication.gotoProductSupplierByCompanyType
contract_version: "0.1"
---

多角色产品且产品为通用产品时，进入产品前检查企业是否完成认证，未完成则禁止进入；平台运营方不检查项目状态。字段落点为 [[tables/cust_company_info]] 的 `cust_build_status`，角色语义见 [[concepts/companyType]]，通用产品前提见 [[calibers/general-product-scope]]。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `PlatformProductApplication.gotoProductSupplierByCompanyType` 的代码证据。

```ground:rule
name: 进入产品前企业角色检查
content: "多角色产品且产品为通用产品时，检查企业是否完成认证，平台运营方不检查项目状态。"
impact: "阻止进入产品。"
field_targets:
  - cust_company_info.cust_build_status
evidence: PlatformProductApplication.gotoProductSupplierByCompanyType
```

## 关联

- 表：[[tables/cust_company_info]]
- 口径：[[calibers/general-product-scope]]
- 术语：[[concepts/companyType]]
- 同类校验：[[rules/goto-product-project-status-check]]

---END FILE---

---FILE: rules/platform-product-list-filter.md ---
---
type: rule
title: 平台产品列表过滤
page_key: rules/platform-product-list-filter
domain: 平台产品配置
status: draft
aliases: [产品列表过滤, listTenantProduct 过滤]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductController.listTenantProduct
contract_version: "0.1"
---

非 AGW 端调用时，产品列表按当前租户已开通产品列表过滤，并通过 Nacos 配置 `platform.limit.product.support` 白名单进一步过滤，返回过滤后的产品列表。

该规则组合了两个口径：租户已开通范围见 [[calibers/tenant-open-product]]，白名单判定见 [[calibers/platform-product-whitelist]]；字段落点为 [[tables/tenant_product]] 与 [[tables/platform_product]] 的 `product_code`。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `PlatformProductController.listTenantProduct` 的代码证据。

```ground:rule
name: 平台产品列表过滤
content: "非 AGW 端调用时，按当前租户已开通产品列表过滤，并通过 Nacos 配置 platform.limit.product.support 白名单过滤。"
impact: "返回过滤后的产品列表。"
field_targets:
  - tenant_product
  - platform_product.product_code
evidence: PlatformProductController.listTenantProduct
```

## 关联

- 口径：[[calibers/tenant-open-product]]、[[calibers/platform-product-whitelist]]
- 表：[[tables/tenant_product]]、[[tables/platform_product]]
- 术语：[[concepts/productCode]]

---END FILE---

---FILE: rules/product-agreement-activate.md ---
---
type: rule
title: 产品协议签署后激活
page_key: rules/product-agreement-activate
domain: 平台产品配置
status: draft
aliases: [协议签署激活, createProductAggrement]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustProductDomainService.createProductAggrement
  - code:CustProductDomainService.activeProduct
contract_version: "0.1"
---

根据产品协议配置决定激活路径：无需签署则直接激活；需要签署则先创建合同，签署成功后激活。激活最终将 [[tables/cust_auth_application]] 的 `open_status` 推进到已开通，对应 [[processes/cust-product-open-status]] 中 `activeProduct` 的迁移。企业是否需要电子签章由 [[tables/cust_company_info]] 的 `need_register_ca` 标识。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `CustProductDomainService.createProductAggrement` 与 `CustProductDomainService.activeProduct` 的代码证据。

```ground:rule
name: 产品协议签署后激活
content: "根据产品协议配置，无需签署则直接激活；需要签署则创建合同，签署成功后激活。"
impact: "激活客户产品。"
field_targets:
  - cust_auth_application.open_status
evidence: CustProductDomainService.createProductAggrement, activeProduct
```

## 关联

- 表：[[tables/cust_auth_application]]、[[tables/cust_company_info]]
- 状态机：[[processes/cust-product-open-status]]
- 口径：[[calibers/cust-open-product]]

---END FILE---

---FILE: concepts/productCode.md ---
---
type: concept
title: productCode 平台产品编码
page_key: concepts/productCode
domain: 平台产品配置
status: draft
aliases: [productCode, platformProductCode, 平台产品编码]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:platform_product.product_code
  - code:tenant_product.platform_product_code
  - code:cust_auth_application.platform_product_code
maps_to: platform_product.product_code
adjudication: synonym
also_confused_with: [code]
contract_version: "0.1"
---

productCode 与 platformProductCode 在代码中常混用，二者均指平台产品编码，映射到 [[tables/platform_product]] 的 `product_code`。

边界：`platform_product.code` 是内部编码，不对外使用，不要与 `product_code` 混为一谈。对外传递、白名单过滤（[[calibers/platform-product-whitelist]]）与租户/客户产品关联所使用的都是 `product_code`。

## 需求背景

语义分析未提供该术语的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，术语裁决与边界来自语义分析的术语桥证据。

## 关联

- 表：[[tables/platform_product]]、[[tables/tenant_product]]、[[tables/cust_auth_application]]
- 规则：[[rules/platform-product-save-check]]、[[rules/platform-product-list-filter]]
- 口径：[[calibers/platform-product-whitelist]]

---END FILE---

---FILE: concepts/companyType.md ---
---
type: concept
title: companyType 企业角色类型
page_key: concepts/companyType
domain: 平台产品配置
status: draft
aliases: [companyType, custCompanyType, 企业角色]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:cust_company_info.cust_company_type
  - code:cust_person_info.company_type
  - code:cust_project_rel.company_type
maps_to: cust_company_info.cust_company_type
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
---

companyType、custCompanyType 与「企业角色」是同一语义，映射到 [[tables/cust_company_info]] 的 `cust_company_type`。

边界：companyType 是枚举值，如 CORE、SUPPLIER、DEALER、FINANCE 等。同一语义在 [[tables/cust_person_info]] 与 [[tables/cust_project_rel]] 上以 `company_type` 命名出现。

## 需求背景

语义分析未提供该术语的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，术语裁决与边界来自语义分析的术语桥证据。

## 关联

- 表：[[tables/cust_company_info]]、[[tables/cust_person_info]]、[[tables/cust_project_rel]]
- 规则：[[rules/cust-role-combine-check]]、[[rules/goto-product-company-type-check]]
- 术语：[[concepts/custRoleCombine]]

---END FILE---

---FILE: concepts/tenantCode.md ---
---
type: concept
title: tenantCode 租户标识
page_key: concepts/tenantCode
domain: 平台产品配置
status: draft
aliases: [tenantCode, dbTenantCode, 数据租户标识]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:platform_product.db_tenant_code
  - db:platform_product.app_tenant_code
  - code:cust_company_info.db_tenant_code
maps_to: platform_product.db_tenant_code
adjudication: boundary
also_confused_with: [appTenantCode]
contract_version: "0.1"
---

tenantCode 与 dbTenantCode 指数据租户标识，映射到 [[tables/platform_product]] 的 `db_tenant_code`，[[tables/cust_company_info]] 也以同名 `db_tenant_code` 承载该语义。

边界：`dbTenantCode` 是数据租户标识，用于数据隔离；`appTenantCode` 是逻辑租户标识，用于应用层。两者同表并存但语义层级不同，不可互换。

## 需求背景

语义分析未提供该术语的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，术语裁决与边界来自语义分析的术语桥证据。

## 关联

- 表：[[tables/platform_product]]、[[tables/cust_company_info]]
- 术语：[[concepts/productCode]]

---END FILE---

---FILE: concepts/openStatus.md ---
---
type: concept
title: openStatus 开通状态
page_key: concepts/openStatus
domain: 平台产品配置
status: draft
aliases: [openStatus, productOpenStatus, 开通状态]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:tenant_product.open_status
  - code:cust_auth_application.open_status
maps_to: tenant_product.open_status
adjudication: boundary
also_confused_with: [cust_auth_application.open_status]
contract_version: "0.1"
---

openStatus / productOpenStatus / 开通状态在默认语境下映射到 [[tables/tenant_product]] 的 `open_status`，即租户产品开通状态。

边界：租户产品开通状态与客户产品开通状态枚举值不同——租户产品用 Y/P/N（[[processes/tenant-product-open-status]]），客户产品用 OPENED/OPENING/NOT_OPENED（[[processes/cust-product-open-status]]，字段位于 [[tables/cust_auth_application]]）。两者不可按同一套取值解析。

## 需求背景

语义分析未提供该术语的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，术语裁决与边界来自语义分析的术语桥证据。

## 关联

- 状态机：[[processes/tenant-product-open-status]]、[[processes/cust-product-open-status]]
- 口径：[[calibers/tenant-open-product]]、[[calibers/cust-open-product]]
- 表：[[tables/tenant_product]]、[[tables/cust_auth_application]]

---END FILE---

---FILE: concepts/custRoleCombine.md ---
---
type: concept
title: custRoleCombine 企业角色组合
page_key: concepts/custRoleCombine
domain: 平台产品配置
status: draft
aliases: [custRoleCombine, 企业角色组合, cust_role_combine]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:platform_product.cust_role_combine
maps_to: platform_product.cust_role_combine
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
---

custRoleCombine、「企业角色组合」与 `cust_role_combine` 是同一语义，映射到 [[tables/platform_product]] 的 `cust_role_combine`。

边界：该字段为文本格式，需解析为 Set<Set<String>>——外层集合表示可接受的组合，内层集合表示同一组合内的角色集合。判定逻辑见 [[calibers/cust-role-combine-check]] 与 [[rules/cust-role-combine-check]]。

## 需求背景

语义分析未提供该术语的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，术语裁决与边界来自语义分析的术语桥证据。

## 关联

- 表：[[tables/platform_product]]
- 口径：[[calibers/cust-role-combine-check]]
- 规则：[[rules/cust-role-combine-check]]
- 术语：[[concepts/companyType]]

---END FILE---

---REVIEW: tables | 平台产品配置域全部表页 ---
语义分析未给出物理库名（scope.databases 无 [DB] 证据），当前所有页面 frontmatter 的 `scope.databases` 以 `unknown` 占位。需补充各表的物理库名后统一回填，并确认 platform_product / tenant_product / cust_* 是否同库。
---END REVIEW---

---REVIEW: tables | tenant_project ---
规则 `进入产品前项目状态检查` 的 field_targets 引用了 `tenant_project.project_status`，但本次语义分析的 field_semantics 未提供 tenant_project 的字段级证据，故未为其建立 table 页。待补充该表字段证据后建档。
---END REVIEW---