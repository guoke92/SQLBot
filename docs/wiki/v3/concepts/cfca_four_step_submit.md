---
type: concept
title: 一证四步提交
page_key: cfca_four_step_submit
belong: concepts
domain: ca_fee
status: draft
aliases: [CFCA一证四步, 开通CA采集]
maps_to: ca_certification_info.submit_status
field_targets: [ca_certification_info.submit_status]
sources: ['code_path:CaSubmitStatusEnum.java:12', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/ca证书收费.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_certification_info]
also_confused_with: [ca_open_status]
adjudication: boundary
---

# 一证四步提交

需求「cfca一证四步」落在 ca_certification_info。PENDING 采集，SUCCESS/FAIL 提交签章中台。
document_claim:cfca一证四步.md#25：V1.35 待办按企业+角色只生成一次，不是缴费订单，也不是 ca_status=NORMAL。

## 页面链接

- [[tables/ca_certification_info]]
- [[dicts/ca_certification_info__submit_status]]
- [[processes/ca_certification_info__submit_status]]
- [[concepts/ca_open_status]]
