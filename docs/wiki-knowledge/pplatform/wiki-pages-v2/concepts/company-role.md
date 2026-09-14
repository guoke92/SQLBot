---
type: concept
title: 企业角色
page_key: company-role
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
  - sys_role(系统权限角色，编码也常写作 accountNormal/accountGuest)
  - userType(落库 accountAdmin/accountNormal/accountGuest；Java 名 admin/operator/guest)
adjudication: boundary
boundary: 企业角色=企业身份维度；用户类型=企业内用户身份维度；sys_role=权限维度角色，三者不可混用。
field_targets:
  - cust_role_info.role_type
contract_version: "0.1"
belong: concepts
---

# 企业角色

「企业角色」（文档与代码中亦称客户角色、companyType、custCompanyType、roleType）描述**企业在业务网络中的身份**，取值是 CORE / SUPPLIER / DEALER / FINANCE / PLATFORM_OPERATOR_COMPANY / PROJECT_COMPANY / CORPORATION_COMPANY / FACTOR_COMPANY / CORE_MANAGER 一类的枚举名，落地在 [[tables/cust_role_info]] 的 role_type。与之相对，[[tables/platform_product_cust_role]] 的 company_type_code 是同一套枚举在**产品配置维度**上的表达（即 [[concepts/port]]）。

三个「角色」概念必须在文档中严格区分：企业角色（企业身份）、userType（用户在企业内的身份，落库 `accountAdmin`/`accountNormal`/`accountGuest`）、sys_role（权限角色，编码常与 dictKey 撞车）。三者分属不同维度，不可混用。

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