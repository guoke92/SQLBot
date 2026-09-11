---
type: concept
title: 事件监听 / onEvent
page_key: concepts/event-listener-onevent
domain: 平台事件监听与同步
status: draft
aliases:
  - IPlatListener.onEvent
  - PlatFormCustEventListener.onEvent
  - IPlatListener<T extends IFlatEvent>
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:lowcode-pplatform-client/.../base/IPlatListener.java
  - code:PlatTenantEventListener.java
  - code:PlatProjectEventListener.java
  - code:PlatProductEventListener.java
  - code:PlatFormCustEventListener.java
  - code:CustSyncEventProvider.java:onEvent
  - "reqdoc:事件回调：平台触发事件 → 构造 FbpReq<T> → 回调 IPlatListener.onEvent"
  - "reqdoc:监听器子接口：租户、项目、产品、角色、协议等扩展监听器（PlatTenantEventListener/PlatProjectEventListener/PlatProductEventListener等）均继承基接口"
  - "reqdoc:PlatProjectEventListener 提供 queryProject/importProject/queryProjectLandTime 等查询与导入契约"
  - "reqdoc:客户域监听器 PlatFormCustEventListener 覆盖企业信息同步/状态同步/经办人/在途校验/站内信等（含默认实现的 syncCustManager/syncDeleteCustInfo）"
  - "reqdoc:回调链路：平台触发事件 → 构造 FbpReq<T> → 回调 IPlatListener.onEvent → 业务系统消费并记录处理结果"
contract_version: "0.1"
maps_to: "产融平台→业务系统的数据变动回调契约（业务系统实现子接口）"
adjudication:
  kind: boundary
  boundary: "两者方向相反：IPlatListener/PlatFormCustEventListener 是产融侧对外提供的回调接口（@Api 信息变动事件），由业务系统实现；CustSyncEventProvider.onEvent 是产融侧实现运营中台 CustEventListener 的入站回调，同名字段但属对立方向。"
also_confused_with:
  - CustSyncEventProvider.onEvent（运营中台→产融平台的回调入口）
---

> 本页 ## 版本演进 收录了未在代码层证实的文档主张（document_claim，未证实）。

「事件监听 / onEvent」是一个被同名复用的契约概念，指代产融侧对外提供的、由业务系统实现的数据变动回调接口族（IPlatListener 及其扩展子接口），与产融侧作为消费方的入站回调 `CustSyncEventProvider.onEvent` 方向相反。二者同名不同向，是阅读同步链路时最容易混淆的一处。

## 需求背景
回调链路为：平台触发事件 → 构造 `FbpReq<T>` → 回调 `IPlatListener.onEvent` → 业务系统消费并记录处理结果。子接口按域扩展，租户、项目、产品、角色、协议等扩展监听器（PlatTenantEventListener / PlatProjectEventListener / PlatProductEventListener 等）均继承基接口；其中 PlatProjectEventListener 提供 queryProject / importProject / queryProjectLandTime 等查询与导入契约。客户域的 PlatFormCustEventListener 覆盖企业信息同步 / 状态同步 / 经办人 / 在途校验 / 站内信等，并含默认实现的 syncCustManager / syncDeleteCustInfo。以上四项 reqdoc 主张均已由代码层证实，锚点证据（code_path + reqdoc:slug）记于 frontmatter sources。

## 版本演进
- v0 契约：产融侧接口族以「基接口 + 分域子接口」组织；客户域实现对象见 [[concepts/cust-build]] 与 [[processes/cust-company-build-status]] 的驱动链路。
- 接口矩阵：PlatFormAmsProvider.addEnterpriseContact（AMS 联系人同步）/ PlatFormTenantProvider.queryTenant·syncProject / PlatFormAgreementProvider.syncAgreementDoc（document_claim，未证实）。
- MigratoryPointService 提供 push（异步）与 call（同步）接口用于迁移点数据推送（document_claim，未证实）。

---REVIEW: concept | 事件监听 / onEvent---
1. 本页为 concept 页，按 v0 §3.9 不设 ground 块；reqdoc_claims 中 action=anchor 的双源证据写入 frontmatter `sources`（code_path + reqdoc:slug 形式），如与团队约定的锚点承载方式不一致请统一。
2. PlatFormCustEventListener 的默认实现方法（syncCustManager/syncDeleteCustInfo）与 `CustSyncEventProvider.syncOperatorUser` 是否职责重叠，语义分析未给结论。
3. 两条 action=review 的接口主张（Provider 矩阵、MigratoryPointService）无代码证据，已按规约仅置于 ## 版本演进。
---END REVIEW---