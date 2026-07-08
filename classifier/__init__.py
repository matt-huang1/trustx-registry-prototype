"""AI-agent risk classifier: a bounded maker/checker loop.

Public entry points:
    classifier.graph.classify   -- run the full proposer/challenger/human_gate loop
    classifier.rules            -- deterministic overrides (the "checker" facts)
    classifier.provider         -- model-agnostic LLM access
"""
