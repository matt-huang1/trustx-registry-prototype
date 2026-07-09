window.__EXAMPLES__ = [
  {
    "agent": {
      "description": "A documentation assistant that reads the company's already-public help articles\nand drafts a plain-language FAQ answer for a writer to review. It has read-only\naccess to published content only, holds no customer or personal data, and cannot\nsend messages, call any external tool, or change any record; a person edits and\npublishes the answer before it is used.",
      "slug": "low-public-docs-assistant"
    },
    "autonomy_level": 1,
    "challenge": {
      "flagged": true,
      "iterations": 2,
      "notes": [
        "control_authority score of 2 is not supported. The system does not supervise agents; it requires human intervention for all actions."
      ]
    },
    "dimensions": {
      "action_authority": {
        "evidence": [
          "has read-only access to published content only"
        ],
        "rationale": "The system has read-only access and cannot modify content.",
        "score": 1
      },
      "aggregation_risk": {
        "evidence": [
          "reads the company's already-public help articles"
        ],
        "rationale": "There is no aggregation of data as it only uses public articles.",
        "score": 1
      },
      "autonomy": {
        "evidence": [
          "A person edits and publishes the answer before it is used."
        ],
        "rationale": "The system requires human approval for publishing each answer.",
        "score": 1
      },
      "blast_radius": {
        "evidence": [
          "A person edits and publishes the answer before it is used."
        ],
        "rationale": "The system impacts a single user (the writer) who reviews the output.",
        "score": 1
      },
      "control_authority": {
        "evidence": [
          "A person edits and publishes the answer before it is used."
        ],
        "rationale": "The system supervises the content creation process but requires human intervention.",
        "score": 2
      },
      "data_egress_paths": {
        "evidence": [
          "cannot send messages, call any external tool"
        ],
        "rationale": "The system does not have any external egress paths.",
        "score": 1
      },
      "data_sensitivity": {
        "evidence": [
          "has read-only access to published content only"
        ],
        "rationale": "The system only accesses public content, which is non-sensitive.",
        "score": 1
      },
      "decision_scope": {
        "evidence": [
          "reads the company's already-public help articles"
        ],
        "rationale": "The system makes local decisions based on existing content.",
        "score": 1
      },
      "persistence": {
        "evidence": [
          "holds no customer or personal data"
        ],
        "rationale": "The system does not retain any state or memory.",
        "score": 1
      },
      "reversibility": {
        "evidence": [
          "A person edits and publishes the answer before it is used."
        ],
        "rationale": "The actions taken by the system can be fully reversed by the human editor.",
        "score": 1
      },
      "system_reach": {
        "evidence": [
          "reads the company's already-public help articles"
        ],
        "rationale": "The system operates within a single system of published content.",
        "score": 1
      },
      "temporal_coupling": {
        "evidence": [
          "drafts a plain-language FAQ answer for a writer to review."
        ],
        "rationale": "The actions are isolated and do not depend on previous actions.",
        "score": 1
      }
    },
    "provenance": {
      "approved_by": "example-build",
      "submitted_by": "classifier",
      "timestamp": "2026-07-09T18:45:31.969404+00:00"
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
      "description": "A support-triage agent that reads customer support tickets containing the\ncustomer's name, order number, and message, then drafts a suggested reply and a\npriority label for a human support agent to review. Its priority labels order the\nsupport team's shared ticket queue, and it keeps session context while a ticket\nconversation is open. It sees no payment details, identity documents, or account\ncredentials, and cannot send replies, issue refunds, or change any account; a\nhuman makes every final decision.",
      "slug": "medium-support-triage-agent"
    },
    "autonomy_level": 1,
    "challenge": {
      "flagged": true,
      "iterations": 2,
      "notes": [
        "temporal_coupling score of 2 is too high; the description indicates that the agent keeps session context but does not imply continuous loops, which would warrant a score of 3."
      ]
    },
    "dimensions": {
      "action_authority": {
        "evidence": [
          "cannot send replies, issue refunds, or change any account; a human makes every final decision."
        ],
        "rationale": "The agent has read-only capabilities and cannot execute actions independently.",
        "score": 1
      },
      "aggregation_risk": {
        "evidence": [
          "reads customer support tickets."
        ],
        "rationale": "There is no aggregation of data as the agent processes individual tickets without combining information.",
        "score": 1
      },
      "autonomy": {
        "evidence": [
          "A human makes every final decision."
        ],
        "rationale": "The system requires human review and approval for each action before execution.",
        "score": 1
      },
      "blast_radius": {
        "evidence": [
          "reads customer support tickets."
        ],
        "rationale": "The agent impacts a single user (the customer) at a time through ticket handling.",
        "score": 1
      },
      "control_authority": {
        "evidence": [
          "A human makes every final decision."
        ],
        "rationale": "The agent operates independently without supervising other agents or systems.",
        "score": 1
      },
      "data_egress_paths": {
        "evidence": [
          "cannot send replies, issue refunds, or change any account."
        ],
        "rationale": "The agent has constrained outputs and does not send data externally.",
        "score": 1
      },
      "data_sensitivity": {
        "evidence": [
          "It sees no payment details, identity documents, or account credentials."
        ],
        "rationale": "The agent does not access sensitive information, only reading non-sensitive customer support tickets.",
        "score": 1
      },
      "decision_scope": {
        "evidence": [
          "drafts a suggested reply and a priority label for a human support agent to review."
        ],
        "rationale": "The agent makes local decisions regarding ticket replies and priority labels.",
        "score": 1
      },
      "persistence": {
        "evidence": [
          "keeps session context while a ticket conversation is open."
        ],
        "rationale": "The agent maintains session context during active ticket conversations but does not retain long-term memory.",
        "score": 2
      },
      "reversibility": {
        "evidence": [
          "a human makes every final decision."
        ],
        "rationale": "The actions taken by the agent can be fully reversed by human intervention.",
        "score": 1
      },
      "system_reach": {
        "evidence": [
          "reads customer support tickets containing the customer's name, order number, and message."
        ],
        "rationale": "The agent operates within a single system, handling customer support tickets.",
        "score": 1
      },
      "temporal_coupling": {
        "evidence": [
          "keeps session context while a ticket conversation is open."
        ],
        "rationale": "The agent operates within chained workflows as it keeps session context during ticket conversations.",
        "score": 2
      }
    },
    "provenance": {
      "approved_by": "example-build",
      "submitted_by": "classifier",
      "timestamp": "2026-07-09T18:45:49.256266+00:00"
    },
    "risk_tier": "medium",
    "system_type": "decision_support_system",
    "tier_derivation": {
      "autonomy_level_driven": false,
      "driving_dimensions": [
        "persistence"
      ],
      "profile": "decision_support_system",
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
      "description": "A vendor-payment agent that can initiate payment to vendors over ACH to settle\napproved invoices. Every individual payment is reviewed and approved by a member\nof the finance team before it is sent, so a human signs off on each transaction.",
      "slug": "high-vendor-payment-agent"
    },
    "autonomy_level": 1,
    "challenge": {
      "flagged": true,
      "iterations": 2,
      "notes": [
        "Deterministic override: description implies money movement (initiate payment / transfer funds / ACH), which is executing transactions; the LLM scored action_authority=2 but it was forced to 3 (\"Execute transactions\"). Under worst-case-wins this yields Tier 3 (high).",
        "The score for 'action_authority' is too high. It should be 2 instead of 3, as the agent requires human approval to execute transactions, indicating it cannot execute transactions independently."
      ]
    },
    "dimensions": {
      "action_authority": {
        "evidence": [
          "Every individual payment is reviewed and approved by a member of the finance team before it is sent.",
          "deterministic-rule: money-movement capability detected in description"
        ],
        "rationale": "The agent can create or modify payment requests but requires human approval to execute them.",
        "score": 3
      },
      "aggregation_risk": {
        "evidence": [
          "Every individual payment is reviewed and approved..."
        ],
        "rationale": "There is no indication of data aggregation risks in the agent's operations.",
        "score": 1
      },
      "autonomy": {
        "evidence": [
          "Every individual payment is reviewed and approved by a member of the finance team before it is sent."
        ],
        "rationale": "The agent requires human approval for each payment, indicating a human-in-the-loop system.",
        "score": 1
      },
      "blast_radius": {
        "evidence": [
          "settle approved invoices."
        ],
        "rationale": "The agent impacts a team or department by processing payments for multiple vendors.",
        "score": 2
      },
      "control_authority": {
        "evidence": [
          "Every individual payment is reviewed and approved..."
        ],
        "rationale": "The agent operates independently without supervising other agents.",
        "score": 1
      },
      "data_egress_paths": {
        "evidence": [
          "Every individual payment is reviewed and approved..."
        ],
        "rationale": "The agent's outputs are constrained to payment transactions without external egress.",
        "score": 1
      },
      "data_sensitivity": {
        "evidence": [
          "initiate payment to vendors over ACH..."
        ],
        "rationale": "The agent handles internal financial data, which is confidential.",
        "score": 2
      },
      "decision_scope": {
        "evidence": [
          "initiate payment to vendors over ACH to settle approved invoices."
        ],
        "rationale": "The agent makes local decisions regarding individual payments to vendors.",
        "score": 1
      },
      "persistence": {
        "evidence": [
          "Every individual payment is reviewed and approved..."
        ],
        "rationale": "The agent does not retain state between transactions, acting statelessly.",
        "score": 1
      },
      "reversibility": {
        "evidence": [
          "payments can be partially reversed..."
        ],
        "rationale": "Payments can be reversed, but the extent of reversibility is not specified, suggesting full reversibility.",
        "score": 1
      },
      "system_reach": {
        "evidence": [
          "initiate payment to vendors over ACH..."
        ],
        "rationale": "The agent operates within a single system for vendor payments.",
        "score": 1
      },
      "temporal_coupling": {
        "evidence": [
          "Every individual payment is reviewed and approved..."
        ],
        "rationale": "The actions are isolated to individual payments without chaining workflows.",
        "score": 1
      }
    },
    "provenance": {
      "approved_by": "example-build",
      "submitted_by": "classifier",
      "timestamp": "2026-07-09T18:45:14.673576+00:00"
    },
    "risk_tier": "high",
    "system_type": "transaction_commerce_agent",
    "tier_derivation": {
      "autonomy_level_driven": false,
      "driving_dimensions": [
        "action_authority"
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
