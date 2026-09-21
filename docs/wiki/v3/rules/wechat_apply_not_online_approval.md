---
type: rule
title: 企微立项单不是上线审批单
page_key: wechat_apply_not_online_approval
belong: rules
domain: remaining
status: draft
field_targets: [wechat_project_approval_apply.sp_no, tenant_project_approval.wf_status]
sources: ['code_path:WechatProjectApprovalApplication.java:148']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [wechat_project_approval_apply, tenant_project_approval]
---

# 企微立项单不是上线审批单

企微审批在 wechat_project_approval_apply。项目上线审批在 tenant_project_approval。不要互代。

```ground:rule
rule: 企微立项单不是上线审批单
field_targets: [wechat_project_approval_apply.sp_no, tenant_project_approval.wf_status]
impact: query_constraint
content: 企微审批在 wechat_project_approval_apply。项目上线审批在 tenant_project_approval。不要互代。
evidence: code_path:WechatProjectApprovalApplication.java:148
```

## 页面链接

- [[tables/tenant_project_approval]]
- [[tables/wechat_project_approval_apply]]
- [[dicts/tenant_project_approval__wf_status]]
- [[processes/tenant_project_approval__wf_status]]
