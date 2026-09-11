---
type: concept
title: 企业状态三字段
page_key: concepts/company_status_fields
domain: 外部渠道与银行对接
status: draft
aliases:
  - custStatus
  - custBuildStatus
  - checkStatus
  - cust_status / cust_build_status / check_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustStatusConstant
  - code:CustBuildStatusEnum
  - code:OperApiConstants.CheckStatus
contract_version: "0.1"
maps_to: "cust_company_info 的三个独立状态列：cust_status（客户状态 ADD/CHANGE/WRITEOFF）、cust_build_status（建档/认证状态 INIT/BUILDING/BUILD_SUCCESS/BUILD_FAIL/CUST_CONFIRM_AWAIT）、check_status（审核状态 CUST_CHECK_*）"
field_targets:
  - cust_company_info.cust_status
  - cust_company_info.cust_build_status
  - cust_company_info.check_status
adjudication: boundary
boundary: "对外查询接口不直接回传库内枚举，而是 CheckStatus→RegStatus 映射后再返回；CUSTS001~CUSTS005 属于开放接口协议值，不能当库存值使用"
also_confused_with:
  - RegStatus（对外编码 CUSTS001~CUSTS005/CUST404）
  - CompanyUserStatus（AUTH0001/AUTH0003）
---

# 企业状态三字段

## 业务定位

`cust_company_info` 上有三个互相独立的状态列，分别承载三台状态机：`cust_status`（企业生命周期：ADD / CHANGE / WRITEOFF，见 [[processes/cust_status_machine]]）、`cust_build_status`（建档/认证：INIT / BUILDING / CUST_CONFIRM_AWAIT / BUILD_SUCCESS / BUILD_FAIL，见 [[processes/cust_build_status_machine]]）、`check_status`（审核：CUST_CHECK_*，见 [[processes/cust_check_status_machine]]）。

## 需求背景

外部渠道对接需要同时回答三个不同问题："这家企业还在不在（未注销）"、"这家企业的建档有没有做完"、"这家企业的资料审核到哪一步了"。三个问题各自有独立的过滤与拦截口径（[[calibers/non_writeoff]]、[[calibers/build_fail_reusable]]、[[calibers/standard_api_registered]]），因此必须是三列而非一个复合状态，三者之间不存在强制的同步迁移关系。

## 边界澄清

对外查询接口不直接回传库内枚举：先做 `CheckStatus → RegStatus` 映射，再返回 `CUSTS001~CUSTS005` / `CUST404`。因此 `CUSTS*` 是开放接口协议值，不能当作库存值参与 SQL 过滤。同样地 `CompanyUserStatus`（`AUTH0001` / `AUTH0003`）描述的是用户侧状态，不属于本表三字段体系。

## 版本演进

- v0.1（本页首版）：术语映射与边界来自代码语义分析，尚无需求文档或变更单佐证。

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 流程：[[processes/cust_status_machine]]、[[processes/cust_build_status_machine]]、[[processes/cust_check_status_machine]]
- 口径：[[calibers/non_writeoff]]、[[calibers/standard_api_registered]]
- 概念：[[concepts/reg_archive]]