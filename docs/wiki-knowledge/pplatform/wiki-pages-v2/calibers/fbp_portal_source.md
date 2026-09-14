---
type: caliber
title: 产融门户一证四步来源口径
page_key: fbp_portal_source
domain: CA证书认证
status: draft
aliases: [FBP_PORTAL, 门户一证四步来源]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationRealNameApplication.java
  - db:ca_certification_info
contract_version: "0.1"
belong: calibers
---

圈定门户 /cust-web/ca/realName/verify 入口落库的 CA 认证行。该来源由 initCertificationRow 建行，是"一证四步"的标准人机链路：协议告知、企业实名、被授权人公安二要素、意愿留痕、附件引用都需要在 [[submit_completeness|一证四步上送完整性口径]] 下齐备后才能上送。

## 需求背景

门户来源是三类来源中体量最大的一类，排查上送失败时通常以本口径先取样，再看 [[ca_submit_status]] 与 sign_platform_result。

## 版本演进

- v0：首次固化谓词与分布值。

```ground:caliber
name: 产融门户一证四步来源口径
predicate: "ca_certification_info.data_source = 'FBP_PORTAL'"
scope: 门户 /cust-web/ca/realName/verify 落库行（db 分布 865）
evidence: "code_path:CaCertificationRealNameApplication.java#initCertificationRow + db_dist:FBP_PORTAL=865"
```

关联页面：[[ca_certification_info]]、[[operation_platform_source]]、[[submit_completeness]]、[[enterprise_four_elements]]。