window.__ARC_META__ = {
  "autonomy_level_defs": {
    "1": "Level 1 — Human-in-the-loop. A human reviews and approves each consequential action before it executes.",
    "2": "Level 2 — Checkpoint approval. A human approves at defined checkpoints; routine steps proceed without per-action review.",
    "3": "Level 3 — Human-on-the-loop. The system acts within set bounds while a human monitors and can intervene or roll back.",
    "4": "Level 4 — Supervised autonomy. The system plans and acts within set bounds; human oversight is exception-based rather than continuous.",
    "5": "Level 5 — Fully autonomous. Plans and executes without per-action review; oversight is by monitoring, audit, and shutdown controls."
  },
  "dimensions": [
    {
      "group": "autonomy_decision_power",
      "id": "autonomy",
      "name": "Autonomy",
      "tiers": {
        "1": "Human-in-the-loop",
        "2": "Human-on-the-loop",
        "3": "Fully autonomous"
      }
    },
    {
      "group": "autonomy_decision_power",
      "id": "decision_scope",
      "name": "Decision Scope",
      "tiers": {
        "1": "Local decisions",
        "2": "Domain-level",
        "3": "Enterprise-wide"
      }
    },
    {
      "group": "autonomy_decision_power",
      "id": "temporal_coupling",
      "name": "Temporal Coupling",
      "tiers": {
        "1": "Isolated actions",
        "2": "Chained workflows",
        "3": "Continuous loops"
      }
    },
    {
      "group": "action_authority_reach",
      "id": "action_authority",
      "name": "Action Authority",
      "tiers": {
        "1": "Read-only / advisory",
        "2": "Create or modify",
        "3": "Execute transactions"
      }
    },
    {
      "group": "action_authority_reach",
      "id": "system_reach",
      "name": "System Reach",
      "tiers": {
        "1": "Single system",
        "2": "Multiple internal",
        "3": "Cross-domain / third-party"
      }
    },
    {
      "group": "action_authority_reach",
      "id": "blast_radius",
      "name": "Blast Radius",
      "tiers": {
        "1": "Single user",
        "2": "Team / department",
        "3": "Enterprise / public"
      }
    },
    {
      "group": "persistence_control",
      "id": "persistence",
      "name": "Persistence",
      "tiers": {
        "1": "Stateless",
        "2": "Session-based",
        "3": "Long-term memory"
      }
    },
    {
      "group": "persistence_control",
      "id": "reversibility",
      "name": "Reversibility",
      "tiers": {
        "1": "Fully reversible",
        "2": "Partially reversible",
        "3": "Irreversible"
      }
    },
    {
      "group": "persistence_control",
      "id": "control_authority",
      "name": "Control Authority",
      "tiers": {
        "1": "Standalone",
        "2": "Supervises agents",
        "3": "Orchestrates fleets"
      }
    },
    {
      "group": "data_authority_confidentiality",
      "id": "data_sensitivity",
      "name": "Data Sensitivity",
      "tiers": {
        "1": "Public / non-sensitive",
        "2": "Internal / confidential",
        "3": "Regulated / crown-jewel"
      }
    },
    {
      "group": "data_authority_confidentiality",
      "id": "aggregation_risk",
      "name": "Aggregation Risk",
      "tiers": {
        "1": "No aggregation",
        "2": "Limited",
        "3": "Cross-session / inferential"
      }
    },
    {
      "group": "data_authority_confidentiality",
      "id": "data_egress_paths",
      "name": "Data Egress Paths",
      "tiers": {
        "1": "Constrained outputs",
        "2": "Multiple controlled",
        "3": "External egress"
      }
    }
  ],
  "frameworks": [
    [
      "nist_ai_rmf",
      "NIST AI RMF"
    ],
    [
      "iso_42001",
      "ISO/IEC 42001"
    ],
    [
      "eu_ai_act",
      "EU AI Act"
    ],
    [
      "owasp_llm",
      "OWASP LLM Top 10"
    ],
    [
      "mitre_atlas",
      "MITRE ATLAS"
    ],
    [
      "sr_11_7",
      "SR 11-7"
    ]
  ],
  "groups": [
    [
      "autonomy_decision_power",
      "Autonomy & Decision Power"
    ],
    [
      "action_authority_reach",
      "Action Authority & Reach"
    ],
    [
      "persistence_control",
      "Persistence & Control"
    ],
    [
      "data_authority_confidentiality",
      "Data Authority & Confidentiality"
    ]
  ],
  "risk_tier_defs": {
    "1": "Tier 1 — Low. All twelve dimensions at baseline. Standard documentation and acceptable-use controls.",
    "2": "Tier 2 — Medium. Elevated dimensions but none at the highest level. Enhanced oversight, documented controls, periodic review.",
    "3": "Tier 3 — High. At least one dimension at its highest level (worst-case-wins). Comprehensive governance: executive approval, real-time monitoring, kill-switch capability, pre-deployment testing."
  },
  "standards_matrix": {
    "action_authority": {
      "eu_ai_act": [
        "High-risk obligations"
      ],
      "iso_42001": [
        "Operational controls"
      ],
      "mitre_atlas": [
        "Execution TTPs"
      ],
      "nist_ai_rmf": [
        "Manage"
      ],
      "owasp_llm": [
        "Insecure output",
        "Excessive agency"
      ]
    },
    "aggregation_risk": {
      "eu_ai_act": [
        "Data governance"
      ],
      "iso_42001": [
        "Privacy controls"
      ],
      "mitre_atlas": [
        "Inference TTPs"
      ],
      "nist_ai_rmf": [
        "Measure"
      ],
      "owasp_llm": [
        "Sensitive info disclosure"
      ]
    },
    "autonomy": {
      "eu_ai_act": [
        "Art. 14 human oversight"
      ],
      "iso_42001": [
        "Oversight controls"
      ],
      "nist_ai_rmf": [
        "Govern",
        "Manage"
      ],
      "owasp_llm": [
        "Excessive agency"
      ],
      "sr_11_7": [
        "Use governance"
      ]
    },
    "blast_radius": {
      "eu_ai_act": [
        "Annex III classification"
      ],
      "iso_42001": [
        "Impact assessment"
      ],
      "mitre_atlas": [
        "Impact TTPs"
      ],
      "nist_ai_rmf": [
        "Map",
        "Measure"
      ],
      "sr_11_7": [
        "Materiality"
      ]
    },
    "control_authority": {
      "iso_42001": [
        "Governance controls"
      ],
      "mitre_atlas": [
        "Orchestration TTPs"
      ],
      "nist_ai_rmf": [
        "Govern",
        "Manage"
      ],
      "owasp_llm": [
        "Excessive agency"
      ],
      "sr_11_7": [
        "Governance"
      ]
    },
    "data_egress_paths": {
      "iso_42001": [
        "Interface controls"
      ],
      "mitre_atlas": [
        "Exfiltration TTPs"
      ],
      "nist_ai_rmf": [
        "Manage"
      ],
      "owasp_llm": [
        "Insecure output",
        "Data leakage"
      ]
    },
    "data_sensitivity": {
      "eu_ai_act": [
        "Art. 10 data governance"
      ],
      "iso_42001": [
        "Data controls"
      ],
      "mitre_atlas": [
        "Exfiltration TTPs"
      ],
      "nist_ai_rmf": [
        "Map",
        "Measure"
      ],
      "owasp_llm": [
        "Sensitive info disclosure"
      ],
      "sr_11_7": [
        "Data quality"
      ]
    },
    "decision_scope": {
      "eu_ai_act": [
        "Scope determination"
      ],
      "iso_42001": [
        "Impact assessment"
      ],
      "nist_ai_rmf": [
        "Map",
        "Measure"
      ],
      "sr_11_7": [
        "Model use scope"
      ]
    },
    "persistence": {
      "iso_42001": [
        "Data & lifecycle controls"
      ],
      "mitre_atlas": [
        "Persistence TTPs"
      ],
      "nist_ai_rmf": [
        "Manage"
      ],
      "owasp_llm": [
        "Sensitive info disclosure"
      ]
    },
    "reversibility": {
      "eu_ai_act": [
        "Art. 12 record-keeping"
      ],
      "iso_42001": [
        "Operational controls"
      ],
      "nist_ai_rmf": [
        "Manage"
      ],
      "sr_11_7": [
        "Validation"
      ]
    },
    "system_reach": {
      "iso_42001": [
        "Supplier & interface controls"
      ],
      "mitre_atlas": [
        "Initial access",
        "Lateral movement"
      ],
      "nist_ai_rmf": [
        "Map"
      ],
      "owasp_llm": [
        "Supply chain"
      ]
    },
    "temporal_coupling": {
      "iso_42001": [
        "Lifecycle controls"
      ],
      "mitre_atlas": [
        "Chained TTPs"
      ],
      "nist_ai_rmf": [
        "Manage"
      ],
      "owasp_llm": [
        "Excessive agency"
      ],
      "sr_11_7": [
        "Ongoing monitoring"
      ]
    }
  },
  "system_types": {
    "autonomous_agent": "Autonomous agent",
    "code_content_generator": "Code / content generator",
    "decision_support_system": "Decision support",
    "embedded_physical_ai": "Embedded / physical AI",
    "knowledge_assistant": "Knowledge assistant",
    "tool_using_agent": "Tool-using agent",
    "transaction_commerce_agent": "Transaction / commerce agent"
  }
};
