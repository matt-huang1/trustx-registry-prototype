window.__REGISTRY__ = [
  {
    "agent": {
      "description": "An internal document summarisation assistant with read-only access to the company's internal document store. It produces draft summaries of internal documents that are always reviewed by a human before use. It cannot take any action, call external tools, or modify any record.",
      "slug": "internal-document-summarisation-assistant"
    },
    "autonomy_level": 1,
    "challenge": {
      "flagged": false,
      "iterations": 1,
      "notes": [
        "Curated, human-authored reference entry; scores reasoned by hand against the ARC 12-dimension model. No automated challenger pass was run.",
        "Tier-weighting note: under the knowledge_assistant profile the tier is weighted off autonomy, action_authority, blast_radius, persistence and reversibility (all Tier 1 here). Under the recommended_default all-12 profile, data_sensitivity=2 (internal documents) would lift this entry to medium — see docs/adr/0012-*.md on the tier-weighting divergence."
      ]
    },
    "dimensions": {
      "action_authority": {
        "evidence": [
          "It cannot take any action, call external tools, or modify any record"
        ],
        "rationale": "Read-only / advisory: it cannot act, call tools, or change any record.",
        "score": 1
      },
      "aggregation_risk": {
        "evidence": [
          "produces draft summaries of internal documents"
        ],
        "rationale": "No aggregation: summarises one document at a time; no cross-document inference.",
        "score": 1
      },
      "autonomy": {
        "evidence": [
          "draft summaries ... always reviewed by a human before use",
          "It cannot take any action"
        ],
        "rationale": "Human-in-the-loop: every draft summary is reviewed by a human before use.",
        "score": 1
      },
      "blast_radius": {
        "evidence": [
          "draft summaries ... always reviewed by a human before use"
        ],
        "rationale": "Single user: a draft goes to the one human who reviews it before use.",
        "score": 1
      },
      "control_authority": {
        "evidence": [
          "It cannot take any action, call external tools, or modify any record"
        ],
        "rationale": "Standalone: supervises or orchestrates no other agents.",
        "score": 1
      },
      "data_egress_paths": {
        "evidence": [
          "draft summaries ... always reviewed by a human before use",
          "cannot ... call external tools"
        ],
        "rationale": "Constrained outputs: the only output is a draft handed to a human reviewer.",
        "score": 1
      },
      "data_sensitivity": {
        "evidence": [
          "read-only access to the company's internal document store",
          "draft summaries of internal documents"
        ],
        "rationale": "Internal / confidential: reads internal business documents, not public or regulated data.",
        "score": 2
      },
      "decision_scope": {
        "evidence": [
          "produces draft summaries of internal documents"
        ],
        "rationale": "Local decisions: each summary concerns one document; nothing wider is decided.",
        "score": 1
      },
      "persistence": {
        "evidence": [
          "produces draft summaries of internal documents"
        ],
        "rationale": "Stateless: summarises per document; no session or long-term memory described.",
        "score": 1
      },
      "reversibility": {
        "evidence": [
          "draft summaries ... always reviewed by a human before use"
        ],
        "rationale": "Fully reversible: an unused draft can simply be discarded.",
        "score": 1
      },
      "system_reach": {
        "evidence": [
          "read-only access to the company's internal document store"
        ],
        "rationale": "Single system: read-only access to the internal document store only.",
        "score": 1
      },
      "temporal_coupling": {
        "evidence": [
          "produces draft summaries of internal documents"
        ],
        "rationale": "Isolated actions: one summary per request, no chained workflow or loop.",
        "score": 1
      }
    },
    "provenance": {
      "approved_by": "@matt-huang1",
      "submitted_by": "curated-reference",
      "timestamp": "2026-07-09T00:00:00+00:00"
    },
    "risk_tier": "low",
    "system_type": "knowledge_assistant",
    "tier_derivation": {
      "autonomy_level_driven": false,
      "driving_dimensions": [],
      "profile": "knowledge_assistant",
      "tier_dimensions": [
        "autonomy",
        "action_authority",
        "blast_radius",
        "persistence",
        "reversibility"
      ]
    }
  },
  {
    "agent": {
      "description": "Read-only question-answering assistant over public and approved internal reference material. Advisory only; takes no actions.",
      "registry_id": "RAI-OPEN-0002",
      "slug": "internal-knowledge-assistant",
      "title": "Internal Knowledge Assistant"
    },
    "autonomy_level": 1,
    "challenge": {
      "flagged": false,
      "iterations": 1,
      "notes": [
        "Adopted seed entry from the RAI ARC reference registry; the published per-dimension tiers are kept verbatim and the published overall tier (Tier 1) reproduces under the knowledge_assistant tier-weighting profile. No automated challenger pass was run."
      ]
    },
    "dimensions": {
      "action_authority": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "Read-only / advisory",
        "score": 1
      },
      "aggregation_risk": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "No aggregation",
        "score": 1
      },
      "autonomy": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "Human-in-the-loop",
        "score": 1
      },
      "blast_radius": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "Single user",
        "score": 1
      },
      "control_authority": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "Standalone",
        "score": 1
      },
      "data_egress_paths": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "Constrained outputs",
        "score": 1
      },
      "data_sensitivity": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "Public / non-sensitive",
        "score": 1
      },
      "decision_scope": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "Local decisions",
        "score": 1
      },
      "persistence": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "Stateless",
        "score": 1
      },
      "reversibility": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "Fully reversible",
        "score": 1
      },
      "system_reach": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "Single system",
        "score": 1
      },
      "temporal_coupling": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0002 v1.0, 2026-05-18)."
        ],
        "rationale": "Isolated actions",
        "score": 1
      }
    },
    "provenance": {
      "approved_by": "@matt-huang1",
      "submitted_by": "RAI-ARC-reference",
      "timestamp": "2026-07-09T00:00:00+00:00"
    },
    "risk_tier": "low",
    "system_type": "knowledge_assistant",
    "tier_derivation": {
      "autonomy_level_driven": false,
      "driving_dimensions": [],
      "profile": "knowledge_assistant",
      "tier_dimensions": [
        "autonomy",
        "action_authority",
        "blast_radius",
        "persistence",
        "reversibility"
      ]
    }
  },
  {
    "agent": {
      "description": "Classifies and routes incoming invoices across internal systems and prepares actions for human approval. Maintains a full audit trail.",
      "registry_id": "RAI-OPEN-0003",
      "slug": "invoice-triage-agent",
      "title": "Invoice Triage Agent"
    },
    "autonomy_level": 2,
    "challenge": {
      "flagged": false,
      "iterations": 1,
      "notes": [
        "Adopted seed entry from the RAI ARC reference registry; the published per-dimension tiers are kept verbatim and the published overall tier (Tier 2) reproduces under the tool_using_agent tier-weighting profile. No automated challenger pass was run."
      ]
    },
    "dimensions": {
      "action_authority": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Create or modify",
        "score": 2
      },
      "aggregation_risk": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Limited",
        "score": 2
      },
      "autonomy": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Human-on-the-loop",
        "score": 2
      },
      "blast_radius": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Team / department",
        "score": 2
      },
      "control_authority": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Standalone",
        "score": 1
      },
      "data_egress_paths": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Multiple controlled",
        "score": 2
      },
      "data_sensitivity": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Internal / confidential",
        "score": 2
      },
      "decision_scope": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Domain-level",
        "score": 2
      },
      "persistence": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Session-based",
        "score": 2
      },
      "reversibility": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Partially reversible",
        "score": 2
      },
      "system_reach": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Multiple internal",
        "score": 2
      },
      "temporal_coupling": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0003 v1.1, 2026-05-24)."
        ],
        "rationale": "Chained workflows",
        "score": 2
      }
    },
    "provenance": {
      "approved_by": "@matt-huang1",
      "submitted_by": "RAI-ARC-reference",
      "timestamp": "2026-07-09T00:00:00+00:00"
    },
    "risk_tier": "medium",
    "system_type": "tool_using_agent",
    "tier_derivation": {
      "autonomy_level_driven": false,
      "driving_dimensions": [
        "autonomy",
        "action_authority",
        "blast_radius",
        "persistence",
        "reversibility"
      ],
      "profile": "tool_using_agent",
      "tier_dimensions": [
        "autonomy",
        "action_authority",
        "blast_radius",
        "persistence",
        "reversibility"
      ]
    }
  },
  {
    "agent": {
      "description": "A KYC onboarding triage agent that reads sensitive customer personal data (PII) — identity documents, addresses, and dates of birth — to draft an onboarding risk recommendation for a human compliance officer. It cannot approve onboarding, open accounts, or act autonomously; a human officer makes every decision.",
      "slug": "kyc-onboarding-triage-agent"
    },
    "autonomy_level": 1,
    "challenge": {
      "flagged": false,
      "iterations": 1,
      "notes": [
        "Curated, human-authored reference entry; scores reasoned by hand against the ARC 12-dimension model. No automated challenger pass was run.",
        "Tier-weighting note: under the tool_using_agent profile the tier is weighted off autonomy, action_authority, blast_radius, persistence and reversibility; blast_radius=2 drives Tier 2 (medium). data_sensitivity=3 (regulated identity PII) is scored but does NOT drive the tier under this profile — under the recommended_default all-12 profile it would force Tier 3 (high). This entry is the concrete case for the divergence recorded in docs/adr/0012-*.md."
      ]
    },
    "dimensions": {
      "action_authority": {
        "evidence": [
          "It cannot approve onboarding, open accounts, or act autonomously"
        ],
        "rationale": "Read-only / advisory: it drafts a recommendation and can take no action itself.",
        "score": 1
      },
      "aggregation_risk": {
        "evidence": [
          "identity documents, addresses, and dates of birth"
        ],
        "rationale": "Limited: combines identity attributes into a per-applicant risk recommendation.",
        "score": 2
      },
      "autonomy": {
        "evidence": [
          "a human officer makes every decision",
          "It cannot approve onboarding, open accounts, or act autonomously"
        ],
        "rationale": "Human-in-the-loop: a human compliance officer makes every decision.",
        "score": 1
      },
      "blast_radius": {
        "evidence": [
          "draft an onboarding risk recommendation for a human compliance officer"
        ],
        "rationale": "Team / department: its recommendations steer the compliance team's onboarding decisions across every applicant it triages.",
        "score": 2
      },
      "control_authority": {
        "evidence": [
          "It cannot approve onboarding, open accounts, or act autonomously"
        ],
        "rationale": "Standalone: supervises or orchestrates no other agents.",
        "score": 1
      },
      "data_egress_paths": {
        "evidence": [
          "draft an onboarding risk recommendation for a human compliance officer"
        ],
        "rationale": "Constrained outputs: the only output is a recommendation to the officer.",
        "score": 1
      },
      "data_sensitivity": {
        "evidence": [
          "reads sensitive customer personal data (PII)",
          "identity documents, addresses, and dates of birth"
        ],
        "rationale": "Regulated / crown-jewel: handles regulated identity PII — identity documents, addresses, dates of birth.",
        "score": 3
      },
      "decision_scope": {
        "evidence": [
          "draft an onboarding risk recommendation for a human compliance officer"
        ],
        "rationale": "Domain-level: its recommendations shape the onboarding/KYC compliance domain.",
        "score": 2
      },
      "persistence": {
        "evidence": [
          "draft an onboarding risk recommendation"
        ],
        "rationale": "Stateless: triages per applicant; no session or long-term memory described.",
        "score": 1
      },
      "reversibility": {
        "evidence": [
          "a human officer makes every decision"
        ],
        "rationale": "Fully reversible: a recommendation binds nothing — the human officer decides.",
        "score": 1
      },
      "system_reach": {
        "evidence": [
          "reads sensitive customer personal data (PII)"
        ],
        "rationale": "Single system: reads the customer PII presented for onboarding; no other systems.",
        "score": 1
      },
      "temporal_coupling": {
        "evidence": [
          "draft an onboarding risk recommendation"
        ],
        "rationale": "Isolated actions: one applicant triaged per request; no chained workflow described.",
        "score": 1
      }
    },
    "provenance": {
      "approved_by": "@matt-huang1",
      "submitted_by": "curated-reference",
      "timestamp": "2026-07-09T00:00:00+00:00"
    },
    "risk_tier": "medium",
    "system_type": "tool_using_agent",
    "tier_derivation": {
      "autonomy_level_driven": false,
      "driving_dimensions": [
        "blast_radius"
      ],
      "profile": "tool_using_agent",
      "tier_dimensions": [
        "autonomy",
        "action_authority",
        "blast_radius",
        "persistence",
        "reversibility"
      ]
    }
  },
  {
    "agent": {
      "description": "A payments initiation agent that can initiate payments and transfer funds through bank payment-rail APIs (ACH and wire) on behalf of the finance team, with only limited human oversight of individual transactions.",
      "slug": "payments-initiation-agent"
    },
    "autonomy_level": 2,
    "challenge": {
      "flagged": true,
      "iterations": 1,
      "notes": [
        "Curated, human-authored reference entry; scores reasoned by hand against the ARC 12-dimension model. No automated challenger pass was run.",
        "Deterministic rule: description contains money-movement language (initiate payments / transfer funds / ACH), so action_authority is pinned to 3 (\"Execute transactions\"). Under worst-case-wins this alone forces Tier 3 (high)."
      ]
    },
    "dimensions": {
      "action_authority": {
        "evidence": [
          "can initiate payments and transfer funds through bank payment-rail APIs (ACH and wire)",
          "deterministic-rule: money-movement capability detected in description"
        ],
        "rationale": "Execute transactions: initiates payments and moves funds — Tier 3 on the merits, and independently pinned to 3 by the deterministic money-movement rule.",
        "score": 3
      },
      "aggregation_risk": {
        "evidence": [
          "individual transactions"
        ],
        "rationale": "No aggregation: processes individual payment instructions only.",
        "score": 1
      },
      "autonomy": {
        "evidence": [
          "with only limited human oversight of individual transactions"
        ],
        "rationale": "Human-on-the-loop: transactions execute with only limited human oversight.",
        "score": 2
      },
      "blast_radius": {
        "evidence": [
          "on behalf of the finance team"
        ],
        "rationale": "Team / department: mis-sent payments hit the finance team's funds and vendors.",
        "score": 2
      },
      "control_authority": {
        "evidence": [
          "A payments initiation agent"
        ],
        "rationale": "Standalone: supervises or orchestrates no other agents.",
        "score": 1
      },
      "data_egress_paths": {
        "evidence": [
          "through bank payment-rail APIs (ACH and wire)"
        ],
        "rationale": "External egress: pushes payment instructions out to external banking rails.",
        "score": 3
      },
      "data_sensitivity": {
        "evidence": [
          "through bank payment-rail APIs (ACH and wire)"
        ],
        "rationale": "Regulated / crown-jewel: handles bank-account and payment-rail data.",
        "score": 3
      },
      "decision_scope": {
        "evidence": [
          "on behalf of the finance team"
        ],
        "rationale": "Domain-level: decides within the finance/payments domain on the team's behalf.",
        "score": 2
      },
      "persistence": {
        "evidence": [
          "limited human oversight of individual transactions"
        ],
        "rationale": "Stateless: initiates per transaction; no session or long-term memory described.",
        "score": 1
      },
      "reversibility": {
        "evidence": [
          "bank payment-rail APIs (ACH and wire)"
        ],
        "rationale": "Irreversible: a sent wire cannot be recalled and ACH recalls are best-effort.",
        "score": 3
      },
      "system_reach": {
        "evidence": [
          "through bank payment-rail APIs (ACH and wire)"
        ],
        "rationale": "Cross-domain / third-party: acts through external bank payment-rail APIs.",
        "score": 3
      },
      "temporal_coupling": {
        "evidence": [
          "initiate payments and transfer funds"
        ],
        "rationale": "Isolated actions: each payment initiation stands alone; no loops described.",
        "score": 1
      }
    },
    "provenance": {
      "approved_by": "@matt-huang1",
      "submitted_by": "curated-reference",
      "timestamp": "2026-07-09T00:00:00+00:00"
    },
    "risk_tier": "high",
    "system_type": "transaction_commerce_agent",
    "tier_derivation": {
      "autonomy_level_driven": false,
      "driving_dimensions": [
        "action_authority",
        "system_reach",
        "reversibility",
        "data_sensitivity",
        "data_egress_paths"
      ],
      "profile": "transaction_commerce_agent",
      "tier_dimensions": [
        "autonomy",
        "decision_scope",
        "temporal_coupling",
        "action_authority",
        "system_reach",
        "blast_radius",
        "persistence",
        "reversibility",
        "control_authority",
        "data_sensitivity",
        "aggregation_risk",
        "data_egress_paths"
      ]
    }
  },
  {
    "agent": {
      "description": "Detects buying and payment intent, recommends allowed financial actions, and prepares transactions for human approval. Acts as a trust boundary between consumer AI assistants and payment systems.",
      "registry_id": "RAI-OPEN-0001",
      "slug": "trustwise-commerce-agent",
      "title": "TrustWise Commerce Agent"
    },
    "autonomy_level": 2,
    "challenge": {
      "flagged": false,
      "iterations": 1,
      "notes": [
        "Adopted seed entry from the RAI ARC reference registry; the published per-dimension tiers are kept verbatim and the published overall tier (Tier 3) reproduces under the transaction_commerce_agent tier-weighting profile. No automated challenger pass was run."
      ]
    },
    "dimensions": {
      "action_authority": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Execute transactions",
        "score": 3
      },
      "aggregation_risk": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Limited",
        "score": 2
      },
      "autonomy": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Human-on-the-loop",
        "score": 2
      },
      "blast_radius": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Team / department",
        "score": 2
      },
      "control_authority": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Supervises agents",
        "score": 2
      },
      "data_egress_paths": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Multiple controlled",
        "score": 2
      },
      "data_sensitivity": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Regulated / crown-jewel",
        "score": 3
      },
      "decision_scope": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Domain-level",
        "score": 2
      },
      "persistence": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Session-based",
        "score": 2
      },
      "reversibility": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Irreversible",
        "score": 3
      },
      "system_reach": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Cross-domain / third-party",
        "score": 3
      },
      "temporal_coupling": {
        "evidence": [
          "Adopted from the published ARC reference assessment (RAI-OPEN-0001 v1.2, 2026-06-02)."
        ],
        "rationale": "Chained workflows",
        "score": 2
      }
    },
    "provenance": {
      "approved_by": "@matt-huang1",
      "submitted_by": "RAI-ARC-reference",
      "timestamp": "2026-07-09T00:00:00+00:00"
    },
    "risk_tier": "high",
    "system_type": "transaction_commerce_agent",
    "tier_derivation": {
      "autonomy_level_driven": false,
      "driving_dimensions": [
        "action_authority",
        "system_reach",
        "reversibility",
        "data_sensitivity"
      ],
      "profile": "transaction_commerce_agent",
      "tier_dimensions": [
        "autonomy",
        "decision_scope",
        "temporal_coupling",
        "action_authority",
        "system_reach",
        "blast_radius",
        "persistence",
        "reversibility",
        "control_authority",
        "data_sensitivity",
        "aggregation_risk",
        "data_egress_paths"
      ]
    }
  }
];
