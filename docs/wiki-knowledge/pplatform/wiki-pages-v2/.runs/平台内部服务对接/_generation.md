---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info 企业信息表
page_key: cust_company_info
domain: 平台内部服务对接
status: draft
aliases:
  - 企业信息表
  - 企业主数据表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

cust_company_info 是平台内部服务对接的企业（客户）主数据表。平台侧的企业建档、认证、审核、冻结与注销都以本表记录为锚点，企业下的联系人、项目、角色与授权申请则通过企业业务编码 `code` 联结，因此它同时是客户服务端与运营端两侧服务共用的读写对象。

企业在平台上的两个生命周期维度分别落在两个字段上：`cust_build_status` 描述建档与认证过程（见 [[cust_build_status_flow]]），`cust_status` 描述企业本身的生效状态（见 [[cust_status_flow]]）。企业下的人员在 [[cust_person_info]]，二者通过 [[ref_cust_company_info]] 约定的关联企业编码字段联结；产品与项目侧关联见 [[cust_project_rel]]、[[cust_role_info]]、[[cust_auth_application]]。

## 需求背景
内部服务在企业维度上需要一份稳定的主数据：客户侧服务负责企业信息录入与确认，运营侧服务负责审核、冻结与注销，两侧读写同一张表。因此字段语义必须明确划分——哪些由客户填写（法人姓名、法人手机号、法人证件），哪些由平台维护（各类状态、租户编码、审核退回标志），哪些是跨表关联的键（`code`）。表中还保存统一社会信用代码与法人证件信息，用于认证类服务比对。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，作为契约初稿；字段物理类型与字典绑定尚未在证据中出现，暂留空。企业建档状态流转见 [[cust_build_status_flow]]，企业生效状态流转见 [[cust_status_flow]]。

```ground:table
table: cust_company_info
fields:
  - name: id
    type: ""
    desc: 企业主键ID
    dict: ""
  - name: code
    type: ""
    desc: 企业业务编码，用于跨表关联
    dict: ""
  - name: name
    type: ""
    desc: 企业名称
    dict: ""
  - name: certification_no
    type: ""
    desc: 统一社会信用代码
    dict: ""
  - name: enable
    type: ""
    desc: 启用状态，Y/N
    dict: ""
  - name: db_tenant_code
    type: ""
    desc: 租户编码
    dict: ""
  - name: cust_build_status
    type: ""
    desc: 企业建档状态
    dict: ""
  - name: cust_status
    type: ""
    desc: 企业状态
    dict: ""
  - name: cust_company_type
    type: ""
    desc: 企业角色，JSON数组字符串
    dict: ""
  - name: identify_style
    type: ""
    desc: 认证方式
    dict: ""
  - name: need_register_ca
    type: ""
    desc: 是否需要开通电子签章，Y/N
    dict: ""
  - name: ca_register_status
    type: ""
    desc: CA注册状态，Y/N
    dict: ""
  - name: legal_name
    type: ""
    desc: 法人姓名
    dict: ""
  - name: legal_phone
    type: ""
    desc: 法人手机号
    dict: ""
  - name: legal_email
    type: ""
    desc: 法人邮箱
    dict: ""
  - name: legal_certification_type
    type: ""
    desc: 法人证件类型
    dict: ""
  - name: legal_certification_no
    type: ""
    desc: 法人证件号
    dict: ""
  - name: head_company
    type: ""
    desc: 总公司标识
    dict: ""
  - name: cust_build_type
    type: ""
    desc: 建档类型
    dict: ""
  - name: cust_from
    type: ""
    desc: 客户来源
    dict: ""
  - name: audit_back_flag
    type: ""
    desc: 审核退回标志，Y/N
    dict: ""
  - name: check_status
    type: ""
    desc: 审核状态
    dict: ""
  - name: data_type
    type: ""
    desc: 数据类型
    dict: ""
```
---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info 企业联系人表
page_key: cust_person_info
domain: 平台内部服务对接
status: draft
aliases:
  - 企业联系人表
  - 客户人员表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

cust_person_info 保存企业下的联系人（人员）记录，是平台内部服务把「企业」与「系统用户」连接起来的一层：每条记录通过 `ref_cust_company_info` 归属到一家企业，通过 `user_id` 关联到系统用户 [[sys_user]]，并通过 `user_type` 区分该联系人在企业中的角色（admin / operator / guest）。企业角色维度另由 `company_type` 表达，与主表中的 [[company_type_role]] 同义。

人员记录带有自己的建档状态 `cust_build_status`、启用状态 `enable` 与状态 `status`（取值见 CustPersonStatusConstant），因此联系人列表类服务在查询时需要同时施加启用与状态的过滤条件，见口径 [[valid_person]]。运营人员信息（`operator_id`、`operator_realname`、`operator`）也随人员记录一起保存，用于运营侧服务回溯经办关系。

## 需求背景
企业被创建后，客户侧服务需要为企业登记联系人并为其分配系统账号；运营侧服务需要按企业、按用户类型查询这些联系人，并在冻结等场景下排除失效数据。手机号以加密方式存储，因此读取该字段的服务需要具备解密能力，不能直接按明文比对。用户类型与管理口径（管理员、经办人）见 [[user_type_role]]、[[admin_user]]、[[operator_user]]。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: cust_person_info
fields:
  - name: id
    type: ""
    desc: 联系人主键ID
    dict: ""
  - name: ref_cust_company_info
    type: ""
    desc: 关联的企业编码
    dict: ""
  - name: company_type
    type: ""
    desc: 企业角色
    dict: ""
  - name: enable
    type: ""
    desc: 启用状态，Y/N
    dict: ""
  - name: user_type
    type: ""
    desc: 用户类型：admin/operator/guest
    dict: ""
  - name: user_id
    type: ""
    desc: 关联的系统用户ID
    dict: ""
  - name: phone
    type: ""
    desc: 手机号（加密存储）
    dict: ""
  - name: name
    type: ""
    desc: 姓名
    dict: ""
  - name: user_name
    type: ""
    desc: 用户名
    dict: ""
  - name: email
    type: ""
    desc: 邮箱
    dict: ""
  - name: status
    type: ""
    desc: 联系人状态，取值见 CustPersonStatusConstant
    dict: CustPersonStatusConstant
  - name: operator_id
    type: ""
    desc: 运营人员ID
    dict: ""
  - name: operator_realname
    type: ""
    desc: 运营人员姓名
    dict: ""
  - name: operator
    type: ""
    desc: 运营人员账号
    dict: ""
  - name: certification_type
    type: ""
    desc: 证件类型
    dict: ""
  - name: certification_no
    type: ""
    desc: 证件号
    dict: ""
  - name: cust_build_status
    type: ""
    desc: 建档状态
    dict: ""
  - name: db_tenant_code
    type: ""
    desc: 租户编码
    dict: ""
```
---END FILE---

---FILE: tables/sys_user.md ---
---
type: table
title: sys_user 系统用户表
page_key: sys_user
domain: 平台内部服务对接
status: draft
aliases:
  - 系统用户表
  - 用户账号表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

sys_user 保存平台内部的系统用户账号，主键 `id` 被 [[cust_person_info]] 的 `user_id` 引用，用于把企业联系人挂到具体的登录账号上；`user_name` 与 `name` 区分账号标识与姓名，`mobile`、`email`、`certificate_type`、`certificate_no` 提供联系方式与证件信息。

在内部服务对接中，本表是「账号—企业」关系的账号侧端点：企业侧关系由 [[cust_person_info]] 与 [[sys_cust_user_rel]] 表达，账号本身的信息只在用户服务内维护。

## 需求背景
企业建档过程中会为联系人分配系统账号，运营侧又会按账号冻结/解冻经办关系（见 [[operator_freeze_flow]]），因此账号标识与联系方式需要稳定可读；证件类字段用于实名与认证类服务的核对。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: sys_user
fields:
  - name: id
    type: ""
    desc: 系统用户ID
    dict: ""
  - name: user_name
    type: ""
    desc: 用户名
    dict: ""
  - name: name
    type: ""
    desc: 姓名
    dict: ""
  - name: mobile
    type: ""
    desc: 手机号
    dict: ""
  - name: email
    type: ""
    desc: 邮箱
    dict: ""
  - name: certificate_type
    type: ""
    desc: 证件类型
    dict: ""
  - name: certificate_no
    type: ""
    desc: 证件号
    dict: ""
```
---END FILE---

---FILE: tables/sso_user.md ---
---
type: table
title: sso_user 单点登录用户表
page_key: sso_user
domain: 平台内部服务对接
status: draft
aliases:
  - SSO用户表
  - 单点登录用户映射
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

sso_user 保存单点登录侧的账号映射：`sso_id` 为 SSO 用户标识，`login_name`、`user_name` 为登录名与用户名，`sys_channel` 记录系统渠道。内部服务在接入 SSO 时需要把平台账号与外部登录身份对应起来，本表是这一映射的落点；租户侧的 SSO 渠道配置见 [[tenant_setting_config]] 的 `sso_tenant_chanel`。

## 需求背景
平台按租户提供不同渠道的登录入口，登录侧服务需要按渠道解析 SSO 身份并映射为平台用户，因此渠道（`sys_channel`）与租户渠道配置需要保持一致。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: sso_user
fields:
  - name: login_name
    type: ""
    desc: 登录名
    dict: ""
  - name: user_name
    type: ""
    desc: 用户名
    dict: ""
  - name: sso_id
    type: ""
    desc: SSO用户ID
    dict: ""
  - name: sys_channel
    type: ""
    desc: 系统渠道
    dict: ""
```
---END FILE---

---FILE: tables/tenant_setting_config.md ---
---
type: table
title: tenant_setting_config 租户设置配置表
page_key: tenant_setting_config
domain: 平台内部服务对接
status: draft
aliases:
  - 租户配置表
  - 租户设置表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

tenant_setting_config 以 `db_tenant_code` 为主键维度保存租户级设置：`sso_tenant_chanel` 指定 SSO 租户渠道，`platform_secret_key` 保存平台密钥，`band_name` 为品牌名称，`platform_operator` 以 JSON 数组保存平台运营方配置。租户编码同时出现在 [[cust_company_info]]、[[cust_person_info]]、[[tenant_product]] 等表上，是内部服务跨表判定租户归属的公共维度。

## 需求背景
同一套内部服务要为多个租户提供服务，登录渠道、品牌展示与密钥必须按租户隔离；平台运营方以 JSON 数组形式配置，意味着读取该字段的服务需按数组结构解析。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: tenant_setting_config
fields:
  - name: db_tenant_code
    type: ""
    desc: 租户编码
    dict: ""
  - name: sso_tenant_chanel
    type: ""
    desc: SSO租户渠道
    dict: ""
  - name: platform_secret_key
    type: ""
    desc: 平台密钥
    dict: ""
  - name: band_name
    type: ""
    desc: 品牌名称
    dict: ""
  - name: platform_operator
    type: ""
    desc: 平台运营方配置，JSON数组
    dict: ""
```
---END FILE---

---FILE: tables/tenant_product.md ---
---
type: table
title: tenant_product 租户产品表
page_key: tenant_product
domain: 平台内部服务对接
status: draft
aliases:
  - 租户产品关系表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

tenant_product 保存租户与平台产品的开通关系：`db_tenant_code` 标识租户，`platform_product_code` 标识平台产品编码。产品编码是内部服务判定「某租户/某企业是否接入某产品」的关键值，同时出现在 [[tenant_project]]、[[cust_auth_application]] 以及 [[sys_cust_user_rel]] 的 `product_id` 语义域中。

## 需求背景
企业接入产品需要与租户已开通的产品范围对齐，因此产品编码必须在租户侧与客户侧使用同一取值；判断用户是否已关联指定产品的口径见 [[current_product_rel]]。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: tenant_product
fields:
  - name: platform_product_code
    type: ""
    desc: 平台产品编码
    dict: ""
  - name: db_tenant_code
    type: ""
    desc: 租户编码
    dict: ""
```
---END FILE---

---FILE: tables/tenant_project.md ---
---
type: table
title: tenant_project 项目表
page_key: tenant_project
domain: 平台内部服务对接
status: draft
aliases:
  - 租户项目表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

tenant_project 保存平台项目主数据：`id` 为项目 ID，`name` 为项目名称，`project_status` 为项目状态，`platform_product_code` 关联产品维度。企业侧与项目的关系不在本表，而落在 [[cust_project_rel]]，后者以 `project_id`（字符串）引用项目。

## 需求背景
项目与产品共同构成企业接入的业务范围；企业在客户服务侧可见的项目由其与企业的关联记录决定，因此项目主数据与关联表需要成对读取。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: tenant_project
fields:
  - name: id
    type: ""
    desc: 项目ID
    dict: ""
  - name: name
    type: ""
    desc: 项目名称
    dict: ""
  - name: project_status
    type: ""
    desc: 项目状态
    dict: ""
  - name: platform_product_code
    type: ""
    desc: 平台产品编码
    dict: ""
```
---END FILE---

---FILE: tables/cust_project_rel.md ---
---
type: table
title: cust_project_rel 企业项目关系表
page_key: cust_project_rel
domain: 平台内部服务对接
status: draft
aliases:
  - 企业项目关联表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

cust_project_rel 描述企业与其可见项目之间的关系：`ref_cust_project_rel_cust_company_info` 按 [[ref_cust_company_info]] 约定存放关联企业编码，`project_id` 与 `product_id` 均为字符串形式的外部标识，`company_type` 表达企业角色（见 [[company_type_role]]），`show_flag` 为 Y/N 的显示标志（见 [[yn_flag_convention]]）。

## 需求背景
企业接入多个产品与项目时，客户侧服务只应展示与其相关且允许展示的项目，因此关联记录既要表达归属，也要表达可见性（`show_flag`），并按企业角色区分。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。`project_id`、`product_id` 在语义上为字符串标识，与 [[tenant_project]] 的数值主键并非同一取值形态。

```ground:table
table: cust_project_rel
fields:
  - name: project_id
    type: ""
    desc: 项目ID（字符串）
    dict: ""
  - name: ref_cust_project_rel_cust_company_info
    type: ""
    desc: 关联企业编码
    dict: ""
  - name: company_type
    type: ""
    desc: 企业角色
    dict: ""
  - name: product_id
    type: ""
    desc: 产品ID（字符串）
    dict: ""
  - name: show_flag
    type: ""
    desc: 显示标志，Y/N
    dict: ""
```
---END FILE---

---FILE: tables/cust_role_info.md ---
---
type: table
title: cust_role_info 企业角色表
page_key: cust_role_info
domain: 平台内部服务对接
status: draft
aliases:
  - 企业角色信息表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

cust_role_info 保存企业维度的角色记录：`ref_cust_company_info` 按 [[ref_cust_company_info]] 约定关联企业编码，`role_type` 为角色类型，`platform_cust_id` 为平台客户 ID，`status` 为状态。它区别于人员表上的 `company_type`（企业角色语义，见 [[company_type_role]]）：前者是企业在平台中被授予的角色，后者是人员/关联记录上标注的角色取值。

## 需求背景
企业内部不同角色（如管理员与经办人）在平台侧拥有不同权限，授权类服务需要按企业、按角色类型检索；平台客户 ID 是企业在本表的另一种标识，与业务编码 `code` 的取值需分别判定，不应混用。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: cust_role_info
fields:
  - name: ref_cust_company_info
    type: ""
    desc: 关联企业编码
    dict: ""
  - name: role_type
    type: ""
    desc: 角色类型
    dict: ""
  - name: platform_cust_id
    type: ""
    desc: 平台客户ID
    dict: ""
  - name: status
    type: ""
    desc: 状态
    dict: ""
```
---END FILE---

---FILE: tables/cust_auth_application.md ---
---
type: table
title: cust_auth_application 企业授权申请表
page_key: cust_auth_application
domain: 平台内部服务对接
status: draft
aliases:
  - 企业授权申请表
  - 客户授权申请
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

cust_auth_application 保存企业对平台产品的授权申请：`ref_cust_company_info` 按 [[ref_cust_company_info]] 约定关联企业编码，`platform_product_code` 标识申请的产品。企业的认证与建档过程见 [[cust_build_status_flow]]，授权申请是该过程在服务侧的业务结果之一。

## 需求背景
内部服务在产品开通链路上需要记录「哪家企业申请了哪个产品」，产品编码取值须与 [[tenant_product]] 保持一致；企业维度的关联一律以企业编码而非主键进行。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: cust_auth_application
fields:
  - name: ref_cust_company_info
    type: ""
    desc: 关联企业编码
    dict: ""
  - name: platform_product_code
    type: ""
    desc: 平台产品编码
    dict: ""
```
---END FILE---

---FILE: tables/sys_cust_user_rel.md ---
---
type: table
title: sys_cust_user_rel 客户用户关系表
page_key: sys_cust_user_rel
domain: 平台内部服务对接
status: draft
aliases:
  - 客户用户关联表
  - 经办人关系表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

sys_cust_user_rel 描述客户（`cust_id`、`cust_type`）与系统用户（`user_id`）之间的授权关系，并记录角色 `role_id`、产品 `product_id` 以及冻结状态 `is_freeze`。在内部服务对接中，它是用户能否以某企业身份操作某产品的主要判据：查询侧使用未冻结口径 [[not_frozen_user_rel]]，产品维度使用 [[current_product_rel]]，冻结/解冻的流转见 [[operator_freeze_flow]]。

## 需求背景
运营侧需要对经办人执行冻结与解冻，冻结后该用户与该客户/产品的关联不应再参与权限判定；同时同一用户可能关联多个产品，判断「是否已关联指定产品」必须带上产品条件，不能只看关系是否存在。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: sys_cust_user_rel
fields:
  - name: cust_type
    type: ""
    desc: 客户类型
    dict: ""
  - name: cust_id
    type: ""
    desc: 客户ID
    dict: ""
  - name: user_id
    type: ""
    desc: 用户ID
    dict: ""
  - name: role_id
    type: ""
    desc: 角色ID
    dict: ""
  - name: product_id
    type: ""
    desc: 产品ID
    dict: ""
  - name: is_freeze
    type: ""
    desc: 冻结状态，Y/N
    dict: ""
```
---END FILE---

---FILE: processes/cust_build_status_flow.md ---
---
type: process
title: 企业认证状态机
page_key: cust_build_status_flow
domain: 平台内部服务对接
status: draft
aliases:
  - 企业建档状态流转
  - cust_company_info.cust_build_status 状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

企业认证状态机描述 [[cust_company_info]] 上 `cust_build_status` 字段的取值与流转，是平台内部服务对接中「客户录入 / 平台录入 → 客户确认 → 运营审核 → 建档成功或失败」这条链路的契约表达。字段本身仍是表 [[cust_company_info]] 的一部分，本页只描述其状态语义。

流转的关键分叉在于提交建档的入口：邀请认证模式下若由客户录入或客户自行注册认证，企业先进入待客户确认；若由平台录入，则直接进入客户建档中。之后由客户提交审核推动到建档中，运营中台审核通过或拒绝分别到达建档成功与建档失败，审核退回则回到待客户确认；建档失败后可重新提交并回到待客户确认。相关状态展示于企业的启用与审核字段旁，见 [[cust_status_flow]]。

## 需求背景
客户侧与运营侧服务读写同一状态字段，任何一侧都需要知道「当前轮到谁处理」。因此状态取值必须是稳定的枚举字符串，而不是可自由拼写的文案；审核退回与重新提交也必须回到确定的节点，避免出现两侧都无法处理的中间态。

## 版本演进
- v0.1（本页）：状态与流转来自代码语义分析，`AWAIT_CUST_CONFIRM`（待客户确认（简易））在证据中只有状态定义，未给出迁移边，暂按孤立状态记录。

```ground:process
name: 企业认证状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始化
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 客户建档中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILD_FAIL
    label: 建档失败
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易）
    source: code_enum
transitions:
  - from: INIT
    event: 提交建档（邀请认证-客户录入/注册认证）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: INIT
    event: 提交建档（邀请认证-平台录入）
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交审核
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 运营中台审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: BUILD_FAIL
    event: 重新提交（客户录入）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
```
---END FILE---

---FILE: processes/cust_status_flow.md ---
---
type: process
title: 企业状态机
page_key: cust_status_flow
domain: 平台内部服务对接
status: draft
aliases:
  - 企业生效状态流转
  - cust_company_info.cust_status 状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

企业状态机描述 [[cust_company_info]] 上 `cust_status` 字段的取值与流转，覆盖企业从新增到生效、冻结、注销的生命周期。它与建档状态（见 [[cust_build_status_flow]]）是两条独立的轨道：建档成功推动企业进入生效，而冻结/解冻与注销只在本状态机上发生。

冻结用于临时停用企业（如风险控制），解冻恢复到生效；注销是不可逆的终态，对应平台侧的注销操作。企业的启用标记 `enable` 与状态口径的关系见 [[valid_company]]，避免出现「已注销但被当作有效企业查出」的情形。

## 需求背景
运营侧服务需要在企业维度执行冻结、解冻与注销，客户侧与其它内部服务则需要按生效状态判断企业是否可用。状态语义必须集中在单一字段上，冻结/解冻成对出现，注销作为终态不再回到生效。

## 版本演进
- v0.1（本页）：状态与流转来自代码语义分析；`ADD → CHANGE` 等变更类流转在证据中未出现，暂不记录。企业有效性的查询口径见 [[valid_company]]。

```ground:process
name: 企业状态机
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增
    source: code_enum
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: CHANGE
    label: 变更中
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
transitions:
  - from: ADD
    event: 建档成功
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth"
  - from: EFFECT
    event: 冻结企业
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java:freeze"
  - from: FREEZE
    event: 解冻企业
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:unfreeze"
  - from: EFFECT
    event: 注销企业
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java:diable"
```
---END FILE---

---FILE: processes/operator_freeze_flow.md ---
---
type: process
title: 经办人冻结状态机
page_key: operator_freeze_flow
domain: 平台内部服务对接
status: draft
aliases:
  - 经办人冻结流转
  - sys_cust_user_rel.is_freeze 状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

经办人冻结状态机描述 [[sys_cust_user_rel]] 上 `is_freeze` 字段的两个取值与冻结/解冻两个操作的对应关系。该字段是 Y/N 形布尔约定在关系表上的实例（见 [[yn_flag_convention]]），冻结与解冻由同一个操作入口按目标状态切换。

在权限判定链路上，未冻结状态是有效关联的必要条件，查询口径见 [[not_frozen_user_rel]]；同一用户可能持有多条关联（不同客户、不同产品），冻结只作用于被操作的那条关系，产品维度的判定见 [[current_product_rel]]。

## 需求背景
运营侧需要在不删除关系数据的前提下停用某个经办人，因此用冻结标志代替物理删除；权限类服务在检索关系时必须显式带上未冻结条件，否则被冻结的经办人仍会通过校验。

## 版本演进
- v0.1（本页）：状态取值与流转来自代码语义分析，取值来源为常量而非枚举类。

```ground:process
name: 经办人冻结状态机
field: sys_cust_user_rel.is_freeze
states:
  - value: N
    label: 未冻结
    source: code_const
  - value: Y
    label: 已冻结
    source: code_const
transitions:
  - from: N
    event: 冻结经办人
    to: Y
    evidence: "code_path:PlatFormUserApplication.java:freezeOrThawOperatorUser"
  - from: Y
    event: 解冻经办人
    to: N
    evidence: "code_path:PlatFormUserApplication.java:freezeOrThawOperatorUser"
```
---END FILE---

---FILE: calibers/valid_company.md ---
---
type: caliber
title: 有效企业
page_key: valid_company
domain: 平台内部服务对接
status: draft
aliases:
  - 有效企业口径
  - 企业启用过滤
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

「有效企业」是查询 [[cust_company_info]] 时的默认过滤条件：启用状态为 Y。内部服务在按编码或名称取企业主数据时，若不附加该条件，可能取到已停用的企业记录，因此新建或临时企业的流程也沿用同一口径。该口径只表达启用与否，与企业状态机（见 [[cust_status_flow]]）中的冻结、注销是两个维度，组合使用时需要分别判断。

## 需求背景
企业可能被停用但历史数据仍需保留，因此不能通过删除记录来屏蔽；把「有效」固化为一个可复用的过滤条件，能让客户侧与运营侧服务得到一致的企业可见范围。

## 版本演进
- v0.1（本页）：口径谓词来自代码语义分析。

```ground:caliber
name: 有效企业
predicate: "cust_company_info.enable = 'Y'"
scope: 查询企业主数据时默认过滤条件
evidence: "code_path:PlatFormRvsApplication.java:getAndCreateTempCompany"
```
---END FILE---

---FILE: calibers/valid_person.md ---
---
type: caliber
title: 有效联系人
page_key: valid_person
domain: 平台内部服务对接
status: draft
aliases:
  - 有效联系人口径
  - 企业联系人过滤
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

「有效联系人」用于查询 [[cust_person_info]] 中的企业联系人列表，同时施加两个条件：启用状态为 Y，且联系人状态属于 ADD 或 EFFECT。两个条件的语义不同——前者是记录级启用（见 [[yn_flag_convention]]），后者是人员状态机上的可用节点（取值见 CustPersonStatusConstant），因此只过滤其中之一都会产生偏差。

## 需求背景
企业用户列表是客户侧与运营侧共用的高频查询，需要稳定地排除停用与失效人员；把该组合固化为口径后，人员表的 `status` 字典变更不应悄悄放宽查询结果。

## 版本演进
- v0.1（本页）：口径谓词来自代码语义分析，`status` 的完整枚举取值未在证据中出现，当前仅记录参与判定的两个取值。

```ground:caliber
name: 有效联系人
predicate: "cust_person_info.enable = 'Y' AND cust_person_info.status IN ('ADD','EFFECT')"
scope: 查询企业联系人列表
evidence: "code_path:PlatFormUserApplication.java:listCompanyUser"
```
---END FILE---

---FILE: calibers/not_frozen_user_rel.md ---
---
type: caliber
title: 未冻结用户关联
page_key: not_frozen_user_rel
domain: 平台内部服务对接
status: draft
aliases:
  - 未冻结关联口径
  - 权限关系过滤
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

「未冻结用户关联」是查询 [[sys_cust_user_rel]] 关系时的过滤条件：`is_freeze = 'N'`。它把经办人冻结状态机（见 [[operator_freeze_flow]]）的当前取值翻译成查询语义——被冻结的关系仍然保留在表中，但不应参与用户列表与权限判定。该口径通常与联系人口径 [[valid_person]] 一起使用。

## 需求背景
冻结是运营侧的临时处置手段，关系数据需要保留以便解冻；如果把冻结实现为删除，将无法恢复且会丢失角色与产品配置，因此在读取侧统一附加未冻结条件更安全。

## 版本演进
- v0.1（本页）：口径谓词来自代码语义分析。

```ground:caliber
name: 未冻结用户关联
predicate: "sys_cust_user_rel.is_freeze = 'N'"
scope: 查询有效用户关联关系
evidence: "code_path:PlatFormUserApplication.java:listCompanyUser"
```
---END FILE---

---FILE: calibers/current_product_rel.md ---
---
type: caliber
title: 当前产品关联
page_key: current_product_rel
domain: 平台内部服务对接
status: draft
aliases:
  - 指定产品关联口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

「当前产品关联」是在 [[sys_cust_user_rel]] 上判断用户是否已关联指定产品时使用的条件：`product_id` 等于入参 productId。产品维度不能省略——同一用户对不同产品可能各有一条关系记录，只按用户判定会误认为已开通全部产品。产品编码的来源见 [[tenant_product]]，企业侧产品授权见 [[cust_auth_application]]。

## 需求背景
新增或更新经办人时需要先确认该用户在产品维度上是否已有关系，以决定插入还是更新；产品取值必须来自调用方传入的产品上下文，而不是从关系记录中猜测。

## 版本演进
- v0.1（本页）：口径谓词来自代码语义分析，参数形式以证据中的写法为准。

```ground:caliber
name: 当前产品关联
predicate: "sys_cust_user_rel.product_id = :productId"
scope: 判断用户是否已关联指定产品
evidence: "code_path:PlatFormUserApplication.java:addOrUpdateOperatorUser"
```
---END FILE---

---FILE: calibers/admin_user.md ---
---
type: caliber
title: 管理员用户
page_key: admin_user
domain: 平台内部服务对接
status: draft
aliases:
  - 企业管理员口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

「管理员用户」以 [[cust_person_info]] 的 `user_type = 'admin'` 识别企业管理员。用户类型取值见 [[user_type_role]]；与之并列的经办人判定见 [[operator_user]]。该口径通常与联系人有效性口径 [[valid_person]] 组合使用，避免把已停用的管理员纳入判定。

## 需求背景
企业管理员在平台上承担确认、提交审核等动作，服务侧需要稳定识别该角色；角色信息落在人员表上而非独立角色表，角色表 [[cust_role_info]] 表达的是另一维度的企业角色，两者不可互相替代。

## 版本演进
- v0.1（本页）：口径谓词来自代码语义分析。

```ground:caliber
name: 管理员用户
predicate: "cust_person_info.user_type = 'admin'"
scope: 识别企业管理员
evidence: "code_path:CustFacade.java:getCustPerson"
```
---END FILE---

---FILE: calibers/operator_user.md ---
---
type: caliber
title: 经办人用户
page_key: operator_user
domain: 平台内部服务对接
status: draft
aliases:
  - 经办人口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

「经办人用户」以 [[cust_person_info]] 的 `user_type = 'operator'` 识别企业经办人，与管理口径 [[admin_user]] 对称，取值域见 [[user_type_role]]。经办人在关系表上的冻结状态见 [[sys_cust_user_rel]] 与状态机 [[operator_freeze_flow]]。

## 需求背景
经办人是被运营侧冻结/解冻的直接对象，因此人员角色与关系冻结两个维度需要分别判定：前者决定「他是不是经办人」，后者决定「这条关系当前是否可用」。

## 版本演进
- v0.1（本页）：本口径在语义分析中被截断，当前仅确认名称与谓词，适用范围与代码出处待补（见页面末尾 REVIEW 记录）。

```ground:caliber
name: 经办人用户
predicate: "cust_person_info.user_type = 'operator'"
```
---END FILE---

---FILE: concepts/ref_cust_company_info.md ---
---
type: concept
title: 关联企业编码
page_key: ref_cust_company_info
domain: 平台内部服务对接
status: draft
aliases:
  - ref_cust_company_info 字段族
  - 关联企业编码约定
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
maps_to:
  - cust_company_info.code
field_targets:
  - cust_person_info.ref_cust_company_info
  - cust_project_rel.ref_cust_project_rel_cust_company_info
  - cust_role_info.ref_cust_company_info
  - cust_auth_application.ref_cust_company_info
adjudication: >
  各关联表上的 ref_cust_company_info 系列字段存放企业业务编码，指向
  cust_company_info.code；跨表关联以企业编码取值，而不是以企业主键 id 取值。
also_confused_with:
  - cust_role_info.platform_cust_id
  - cust_project_rel.project_id
---

「关联企业编码」是平台内部服务对接中的一条字段命名约定：凡是需要指向企业主体的关联表，都使用 `ref_cust_company_info`（或在被外键命名规则改造后形如 `ref_cust_project_rel_cust_company_info`）这类字段存放**企业业务编码**，与 [[cust_company_info]] 的 `code` 对应。

这条约定使得多个服务可以在不了解对方表结构的情况下按同一取值联结——[[cust_person_info]] 用它把人员挂到企业，[[cust_project_rel]] 用它表达企业与项目的关系，[[cust_role_info]]、[[cust_auth_application]] 同样如此。相关页面：[[cust_company_info]]、[[cust_person_info]]、[[cust_project_rel]]。

## 需求背景
企业主键 `id` 是数据库内部标识，业务侧服务在接口与消息中流动的是企业编码。若部分表按主键关联、部分表按编码关联，内部服务对接时会出现「传了编码查不到」的错配，因此把关联取值统一到企业编码上是必要的契约约束。

## 版本演进
- v0.1（本页）：约定来自代码语义分析中各关联表字段释义的一致性归纳。容易混淆的标识：`cust_role_info.platform_cust_id`（平台客户ID）与 `cust_project_rel.project_id`（项目ID），它们与关联企业编码不是同一取值域。
---END FILE---

---FILE: concepts/yn_flag_convention.md ---
---
type: concept
title: Y/N 布尔约定
page_key: yn_flag_convention
domain: 平台内部服务对接
status: draft
aliases:
  - Y/N 标志位
  - 布尔字符约定
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
field_targets:
  - cust_company_info.enable
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - cust_company_info.audit_back_flag
  - cust_person_info.enable
  - cust_project_rel.show_flag
  - sys_cust_user_rel.is_freeze
adjudication: >
  上述字段以字符 Y / N 表达布尔语义，Y 表示是、启用、需要或已冻结状态成立；
  服务侧读取与写入均应使用单字符取值，不写入 1/0 或 true/false。
also_confused_with:
  - cust_person_info.status
  - cust_company_info.cust_status
---

「Y/N 布尔约定」描述平台内部服务对接中一组以字符 `Y` / `N` 存储的布尔字段。它们语义各异——启用（`enable`）、是否需要开通电子签章（`need_register_ca`）、CA 注册状态（`ca_register_status`）、审核退回标志（`audit_back_flag`）、关联显示标志（`show_flag`）、经办人冻结状态（`is_freeze`）——但取值形态一致，因此查询与写入可以按同一约定处理。

这类字段是查询口径的常见组成：企业有效性口径 [[valid_company]] 使用 `enable = 'Y'`，未冻结口径 [[not_frozen_user_rel]] 使用 `is_freeze = 'N'`，冻结状态机见 [[operator_freeze_flow]]。

## 需求背景
布尔语义在不同表上以字符存储，如果某些服务按 1/0 处理，就会出现过滤条件永远为假或永远为真的隐性缺陷；把取值形态固化为一条约定，可以让人工与代码审查都按同一标准检查。

## 版本演进
- v0.1（本页）：约定来自代码语义分析中各字段释义中「Y/N」描述的一致性归纳。注意区分同为「状态」但取值是枚举字符串的字段，例如 `cust_person_info.status`、`cust_company_info.cust_status`，它们不属于本约定。
---END FILE---

---FILE: concepts/company_type_role.md ---
---
type: concept
title: 企业角色 company_type
page_key: company_type_role
domain: 平台内部服务对接
status: draft
aliases:
  - 企业角色术语桥
  - company_type 字段族
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
maps_to:
  - cust_company_info.cust_company_type
field_targets:
  - cust_person_info.company_type
  - cust_project_rel.company_type
adjudication: >
  企业主表以 cust_company_info.cust_company_type 承载企业角色，且以 JSON 数组字符串
  存储多个角色；cust_person_info.company_type 与 cust_project_rel.company_type 是
  同一术语在关联表上的落点，取值需与主表角色集合保持一致。
also_confused_with:
  - cust_person_info.user_type
  - sys_cust_user_rel.cust_type
---

「企业角色」是同一业务术语在多个表上的桥接点：主表 [[cust_company_info]] 用 `cust_company_type` 以 JSON 数组字符串保存企业当前承担的角色，人员表 [[cust_person_info]] 与关系表 [[cust_project_rel]] 分别在记录上标注 `company_type`。服务对接时，主表回答「这家企业是什么」，关联表回答「这条记录属于哪种角色语境」。

## 需求背景
企业可能同时具备多个角色，因此主表选择用 JSON 数组字符串承载；下游服务若按单值解析，会出现角色判断遗漏。关联表上的 `company_type` 需要能回落到主表的角色集合中，否则会出现不一致的角色标注。

## 版本演进
- v0.1（本页）：术语桥来自代码语义分析中三处同名字段的释义归纳。易混淆项：`cust_person_info.user_type`（人员用户类型）与 `sys_cust_user_rel.cust_type`（客户类型）属于不同维度。
---END FILE---

---FILE: concepts/user_type_role.md ---
---
type: concept
title: 用户类型 user_type
page_key: user_type_role
domain: 平台内部服务对接
status: draft
aliases:
  - 用户类型术语桥
  - 人员角色 admin/operator/guest
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
maps_to:
  - cust_person_info.user_type
field_targets:
  - cust_person_info.user_id
adjudication: >
  联系人记录通过 cust_person_info.user_type 区分 admin / operator / guest 三类
  用户，并通过 cust_person_info.user_id 关联系统用户；识别管理员与经办人分别使用
  cust_person_info.user_type = 'admin' 与 cust_person_info.user_type = 'operator'。
also_confused_with:
  - cust_person_info.company_type
  - sys_cust_user_rel.cust_type
---

「用户类型」把企业下的人员区分为 admin（管理员）、operator（经办人）、guest（访客）三类，落在 [[cust_person_info]] 的 `user_type` 上，并与 `user_id` 一起构成「企业联系人 → 系统用户」的桥。它是 [[admin_user]] 与 [[operator_user]] 两个口径的共同取值域。

## 需求背景
平台侧需要按用户类型裁剪可见功能与可执行动作：管理员承担企业确认等管理动作，经办人被纳入关系冻结管理。因此类型字段必须在建档时确定，并在人员列表查询中与有效性口径 [[valid_person]] 一起使用。

## 版本演进
- v0.1（本页）：术语桥来自代码语义分析中该字段的取值说明与两条口径谓词。易混淆项：`cust_person_info.company_type` 与 `sys_cust_user_rel.cust_type` 描述的是企业/客户维度，不是用户维度。
---END FILE---

---REVIEW: caliber | 经办人用户---
语义分析在 calibers 数组的「经办人用户」条目处被截断，仅取到 `name` 与 `predicate` 两个字段，`scope` 与 `evidence` 缺失。因此 calibers/operator_user.md 的 ground:caliber 块只写入这两个逐字值，未补写 scope/evidence；适用范围与代码出处需回溯原始分析后补齐。
---END REVIEW---

---REVIEW: rule | 规则页缺失---
本次语义分析（已截断）中未出现 rules 类条目，也没有带 reqdoc 双源证据的规则主张，因此未产出 rules/ 目录页面。若规则清单存在但被截断，请在补全后按「一条规则一页」重建；在补全前不应由表字段释义推导规则，以免产生无证据锚点。
---END REVIEW---

---REVIEW: table | 物理库名与字段类型---
全部表页的 `scope.databases` 暂记为 `unknown`：语义分析未给出物理库名，仅给出表名、字段名与中文释义（evidence=code）。同理，ground:table 中 `fields[].type` 一律留空、`dict` 仅在 `cust_person_info.status`（释义中明示 CustPersonStatusConstant）处填写。需要 DBA 或代码侧补充物理库名、字段类型与字典绑定后回填，方可从 draft 升级。
---END REVIEW---