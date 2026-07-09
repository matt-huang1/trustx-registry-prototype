window.__EXAMPLES__ = [
  {
    "agent": {
      "description": "A documentation assistant that reads the company's already-public help articles\nand drafts a plain-language FAQ answer for a writer to review. It has read-only\naccess to published content only, holds no customer or personal data, and cannot\nsend messages, call any external tool, or change any record; a person edits and\npublishes the answer before it is used.",
      "slug": "low-public-docs-assistant"
    },
    "challenge": {
      "flagged": false,
      "iterations": 1,
      "notes": []
    },
    "dimensions": {
      "autonomy": {
        "evidence": [
          "'a person edits and publishes the answer before it is used'"
        ],
        "rationale": "The agent requires human confirmation for every step, as a person must edit and publish the answer.",
        "score": 1
      },
      "data_exposure": {
        "evidence": [
          "'reads the company's already-public help articles' and 'holds no customer or personal data'"
        ],
        "rationale": "The agent only has read-only access to already-public content and holds no sensitive data.",
        "score": 1
      },
      "delegated_authority": {
        "evidence": [
          "'cannot ... change any record'"
        ],
        "rationale": "The agent has no authority to spend money, sign, or change records.",
        "score": 1
      },
      "tool_access": {
        "evidence": [
          "'cannot send messages, call any external tool'"
        ],
        "rationale": "The agent cannot invoke any external tools or APIs.",
        "score": 1
      }
    },
    "provenance": {
      "approved_by": "example-build",
      "submitted_by": "classifier",
      "timestamp": "2026-07-09T14:26:14.842097+00:00"
    },
    "risk_tier": "low"
  },
  {
    "agent": {
      "description": "A support-triage agent that reads customer support tickets containing the\ncustomer's name, order number, and message, then drafts a suggested reply and a\npriority label for a human support agent to review. It sees no payment details,\nidentity documents, or account credentials, and cannot send replies, issue\nrefunds, or change any account; a human makes every final decision.",
      "slug": "medium-support-triage-agent"
    },
    "challenge": {
      "flagged": true,
      "iterations": 2,
      "notes": [
        "The score for 'data_exposure' is too high. A score of 3 suggests a higher level of sensitivity or risk than indicated by the description, which states that the agent only accesses customer names and order numbers without any payment details or identity documents. A lower score would be more appropriate."
      ]
    },
    "dimensions": {
      "autonomy": {
        "evidence": [
          "'a human support agent to review'"
        ],
        "rationale": "The agent requires human confirmation for every action it takes.",
        "score": 1
      },
      "data_exposure": {
        "evidence": [
          "'reads customer support tickets containing the customer's name, order number, and message'"
        ],
        "rationale": "The agent accesses customer names and order numbers, which are sensitive but limited in scope.",
        "score": 3
      },
      "delegated_authority": {
        "evidence": [
          "'cannot send replies, issue refunds, or change any account'"
        ],
        "rationale": "The agent has no authority to perform actions like sending replies or issuing refunds.",
        "score": 1
      },
      "tool_access": {
        "evidence": [
          "'drafts a suggested reply and a priority label'"
        ],
        "rationale": "The agent does not invoke any external tools or APIs.",
        "score": 1
      }
    },
    "provenance": {
      "approved_by": "example-build",
      "submitted_by": "classifier",
      "timestamp": "2026-07-09T14:26:24.378156+00:00"
    },
    "risk_tier": "medium"
  },
  {
    "agent": {
      "description": "A vendor-payment agent that can initiate payment to vendors over ACH to settle\napproved invoices. Every individual payment is reviewed and approved by a member\nof the finance team before it is sent, so a human signs off on each transaction.",
      "slug": "high-vendor-payment-agent"
    },
    "challenge": {
      "flagged": true,
      "iterations": 2,
      "notes": [
        "Deterministic override: description implies money movement (initiate payment / transfer funds / ACH); the LLM scored delegated_authority=2 but it was forced to >= 4.",
        "delegated_authority score of 4 is too high; the description indicates that the agent cannot initiate payments without human approval, suggesting a lower level of authority."
      ]
    },
    "dimensions": {
      "autonomy": {
        "evidence": [
          "Every individual payment is reviewed and approved by a member of the finance team before it is sent."
        ],
        "rationale": "The agent requires human approval for each payment, limiting its independence.",
        "score": 2
      },
      "data_exposure": {
        "evidence": [
          "can initiate payment to vendors over ACH to settle approved invoices."
        ],
        "rationale": "The agent likely handles sensitive financial data but does not exfiltrate it.",
        "score": 2
      },
      "delegated_authority": {
        "evidence": [
          "Every individual payment is reviewed and approved by a member of the finance team before it is sent.",
          "deterministic-rule: money-movement capability detected in description"
        ],
        "rationale": "The agent has limited authority as it cannot initiate payments without human approval.",
        "score": 4
      },
      "tool_access": {
        "evidence": [
          "can initiate payment to vendors over ACH to settle approved invoices."
        ],
        "rationale": "The agent can initiate payments over ACH, indicating some access to financial tools.",
        "score": 3
      }
    },
    "provenance": {
      "approved_by": "example-build",
      "submitted_by": "classifier",
      "timestamp": "2026-07-09T14:26:10.125343+00:00"
    },
    "risk_tier": "high"
  }
];
