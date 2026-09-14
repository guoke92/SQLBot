---
type: caliber
title: 运营中台推送来源口径
page_key: operation_platform_source
domain: CA证书认证
status: draft
aliases: [OPERATION_PLATFORM, 运营中台来源]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaActivationApplication.java
  - db:ca_certification_info
contract_version: "0.1"
belong: calibers
---

用于圈定由运营中台 notifyActivateCa 主动通知触发的 CA 落库行。该来源的行由 persistActivateData 写入，且在分公司场景下会并行上送 N/Y 两行（与 [[confirm_submit_own_row_only]] 描述的协议确认链路不同）。统计与排障都应以本口径为基础，避免与门户来源混淆。

## 需求背景

运营推送链路标 @Transactional(NOT_SUPPORTED)，中台调用在事务外（见 [[sign_center_call_outside_tx]]），因此该来源的行出现"已建行未上送"属于预期内的中间态。

## 版本演进

- v0：首次固化谓词与分布值。

```ground:caliber
name: 运营中台推送来源口径
predicate: "ca_certification_info.data_source = 'OPERATION_PLATFORM'"
scope: 运营中台 notifyActivateCa 主动通知触发的 CA 落库行（db 分布 453）
evidence: "code_path:CaActivationApplication.java#persistActivateData + db_dist:OPERATION_PLATFORM=453"
```

关联页面：[[ca_certification_info]]、[[fbp_portal_source]]、[[channel_openapi_source]]、[[ca_submit_status]]。