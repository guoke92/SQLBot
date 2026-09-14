---
type: concept
title: busiKey（影像业务键）
page_key: busi_key
domain: 文件/附件/媒体
status: draft
aliases: [业务键, 业务KEY]
oid: 1
scope:
  databases: [unknown]
sources: ["term_bridge:busiKey", "code:ProjectMediaFacade.java:uploadProjectConfigFiles", "code:CustMediaFacade.java:hasAuthorizationAgreementMedia"]
contract_version: "0.1"
maps_to: media_file.busi_key
adjudication: boundary
field_targets: [media_file.busi_key, media_file.user_busi_key]
also_confused_with: [userBusiKey]
belong: concepts
---
busiKey 通常为企业 id 或运营中台客户 id，用于按业务对象组织影像；userBusiKey 为联系人 id，用于区分操作人影像，二者是不同粒度的业务键，勿混用。

## 需求背景
本期语义分析未提供需求文档主张；本概念来自术语桥证据。

## 版本演进
v0 初版：确立 busiKey 与 userBusiKey 的边界；无 action=uncovered 的文档主张。

关联：[[media_file]]、[[media]]、[[catg_operator_filter]]、[[company_auth_media_existence]]。