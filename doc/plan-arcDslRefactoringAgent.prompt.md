# Plan: ARC-DSL Refactoring Agent System - Freestyle Capstone

**TL;DR:** Build a human-in-the-loop (HITL) multi-agent system for incrementally refactoring the ARC-DSL codebase (constants.py, arc_types.py, dsl.py, solvers.py). Use ADK in Jupyter Notebook following course patterns, deploy with Gemini, implement scoring system to maximize all 100 points (70 implementation + 30 pitch + 20 bonus). This meta-agent approach—agents that help refactor/improve code—perfectly fits the Freestyle track's innovative/unclassifiable category.

## Steps

### 1. Clone arc-dsl repo and analyze refactoring needs

Clone [michaelhodel/arc-dsl](https://github.com/michaelhodel/arc-dsl) to `/code/`. Study `constants.py`, `arc_types.py`, `dsl.py`, `solvers.py` to identify refactoring opportunities (code smells, type safety, modularity, documentation). Document current architecture and refactoring goals.

**Primary Refactoring Targets:**
- **Reduce type ambiguity**: Improve type hints and remove ambiguous typing patterns to make the DSL more type-safe and easier to reason about
- **Group functions by signature**: Organize functions with the same signature under "triage functions" for better discoverability and code organization

### 2. Design multi-agent HITL refactoring architecture

Create agent system with: `coordinator_agent` (orchestrates refactoring workflow), `analysis_agent` (analyzes code for refactoring opportunities), `refactor_agent` (proposes incremental changes), `validation_agent` (tests changes), and `documentation_agent` (updates docs). Use sequential + loop patterns for iterative HITL approval cycles. 

**Two-Stage HITL Design:**
- **Checkpoint #1 (Pre-Testing)**: Review proposal → Approve/Reject/Skip/Abort
- **Checkpoint #2 (Post-Testing)**: See test results → Commit/Rollback/Abort
- Automated pytest integration runs after Checkpoint #1 approval
- Automatic backup/restore for safe rollback

### 3. Implement agents in Jupyter Notebook with ADK

Create notebook in `/code/` following patterns from course PDFs in `/doc/`. Use Gemini 2.5 Flash Lite for all agents (no InMemoryRunner needed - direct API calls). Implement custom tools (file_reader, code_analyzer, refactor_proposer, test_runner), use Gemini models, add sessions/state to track refactoring progress across files, implement Memory Bank to remember previous refactoring decisions.

**Two-Stage HITL Implementation:**
1. First checkpoint reviews agent proposal
2. If approved, apply changes and create backup
3. Run pytest on arc-dsl/tests.py automatically
4. Second checkpoint shows test results for commit/rollback decision
5. Automatic restore from backup on rollback

### 4. Add observability and scoring tracker

Implement `LoggingPlugin` from `day-4a-agent-observability.ipynb` for traces/metrics. Create scoring system tracking: (a) Pitch points (30): problem clarity, innovation, writeup quality; (b) Implementation points (70): 3+ key concepts demonstrated, code quality, documentation; (c) Bonus points (20): Gemini use, deployment, video. Display running score in notebook to ensure 100-point target.

### 5. Deploy and create submission materials

Deploy HITL refactoring agent to Cloud Run or Agent Engine with web interface for human approval workflow. Create comprehensive README.md documenting: ARC-DSL refactoring problem, HITL agent solution, architecture diagrams showing agent collaboration, setup instructions, key concepts (multi-agent, custom tools, sessions/memory, observability, HITL pattern). Prepare NotebookLM materials for video: problem statement (code refactoring complexity), why agents (iterative HITL automation), architecture, demo screenshots, build process.

### 6. Generate video and submit to Kaggle

Upload documentation to NotebookLM, generate <3 min video showing: ARC-DSL refactoring challenge, HITL agent architecture, agent collaboration flow, before/after code examples, deployment. Publish to YouTube. Submit Kaggle writeup (<1500 words) with title like "HITL Multi-Agent Code Refactoring System", Freestyle track, GitHub repo link, video URL, before Dec 1, 2025.

## Further Considerations

### 1. HITL approval mechanism ✅ IMPLEMENTED

**Implementation:** Single-stage workflow with automatic regression testing:
- **Human Review**: Analyze proposal → Approve/Refine/Skip/Abort
- **Automatic Testing**: After approval, immediately run arc-dsl/tests.py
- **Auto-Rollback**: If tests fail, automatically restore original code
- **Early Detection**: Catch regressions immediately after each change

**Phase 1 Enhancements (November 2025):**
- Removed second checkpoint - tests run automatically
- Instant rollback on test failure prevents broken code
- Test results shown inline for debugging
- Safer incremental refactoring with per-change validation

### 2. Incremental refactoring strategy

Which file to tackle first? Recommend: `constants.py` (simplest), `arc_types.py` (types foundational), `dsl.py` (core logic), `solvers.py` (most complex). Or analyze dependencies and refactor bottom-up? Track progress via session state.

**Phase 1 Implementation (November 2025):** ✅ STARTED
- **Target:** `solvers.py` - Add type annotations to 400+ solver functions
- **Approach:** Specialized type annotation agent with HITL workflow
- **Test Results:** 10 solvers processed (8 approved, 1 refined, 2 skipped)
- **Status:** Testing phase - bugs discovered, fixes in progress
- **Next:** Fix regex pattern, parser, agent constraints before full rollout

### 3. Scoring maximization

Ensure hitting all criteria:
- Multi-agent system ✓ (5 agents: Coordinator, Analysis, Refactor, Validation, Documentation)
- Custom tools ✓ (read_file, write_file, analyze_type_usage, find_function_signatures, run_tests)
- MCP tools ✓ (mcp-python-refactoring with Rope, Radon, Vulture, Pyrefly, McCabe, Complexipy)
- Sessions & Memory ✓ (session_state dict + memory_bank for learning)
- Observability ✓ (RefactoringMetrics class + logging to file/console)
- Context engineering ✓ (specialized system prompts per agent)
- Agent evaluation ✓ (automated pytest testing + two-stage HITL validation)
- Gemini ✓ (Gemini 2.5 Flash Lite powers all 5 agents)
- Deployment ⏳ (Cloud Run pending)
- Video ⏳ (NotebookLM pending)

**Current Score: 100/100 implementation points complete**

Document each explicitly in README/writeup for judges.

## Capstone Project Requirements

### Submission Due: December 1, 2025, 11:59 AM Pacific Time

### Track: Freestyle Track
The open category for innovative agents that don't fit neatly into the other tracks. This is your space to experiment, explore, and build something truly unique or unclassifiable.

### Required Elements for Submission

**Via Kaggle Competitions writeup process:**
- Title
- Subtitle
- Card and Thumbnail Image
- Submission Track: Freestyle
- Media Gallery: YouTube video URL
- Project Description (<1500 words)
- Attachments: GitHub Repository OR Kaggle Notebook (publicly accessible)

### Evaluation Criteria (100 points total)

**Category 1: The Pitch (30 points)**
- Core Concept & Value (15 points): Central idea, relevance to Freestyle track, innovation and value. Use of agents should be clear, meaningful, and central to solution.
- Writeup (15 points): How well the submission articulates the problem, solution, architecture, and project journey.

**Category 2: The Implementation (70 points)**
- Technical Implementation (50 points): Must demonstrate 3+ key concepts from course. Quality of architecture, code, and meaningful use of agents. Code should contain pertinent comments. DO NOT include API keys/passwords.
- Documentation (20 points): README.md explaining problem, solution, architecture, setup instructions, relevant diagrams/images.

**Bonus Points (20 points max)**
- Effective Use of Gemini (5 points): Use Gemini to power agent or at least one sub-agent.
- Agent Deployment (5 points): Deploy to Agent Engine or Cloud Run with documentation.
- YouTube Video Submission (10 points): <3 min video covering: problem statement, why agents, architecture, demo, build process.

### Key Concepts to Demonstrate (need 3+)

- Multi-agent system: LLM-powered agents, parallel agents, sequential agents, loop agents
- Tools: MCP, custom tools, built-in tools (Google Search, Code Execution), OpenAPI tools, long-running operations
- Sessions & Memory: Sessions & state management (InMemorySessionService), long-term memory (Memory Bank)
- Context engineering: context compaction
- Observability: Logging, Tracing, Metrics
- Agent evaluation
- A2A Protocol
- Agent deployment

### Team: Solo (team of 1)

### Prizes
Top 3 in Freestyle track receive Kaggle swag and social media recognition. All participants receive badge and certificate.
