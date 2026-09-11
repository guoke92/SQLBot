---
type: table
title: ca_certification_info
page_key: table/ca_certification_info
domain: CA证书认证
status: draft
aliases: [CA认证信息表, CA认证行]
oid: 1
scope:
  databases: [unknown]
sources: [db, code]
contract_version: "0.1"
---

ca_certification_info 是 CA 证书认证（CFCA 一证四步）的主过程表。每一行代表某企业（cust_id）在某个数据日期（data_date）下、按是否总公司行（head_company_data）区分的一条认证登记记录，承载协议告知、实名核验、意愿认证、附件引用与签章中台请求响应原文等留痕，并用 submit_status 跟踪上送签章中台的进展。

行粒度上的幂等键是（cust_id, data_date, head_company_data, submit_status=PENDING），详见 [[calibers/ca_row_idempotent_key]] 与 [[rules/ca_row_idempotent]]。成功上送后的最新一行是下游查询的取值口径，见 [[calibers/latest_success_report]]。分公司场景下同一企业会同时存在 head_company_data=N 与 Y 两行，见 [[rules/branch_dual_row]]。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。表结构与字段语义由两类证据支撑：编码型字段（cust_type、op_type、data_source、head_company_data、submit_status）取值来自代码枚举，id、cust_id、enable 等来自库结构。四类核验留痕字段（enterprise_four_json、police_two_json、intent_sms_json、intent_h_face_json）分别对应 [[concepts/one_cert_four_steps]] 中的实名核验与意愿认证环节；file_refs_json 与 notify_agreement_json 是上送签章中台的前置材料。

## 版本演进

暂无文档化的版本演进证据。与提交行为相关的规则可从代码路径观察：提交前的完整性校验（[[rules/submit_sign_center_completeness]]）、data 字段超长截断（[[rules/data_field_truncate]]）、提交状态流转（[[processes/ca_certification_submit_status]]）。另一张表 [[tables/ca_cfca_upgrade_report]] 记录证书升级过程中的异常上报，与本表通过企业标识关联。

```ground:table
table: ca_certification_info
fields:
  - name: id
    meaning: 表主键
    evidence: db
  - name: cust_id
    meaning: 企业ID（产融企业主键）
    evidence: db
  - name: cust_type
    meaning: "客户类型：COMPANY（企业）/ PERSON（个人）"
    evidence: code
  - name: data_date
    meaning: 数据日期，格式 yyyyMMdd
    evidence: code
  - name: op_type
    meaning: "操作类型：INSERT（新增）/ UPDATE（更新）"
    evidence: code
  - name: batch_no
    meaning: "批次号/唯一流水号，格式 INC_yyyyMMddHHmmssSSS_6位hex"
    evidence: code
  - name: data_source
    meaning: "数据来源：CHANNEL_OPENAPI（渠道API）/ FBP_PORTAL（产融门户）/ OPERATION_PLATFORM（运营中台）"
    evidence: code
  - name: head_company_data
    meaning: "是否总公司行：Y（总公司行）/ N（分公司自身行）"
    evidence: code
  - name: submit_status
    meaning: "提交状态：PENDING（待提交）/ SUCCESS（提交成功）/ FAIL（提交失败）"
    evidence: code
  - name: enable
    meaning: "启用标识：Y（有效）/ N（无效）"
    evidence: db
  - name: notify_agreement_json
    meaning: 协议告知 JSON 数组，记录各协议签署留痕
    evidence: code
  - name: enterprise_four_json
    meaning: 企业四要素/三要素核验 JSON（verifyMethod=ENTERPRISE_FOUR 或 ENTERPRISE_THREE）
    evidence: code
  - name: police_two_json
    meaning: 公安二要素核验 JSON（verifyMethod=POLICE_TWO）
    evidence: code
  - name: intent_sms_json
    meaning: 短信意愿认证 JSON（authType=SMS_CODE）
    evidence: code
  - name: intent_h_face_json
    meaning: H5刷脸意愿认证 JSON（authType=H5_FACE）
    evidence: code
  - name: file_refs_json
    meaning: 附件引用 JSON，包含 embeddedFiles 列表（multipartField + path）
    evidence: code
  - name: sign_platform_result
    meaning: 签章中台请求与响应原文（含异常信息），完整保留
    evidence: code
  - name: submit_time
    meaning: 最近一次提交签章中台的时间
    evidence: code
```

相关页面：[[processes/ca_certification_submit_status]]、[[concepts/ca]]、[[concepts/data_source]]、[[concepts/head_company_data]]。