---
type: process
title: 协议迁移拉取状态流转
page_key: agreement_migratory_pull_status
domain: 授权协议与电子授权
status: draft
aliases:
  - 协议拉取状态机
  - status 状态流转
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
belong: processes
---

该状态机描述 [[argeement_migratory_record]] 中 `status` 的推进方式：协议迁移任务取出待拉取记录（口径 [[agreement_migratory_pending_pull]]），成功落库后置 1（口径 [[agreement_migratory_pulled]]）；失败时 `pull_num+1` 等待下一轮重试，超过上限不再拉取，见 [[agreement_pull_retry_limit]]。客户端返回空协议集时直接标记完成，属于终态但无协议文件。

## 需求背景
存量协议不能一次性可靠拉齐，因此需要“待拉取 / 已拉取完成”两态 + 计数重试的组合，保证最终一致性同时避免无限重试。取数一律过滤 `enable='Y'`，见 [[agreement_migratory_enabled]]。

## 版本演进
`status` 列定义为 int 但代码写入的是字符串数字（`BooleanEnum.no/yes`），说明状态取值复用了布尔枚举的字典码而非独立枚举，属迁移初期的实现选择。

```ground:process
name: 协议迁移拉取状态
field: argeement_migratory_record.status
states:
  - value: "0"
    label: 待拉取
    source: db_dist
  - value: "1"
    label: 已拉取完成
    source: db_dist
transitions:
  - from: "0"
    event: 从业务系统拉取到协议并落库
    to: "1"
    evidence: "code_path:AgreementMigratoryService.java:setAgreement"
  - from: "0"
    event: 拉取失败，pull_num+1 后等待重试
    to: "0"
    evidence: "code_path:AgreementMigratoryService.java:updateAgreementPullNum"
  - from: "0"
    event: 客户端返回空协议集，标记为已完成
    to: "1"
    evidence: "code_path:AgreementMigratoryService.java:setAgreement（agreementDocs 为空分支）"
```