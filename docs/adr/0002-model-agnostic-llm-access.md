# ADR-0002: Model-agnostic LLM access via an OpenAI-compatible interface

- Status: Accepted
- Date: 2026-07-08

## Decision
Route all LLM access through a single thin interface (`classifier/provider.py`) built on
an **OpenAI-compatible** client. The base URL, API key, and model name are read only from
environment variables (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`). No provider or model
name is hard-coded anywhere else. Switching to an open-weight model (e.g. GLM-5.2 via
OpenRouter) or a local/on-prem endpoint (e.g. Ollama) is a config change only.

## Context
This is an open-source registry whose credibility rests on being transparent and
reproducible — including on models that anyone can run. We must not couple the method to a
single commercial vendor, and we must be able to run fully offline/on-prem for sensitive
descriptions. Tests must run with no network and no API key.

## Alternatives considered
- **Hard-code one provider (e.g. the OpenAI SDK directly, throughout the code).** Simple
  initially, but couples the whole project to one vendor, blocks open-weight/on-prem use,
  and scatters model assumptions across the codebase.
- **A per-provider SDK abstraction (a class per provider: OpenAI, Anthropic, Google, …).**
  Flexible but heavy: every provider adds a dependency and a code path to maintain and
  test, and the surface we actually need (one chat completion) is tiny.

## Why chosen
The OpenAI chat-completions API is a de-facto standard that OpenRouter, vLLM, Ollama,
LM Studio, and many hosted open-weight providers already speak. A single tiny
`LLMProvider` protocol therefore gives vendor-neutral, open-weight-capable, on-prem-capable
access with one dependency and one code path — and makes the offline test suite trivial by
injecting a fake that satisfies the same protocol.
