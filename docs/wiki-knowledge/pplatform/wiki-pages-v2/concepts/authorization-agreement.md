---
type: concept
title: 授权书
page_key: concept.authorization_agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - 授权确认书
  - 授权协议
  - 客户管理员授权认证
  - 企业授权书
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:authorization_agreement
contract_version: "0.1"
maps_to: "authorization_agreement（表注释：授权确认书表）——记录企业管理员是否完成平台/产品级授权，authed_status=Y 视为已授权"
field_targets:
  - authorization_agreement.authed_status
  - authorization_agreement.platform_product_code
  - authorization_agreement.cust_manager_id
adjudication: boundary
also_confused_with:
  - 线下电子授权书（OfflineElectronicAuth 协议文件）
  - 平台协议文本（用户协议/隐私政策）
boundary: "authorization_agreement 是「谁授过权」的关系记录；线下电子授权书是「授权书这一份文件」的生成与签章，二者通过 cust_id 关联但生命周期不同"
---

「授权书」在业务对话中指关系事实而非文件：它回答「某管理员是否已代表某企业完成授权」，落在 [[tables/authorization_agreement]]，以 `authed_status='Y'` 表达已授权，判定口径见 [[calibers/platform-level-authed]]，状态流转见 [[processes/authorization-agreement-authed-status]]。

最常见的混淆是把「授权书」等同于 [[concepts/offline-electronic-auth]]（一份被签署并上传影像的合同文件），或者等同于 [[concepts/agreement]]（用户协议/隐私政策这类平台协议文本）。二者的边界是：本术语不含文件落库、不含签署模式，只有授权关系与生效标志；文件的生命周期、开关控制与签署动作在电子授权书术语下描述。

## 需求背景
企业授权按人（userid）维度判定，同一自然人的多企业角色只需一份平台级授权；为避免与「授权书文件」「平台协议文本」混用，需要把关系记录这一层语义单独命名。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。