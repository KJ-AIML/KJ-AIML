<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/kj-hello-still.svg" />
  <img src="./assets/kj-hello.svg" width="855" alt="Two hands made of dots reach toward each other and touch. A green spark bursts and forms the handle kjct0s_ between them, above the words Hello KJ." />
</picture>

<sub>[View still artwork](./assets/kj-hello-still.svg)</sub>

# Hey, I'm KJ — Kongphop Jamreansuk

**AI engineer for LLM systems, agents, and inference infrastructure.**<br>
Co-founder & CTO at [Talvyn Labs](https://talvynlabs.com) and Axtra Intellion · Bangkok, Thailand

<a href="https://www.kjsc.dev"><img src="./assets/icons/btn-site.svg" height="28" alt="Website: kjsc.dev"></a>
<a href="https://www.linkedin.com/in/kongphop-jamreansuk/"><img src="./assets/icons/btn-linkedin.svg" height="28" alt="LinkedIn"></a>
<a href="https://www.kjsc.dev/resume"><img src="./assets/icons/btn-cv.svg" height="28" alt="CV"></a>
<a href="https://www.npmjs.com/package/heli-harness"><img src="./assets/icons/btn-npm.svg" height="28" alt="heli-harness on npm"></a>

I take AI from a first proof of concept to a system that runs reliably in
production: serving open models on GPUs, building agent workflows whose
decisions can be audited, and making the tools that keep coding agents on track.
My rule is simple: *make it exist first, make it production-ready next.*

## Production work

- **LLM serving.** Deployed open models (Typhoon, Qwen, Gemma, GPT-OSS) behind
  OpenAI-compatible APIs with vLLM, then evaluated, tuned, and quantized them to
  fit on-premise and cloud GPU budgets.
- **Thai speech-to-text with PII masking.** On-premise call transcription for a
  PCI-DSS environment. Two NVIDIA L4 GPUs are shared between speech and LLM
  workloads, recordings are split at pauses, and an LLM picks the best of three
  Thai speech models for each call.
- **Auditable PII detection.** A LangGraph workflow that checks transcripts in
  overlapping chunks, re-verifies every finding to cut false positives, and keeps
  an audit trail so QA can review each masking decision.
- **Document and compliance AI.** An on-premise PDF and OCR extraction service
  that replaced a paid cloud API, and an LLM engine, still pre-launch, that checks
  pay against Australian Modern Award rules.
- **Agent-assist copilot.** Follows live support chats, finds the answer with RAG,
  and suggests a reply to the agent, reaching 95%+ tag recall.

Employers and dates are on my [CV](https://www.kjsc.dev/resume).

## Companies

<img src="./assets/icons/talvyn-labs.png" height="22" align="top" alt=""> **[Talvyn Labs](https://talvynlabs.com)** · Co-founder & CTO<br>
A software house and product studio in Bangkok. We design and build AI agents,
automation, websites, and web apps for businesses, and keep them running after
launch. Our products include TalvynCRM, a CRM shaped around how each business
works, and TalvynMesher, a workspace where AI agents share context and people
approve what goes out.

<img src="./assets/icons/axtra-intellion.png" height="22" align="top" alt=""> **Axtra Intellion (AXTL)** · Co-founder & CTO<br>
I'm building AXTL. You describe the backend you need in plain English and review
the spec it writes. AXTL then generates the code, tests it in a sandbox, and
deploys a FastAPI agent backend. It runs on Cloud Run, Cloud Build, and
Cloudflare Workers, and is in pre-launch testing.

## Open source

<table>
<tr>
<td width="50%" valign="top">
<a href="https://github.com/KJ-AIML/heli-harness"><img src="./assets/projects/heli-harness.jpg" alt="Heli-Harness artwork: governance for coding agents"></a><br>
<b><a href="https://github.com/KJ-AIML/heli-harness">Heli-Harness</a></b> · <img src="./assets/icons/npm.svg" height="18" align="top" alt=""> npm package<br>
Carries project context, policies, and task handoffs between coding tools and repositories.<br>
<a href="https://github.com/KJ-AIML/heli-harness#readme">Get started</a> · <a href="https://www.npmjs.com/package/heli-harness">npm</a> · <a href="https://github.com/KJ-AIML/heli-harness/releases">Releases</a>
</td>
<td width="50%" valign="top">
<a href="https://github.com/KJ-AIML/samo"><img src="./assets/projects/samo.jpg" alt="Samo's overview screen: CPU, memory, disk and the busiest processes"></a><br>
<b><a href="https://github.com/KJ-AIML/samo">Samo</a></b> · <img src="./assets/icons/rust.svg" height="18" align="top" alt=""> Rust + GPUI<br>
A native Mac disk and system monitor that finds large files and cleans up build artifacts.<br>
<a href="https://github.com/KJ-AIML/samo">Source</a> · <a href="https://github.com/KJ-AIML/samo/releases">Downloads</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<a href="https://github.com/KJ-AIML/memctrl"><img src="./assets/projects/memctrl.png" alt="A MemCtrl session brief in a terminal, with one memory flagged as stale"></a><br>
<b><a href="https://github.com/KJ-AIML/memctrl">MemCtrl</a></b> · <img src="./assets/icons/rust.svg" height="18" align="top" alt=""> <img src="./assets/icons/sqlite.svg" height="18" align="top" alt=""> Rust + SQLite<br>
Local memory for coding agents that flags stale context and shows where each memory came from.<br>
<a href="https://github.com/KJ-AIML/memctrl#quick-start">Get started</a> · <a href="https://github.com/KJ-AIML/memctrl/releases">Releases</a>
</td>
<td width="50%" valign="top">
<a href="https://github.com/KJ-AIML/clarify"><img src="./assets/projects/clarify.jpg" alt="A Clarify architecture brief for an e-commerce checkout"></a><br>
<b><a href="https://github.com/KJ-AIML/clarify">Clarify</a></b> · <img src="./assets/icons/javascript.svg" height="18" align="top" alt=""> JavaScript<br>
Turns Markdown into interactive architecture and decision boards for you and your coding agent.<br>
<a href="https://github.com/KJ-AIML/clarify">Source</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<a href="https://github.com/KJ-AIML/alms"><img src="./assets/projects/alms.png" alt="The ALMS quick start: install the CLI, then alms init my-project"></a><br>
<b><a href="https://github.com/KJ-AIML/alms">ALMS</a></b> · <img src="./assets/icons/python.svg" height="18" align="top" alt=""> <img src="./assets/icons/fastapi.svg" height="18" align="top" alt=""> Python + FastAPI<br>
A backend starter and CLI with explicit application and agent layers.<br>
<a href="https://github.com/KJ-AIML/alms#quick-start-with-cli">Get started</a> · <a href="https://github.com/KJ-AIML/alms/releases">Releases</a>
</td>
<td width="50%" valign="top">
<a href="https://github.com/KJ-AIML/axga-harness-agent-rs"><img src="./assets/projects/axga.png" alt="An AXGA terminal session: a request, the tool it runs, and its answer"></a><br>
<b><a href="https://github.com/KJ-AIML/axga-harness-agent-rs">AXGA</a></b> · <img src="./assets/icons/rust.svg" height="18" align="top" alt=""> Rust<br>
A small coding agent made to run on a cheap VPS.<br>
<a href="https://github.com/KJ-AIML/axga-harness-agent-rs">Source</a> · <a href="https://github.com/KJ-AIML/axga-harness-agent-rs/releases">Releases</a>
</td>
</tr>
</table>

I contributed a [fullscreen fix to OpenIDEA](https://github.com/l0ng-ai/openidea/pull/1608)
for grouped project windows on notched Macs. It was merged and shipped in
[v0.1.38](https://github.com/l0ng-ai/openidea/releases/tag/v0.1.38). I also
maintain an [agent backend field guide](https://github.com/KJ-AIML/agent-native-backend).

## Stack

<p>
<img src="./assets/icons/python.svg" height="28" alt="Python" title="Python">
<img src="./assets/icons/rust.svg" height="28" alt="Rust" title="Rust">
<img src="./assets/icons/typescript.svg" height="28" alt="TypeScript" title="TypeScript">
<img src="./assets/icons/react.svg" height="28" alt="React" title="React">
<img src="./assets/icons/fastapi.svg" height="28" alt="FastAPI" title="FastAPI">
<img src="./assets/icons/langchain.svg" height="28" alt="LangChain" title="LangChain">
<img src="./assets/icons/langgraph.svg" height="28" alt="LangGraph" title="LangGraph">
<img src="./assets/icons/pytorch.svg" height="28" alt="PyTorch" title="PyTorch">
<img src="./assets/icons/ollama.svg" height="28" alt="Ollama" title="Ollama">
<img src="./assets/icons/postgresql.svg" height="28" alt="PostgreSQL" title="PostgreSQL">
<img src="./assets/icons/redis.svg" height="28" alt="Redis" title="Redis">
<img src="./assets/icons/docker.svg" height="28" alt="Docker" title="Docker">
<img src="./assets/icons/githubactions.svg" height="28" alt="GitHub Actions" title="GitHub Actions">
<img src="./assets/icons/googlecloud.svg" height="28" alt="Google Cloud" title="Google Cloud">
<img src="./assets/icons/cloudflare.svg" height="28" alt="Cloudflare" title="Cloudflare">
</p>

<details>
<summary>Full stack</summary>
<br>

**LLM & agents:** LangGraph, LangChain, RAG, multi-agent workflows, open-source LLMs<br>
**Inference & GPU:** vLLM, Ollama, quantization, model evaluation, GPU-aware scheduling<br>
**Speech & documents:** Thai ASR (Typhoon, Pathumma), voice activity detection, PII masking, OCR<br>
**Backend & infra:** Python, FastAPI, PyTorch, Rust (Axum, SQLx), TypeScript/React, PostgreSQL, pgvector, Redis, Docker, GitHub Actions, GCP, Cloudflare Workers

</details>

## Working with me

I'm open to AI platform and AI engineering opportunities, and to collaboration
from anywhere. Reach me through [kjsc.dev](https://www.kjsc.dev) or
[LinkedIn](https://www.linkedin.com/in/kongphop-jamreansuk/).

<sub>The hand artwork is adapted from my [pi-ter](https://github.com/KJ-AIML/pi-ter) project, and every image here is a local file. [Design](./docs/design-system.md) · [Sources](./docs/profile-refresh/sources.md)</sub>
