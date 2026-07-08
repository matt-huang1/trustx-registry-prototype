# Architecture

The registry turns a free-text agent description into a defensible, evidence-backed
risk entry through a bounded **maker/checker** loop: an LLM *proposer* drafts scores,
an LLM *challenger* red-teams them, **deterministic rules** override the LLM wherever a
fact can be pinned down, and a *human gate* ratifies the result before anything is
written to `entries/`. All LLM access is funnelled through a single OpenAI-compatible
provider so the model is swappable via environment variables only.

## TODO
- [ ] Diagram of the LangGraph state machine (proposer → challenger → human_gate).
- [ ] Describe the entry lifecycle: draft → challenged → ratified → published.
- [ ] Document how risk-tier drives the depth of the human gate (auto-approve low, mandatory review high).
- [ ] Data flow and storage model once the web UI and a backing store exist.
- [ ] Threat model for the classifier itself (prompt injection via agent descriptions).
