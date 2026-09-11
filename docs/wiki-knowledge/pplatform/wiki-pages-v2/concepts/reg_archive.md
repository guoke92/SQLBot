---
type: concept
title: 建档
page_key: concepts/reg_archive
domain: 外部渠道与银行对接
status: draft
aliases:
  - reg
  - independentReg
  - dependentReg
  - companyArchiveOfTianma
  - channelArchive
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#reg
  - code:CustAccessApplication#companyArchiveOfTianma
  - code:ChannelArchiveProvider
  - code:ChannelCustArchiveOrchestrator
contract_version: "0.1"
maps_to: "cust_company_info 建档流程：CustAccessApplication#reg(isIndependent=true/false)、#companyArchiveOfTianma、以及 ChannelArchiveProvider#execute→ChannelCustArchiveOrchestrator"
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.certification_no
adjudication: boundary
boundary: "ChannelArchiveProvider 注释明确『Orchestrator 编排，不经过 reg / companyArchiveOfTianma』，是与标准建档并列的第三条入口；天马入站走 companyArchiveOfTianma，蚂蚁入站走 ChannelArchiveProvider"
also_confused_with:
  - 渠道建档（channelArchive）
  - 天马建档（companyArchiveOfTianma）
  - 运营中台建档（submitCust）
---

# 建档

## 业务定位

"建档"指在 `cust_company_info` 中创建/初始化一条企业记录并推动其进入建档状态机的动作。它在代码中对应三条并列入口：标准开放接口的 `reg(isIndependent=true/false)`（自主建档 `independentReg` / 挂靠建档 `dependentReg`）、天马入站 `companyArchiveOfTianma`、以及渠道统一入站 `ChannelArchiveProvider#execute → ChannelCustArchiveOrchestrator`。

## 需求背景

三条入口最终都写同一张企业表（[[tables/cust_company_info]]），因此需要共享同一套重复校验与状态口径：已建档拦截见 [[calibers/standard_api_registered]]，失败可复用见 [[calibers/build_fail_reusable]]，状态流转见 [[processes/cust_build_status_machine]]。

## 边界澄清

"渠道建档（channelArchive）"是一条独立入口，不与 `reg` / `companyArchiveOfTianma` 复用同一方法链：`ChannelArchiveProvider` 的注释明确『Orchestrator 编排，不经过 reg / companyArchiveOfTianma』。天马渠道入站走 `companyArchiveOfTianma`，蚂蚁渠道入站走 `ChannelArchiveProvider`。讨论建档行为时必须先区分入口，再看落库字段。

## 版本演进

- v0.1（本页首版）：术语映射与边界来自代码语义分析，尚无需求文档或变更单佐证。

## 关联页面

- 概念：[[concepts/channel]]、[[concepts/tianma_inbound_outbound]]、[[concepts/company_status_fields]]
- 口径：[[calibers/standard_api_registered]]、[[calibers/build_fail_reusable]]
- 流程：[[processes/cust_build_status_machine]]
- 规则：[[rules/channel_archive_unified_entry]]、[[rules/tianma_inbound_validation]]