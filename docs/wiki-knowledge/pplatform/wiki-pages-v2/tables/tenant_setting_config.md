---
type: table
title: tenant_setting_config（租户配置表）
page_key: table.tenant_setting_config
domain: 平台内部服务对接
status: draft
aliases:
  - tenant_setting_config
  - 租户配置表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

租户级配置表，是平台内部服务对接的「参数中枢」：运营中台鉴权秘钥、SSO 渠道、门户与小程序配置、子账号授权书模板等均由此表驱动。

## 需求背景

对接运营中台时，sysChannel 取 sso_tenant_chanel，鉴权秘钥取 platform_secret_key，二者共同参与签名计算（见 [[rules/token_sign_md5]]）。生效租户的判定口径见 [[calibers/tenant_active_list]]，平台运营方取值口径见 [[calibers/platform_operator_value]]。运营中台企业 id 的对接字段见 [[concepts/platform_cust_id_bridge]]。

## 版本演进

v0：首次成页；仅收录语义分析中明确给出含义的配置项。

```ground:table
table: tenant_setting_config
columns:
  - field: db_tenant_code
    meaning: "租户数据编码，全局隔离键"
    evidence: code
  - field: enable / status
    meaning: "有效标志 / 生效标志（查询生效租户 activeList、'Y' 判定）"
    evidence: code
  - field: sso_tenant_chanel
    meaning: "SSO 渠道标识，作为 sysChannel 用于请求运营中台 token 与拉取互通系统列表"
    evidence: code
  - field: platform_secret_key
    meaning: "运营中台鉴权秘钥，参与 md5(secret+sysChannel+loginName)"
    evidence: code
  - field: platform_operator
    meaning: "平台运营方配置，JSON 数组，取值 PLATFORM（联易融）/TENANT（租户自身）"
    evidence: code
  - field: band_name
    meaning: "品牌名，用于同步给运营中台的 bizLabel"
    evidence: code
  - field: oper_auth_agreement
    meaning: "子账号授权书模板 id，未配置时回落 Nacos 值 operAuthAgreement"
    evidence: code
  - field: source / portal_flag / need_hfive / need_mp_wx
    meaning: "租户来源（PPLATFORM_SYSTEM）/ 门户开关 / 是否需要 H5 / 是否需要小程序微信配置，用于配置完备性校验"
    evidence: code
  - field: prd_mp_app_id / uat_mp_app_id / hfive_dev_domain / hfive_test_domain / hfive_uat_domain / hfive_prd_domain
    meaning: "小程序 appid 与环境域名，按 spring.profiles.active 取值"
    evidence: code
  - field: is_stack
    meaning: "是否堆栈/迁移标识 'Y'/'N'，决定 PlatMiniProgramTenantInfoDto 的 migratory/stock"
    evidence: code
```
## 关联表

- [[tenant_interworking_product]]：tenant_setting_config.code → tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config（ref-convention:TenantInterworkingProductDO.java，suggested）
- [[tenant_interworking_project]]：tenant_setting_config.code → tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config（ref-convention:TenantInterworkingProjectDO.java，suggested）
- [[tenant_product]]：tenant_setting_config.code → tenant_product.ref_tenant_product_tenant_setting_config（ref-convention:TenantProductDO.java，suggested）
