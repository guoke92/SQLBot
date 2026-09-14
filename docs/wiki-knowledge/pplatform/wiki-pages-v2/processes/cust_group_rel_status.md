---
type: process
title: 集团成员单位关系状态
page_key: cust_group_rel_status
domain: 集团关系
status: draft
aliases:
  - 集团关系状态机
  - 成员单位生效状态
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
  - code
contract_version: "0.1"
belong: processes
---

> (document_claim，未证实)

# 集团成员单位关系状态

`cust_group_rel.status` 描述成员单位关系的生效状态：新增/待办发出后为 `INEFFECTIVE`，成员单位签署协议 `accept` 后置 `EFFECTIVE`，拒绝 `reject` 后置 `REJECTED`；集团根企业的关系在建档成功场景下可直接落 `EFFECTIVE`。

## 需求背景

关系生效是集团业务的前置条件：查询成员只返回 `EFFECTIVE` 节点（[[effective_group_rel]]），根节点禁止再次签署或拒绝（[[root_group_no_operation]]），签署待办不可重复发送且异步容错（[[notice_no_duplicate]]、[[async_notice_tolerant]]），删除成员单位前需校验在途业务（[[member_remove_check_business]]）。

## 版本演进

- 新增关系（`addExistSubCustGroupRel`/`addNewSubCustGroupRel`/导入）与发送签署待办均落 `INEFFECTIVE`。
- `effectGroupRel` 外部回调可把 `INEFFECTIVE` 置为 `EFFECTIVE`。
- 需求文档主张“企业状态流转：待提交→审核中→已通过；已通过→已冻结/已注销”。**该主张为 document_claim，未证实**：代码侧仅见 `CustBuildStatusEnum` 的 BUILD_SUCCESS/CUST_BUILDING/BUILD_FAIL/CUST_CHANGE 被引用，冻结/注销流转的枚举与写值点未出现在给出的文件中。

```ground:process
name: 集团成员单位关系状态
field: cust_group_rel.status
states:
  - value: INEFFECTIVE
    label: 未生效
    source: code_enum
  - value: EFFECTIVE
    label: 已生效
    source: db_dist
  - value: REJECTED
    label: 已拒绝
    source: code_enum
transitions:
  - from: null
    event: 新增成员单位关系（addExistSubCustGroupRel/addNewSubCustGroupRel/导入）
    to: INEFFECTIVE
    evidence: code_path:CustGroupRelApplication.java:addExistSubCustGroupRel
  - from: null
    event: 发送成员单位签署待办 sendCustGroupRelNotice
    to: INEFFECTIVE
    evidence: code_path:CustGroupLicenseApplication.java:sendCustGroupRelNotice
  - from: INEFFECTIVE
    event: 成员单位签署协议 accept
    to: EFFECTIVE
    evidence: code_path:CustGroupLicenseApplication.java:accept
  - from: INEFFECTIVE
    event: 拒绝签署协议 reject
    to: REJECTED
    evidence: code_path:CustGroupLicenseApplication.java:reject
  - from: null
    event: 新增集团根企业且企业已建档成功 BUILD_SUCCESS
    to: EFFECTIVE
    evidence: code_path:CustGroupRelApplication.java:addExistRootGroupRel
  - from: INEFFECTIVE
    event: effectGroupRel 外部回调置为已生效
    to: EFFECTIVE
    evidence: code_path:CustGroupRelApplication.java:effectGroupRel
```