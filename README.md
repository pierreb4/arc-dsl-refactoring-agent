# HITL Multi-Agent Code Refactoring System

**Kaggle Agents Intensive Capstone Project - Freestyle Track**

A human-in-the-loop (HITL) multi-agent system that incrementally refactors the [arc-dsl codebase](https://github.com/michaelhodel/arc-dsl) through intelligent analysis, proposal generation, validation, and documentation. This "meta-agent" approach—agents that help refactor and improve code—demonstrates an innovative application of AI agents for software engineering.

## 🎯 Project Overview

### The Problem

The ARC-DSL (Abstraction and Reasoning Corpus Domain Specific Language) codebase suffers from:
- **Type Ambiguity**: Overuse of Union types and isinstance checks making code hard to reason about
- **Poor Organization**: 200+ functions in `dsl.py` with identical signatures but no grouping mechanism
- **Complexity**: Manual refactoring is risky due to tight coupling and limited test coverage

### The Solution

A multi-agent system with human oversight that:
1. **Analyzes** code for refactoring opportunities (type issues, function grouping)
2. **Proposes** incremental, backward-compatible changes
3. **Validates** proposals through automated testing
4. **Documents** all changes with migration guides
5. **Learns** from human approval patterns via Memory Bank

### Why Agents?

Traditional refactoring tools are rule-based and brittle. Our agent-based approach provides:
- **Intelligence**: LLMs understand code semantics, not just syntax
- **Adaptability**: Learns from human decisions to improve future proposals
- **Safety**: HITL checkpoints prevent automated mistakes
- **Coordination**: Multiple specialized agents collaborate on complex tasks

## 🏗️ Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     COORDINATOR AGENT                       │
│  Orchestrates workflow: Analysis → Refactor → Validate      │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  ANALYSIS    │  │  REFACTOR    │  │ VALIDATION   │
    │   AGENT      │  │   AGENT      │  │   AGENT      │
    │              │  │              │  │              │
    │ • Find type  │  │ • Generate   │  │ • Run tests  │
    │   issues     │  │   proposals  │  │ • Check      │
    │ • Group      │  │ • Ensure     │  │   backwards  │
    │   functions  │  │   compat     │  │   compat     │
    └──────────────┘  └──────────────┘  └──────────────┘
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                   ┌─────────────────┐
                   │  HITL APPROVAL  │
                   │   CHECKPOINT    │
                   │                 │
                   │ Human decides:  │
                   │ Approve/Reject  │
                   └─────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ DOCUMENTATION    │
                  │     AGENT        │
                  │                  │
                  │ • Docstrings     │
                  │ • Changelog      │
                  │ • Migration docs │
                  └──────────────────┘
```

### Agent Roles

| Agent | Purpose | Key Responsibilities |
|-------|---------|---------------------|
| **Coordinator** | Workflow orchestration | Manages multi-agent pipeline, handles retries |
| **Analysis** | Code inspection | Identifies type ambiguities, finds groupable functions |
| **Refactor** | Code transformation | Generates backward-compatible refactoring proposals |
| **Validation** | Quality assurance | Runs tests, checks compatibility, assesses risk |
| **Documentation** | Knowledge capture | Creates docstrings, changelogs, migration guides |

### Custom Tools

```python
class RefactoringTools:
    read_file(file_path)           # Load source code
    write_file(file_path, content) # Save refactored code (with backup)
    analyze_type_usage(file_path)  # Find isinstance checks and Union types
    find_function_signatures(...)  # Identify functions with identical signatures
    run_tests(test_file)           # Execute pytest suite
```

### Session State & Memory

- **Session State**: Tracks files processed, proposals approved/rejected, metrics
- **Memory Bank**: Stores approval patterns and rejection reasons to learn human preferences
- **Checkpoints**: Records every HITL decision with timestamps and feedback

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Gemini API key ([Get one here](https://aistudio.google.com/app/api-keys))

### Installation

```bash
# Clone this repository
cd "AI Agents Intensive"

# Install dependencies
pip install python-dotenv google-genai google-adk ipywidgets

# Set up API key
echo "GOOGLE_API_KEY=your_api_key_here" > code/.env
```

### Running the System

1. **Open the notebook**:
   ```bash
   jupyter notebook code/arc-dsl-refactoring-agent.ipynb
   ```

2. **Execute cells sequentially** (1-13):
   - Cells 1-4: Setup and configuration
   - Cells 5-8: Initialize tools, memory, and agents
   - Cell 9: HITL checkpoint interface
   - Cell 10: Workflow execution
   - Cells 11-12: Metrics and reporting
   - Cell 13: Run the system

3. **Interact with HITL checkpoints**:
   - Review each proposal summary
   - Enter `approve`, `skip`, or `reject`
   - Provide feedback for rejected proposals
   - System learns from your decisions

### Example Session

```
📊 ANALYSIS SUMMARY:
  - isinstance checks found: 47
  - Union types found: 4
  - Groupable function signatures: 12

🔨 REFACTORING PROPOSAL:
Replace Union[Grid, np.ndarray] with dedicated Grid type...

✅ VALIDATION RESULTS:
All tests pass. Backward compatible via type aliases...

Decision [approve/skip/reject]: approve
✅ APPROVED - Will proceed with refactoring
```

## 📊 Key Concepts Demonstrated

This project demonstrates **7 out of 8** core course concepts:

- ✅ **Multi-agent system**: 5 specialized agents collaborating
- ✅ **Custom tools**: 5 tools for code analysis and transformation
- ✅ **Sessions & Memory**: Session state + Memory Bank for learning
- ✅ **Observability**: Logging, tracing, and metrics tracking
- ✅ **Context engineering**: Specialized system prompts per agent
- ✅ **Agent evaluation**: Validation agent + metrics tracking
- ✅ **Gemini**: Gemini 2.0 Flash powers all agents
- ⏳ **Deployment**: Cloud Run (planned)

## 📈 Results & Metrics

### Refactoring Impact (Per Session)

| Metric | Target | Status |
|--------|--------|--------|
| isinstance checks removed | 150+ | Tracked |
| Union types eliminated | 4 | Tracked |
| Functions grouped | 20+ | Tracked |
| Test coverage maintained | 100% | Validated |
| Backward compatibility | Yes | Required |

### Kaggle Scoring Progress

**Current: 95/100 points**

- ✅ Pitch (30/30): Architecture docs, innovative approach
- ✅ Implementation (45/50): Core system + observability
- ✅ Documentation (20/20): Comprehensive README
- 🔄 Bonus (5/20): Gemini integrated, deployment pending

**Target: 100/100 points**

## 🔧 Technical Implementation

### Agent System (Gemini-Powered)

```python
# Each agent uses Gemini 2.0 Flash with specialized prompts
analysis_agent = RefactoringAgent(
    name="Analysis Agent",
    system_prompt="""You analyze Python files for refactoring opportunities.
    Focus on type ambiguity and function grouping..."""
)

# Coordinator orchestrates multi-agent workflow
result = coordinator.process_file("arc-dsl/arc_types.py")
# Returns: {analysis, proposal, validation, metrics}
```

### HITL Approval Flow

```python
def hitl_checkpoint(result):
    # Display proposal summary
    print(f"Proposal: {result['proposal'][:500]}...")
    print(f"Validation: {result['validation'][:500]}...")
    
    # Get human decision
    decision = input("Decision [approve/skip/reject]: ")
    
    # Store in memory bank for learning
    store_memory(decision, context=result['file'])
    
    return {'status': decision, 'feedback': feedback}
```

### Observability & Metrics

```python
# All agents wrapped with observability
class ObservableRefactoringAgent:
    def call(self, prompt, context):
        metrics.log_agent_call(self.name)
        metrics.log_llm_request(prompt_length=len(prompt))
        # ... execute agent ...
        metrics.log_llm_request(response_length=len(response))
        return response

# Comprehensive metrics tracking
metrics = RefactoringMetrics()
# Tracks: agent calls, tool calls, LLM tokens, 
#         HITL decisions, errors

# After session:
metrics.display_summary()
# Shows complete breakdown of agent performance
```

**Observability Features:**
- **Logging**: DEBUG-level logs to `refactoring_agent.log`
- **Metrics**: Real-time tracking of agents, tools, LLM calls, HITL approvals
- **Tracing**: Complete session workflow with timestamps
- **Error Tracking**: All errors logged with context for debugging

```python
# System learns from human decisions
memory_bank = {
    'approval_patterns': [
        {'context': 'arc_types.py', 'proposal_type': 'eliminate_union'},
    ],
    'rejection_reasons': [
        {'context': 'dsl.py', 'reason': 'Changes too large, split into smaller PRs'},
    ],
    'preferences': {
        'incremental_changes': True,
        'backward_compatibility': True
    }
}
```

## 📚 Documentation

- **[Analysis Document](doc/analysis-arcDslRefactoringTargets.md)**: 600+ lines detailing refactoring targets
- **[Architecture Document](doc/architecture-arcDslRefactoringAgent.md)**: 1000+ lines with system design
- **[Progress Tracker](doc/progress-arcDslRefactoringAgent.md)**: Step-by-step implementation status
- **[Jupyter Notebook](code/arc-dsl-refactoring-agent.ipynb)**: Complete working implementation

## 🎯 Why Freestyle Track?

This project exemplifies the Freestyle track's spirit:

1. **Innovative**: Meta-agents (agents that improve code) are unconventional
2. **Unclassifiable**: Doesn't fit neatly into other tracks (not purely chat, productivity, or game)
3. **Meaningful Agent Use**: Agents are central—impossible to solve without multi-agent collaboration
4. **Real-World Value**: Addresses actual software engineering pain point

## 🚀 Next Steps

- [x] **Step 1-3**: Analysis, architecture, implementation ✅
- [x] **Step 4**: Observability (LoggingPlugin + Metrics) ✅
- [ ] **Step 5**: Deploy to Cloud Run (+5 pts deployment)
- [ ] **Step 6**: Create NotebookLM video (+10 pts)
- [ ] **Submit**: Kaggle writeup before Dec 1, 2025

## 📄 License

Apache 2.0 (matching Kaggle course materials)

## 🙏 Acknowledgments

- **ARC-DSL**: Michael Hodel's excellent DSL for ARC challenges
- **Google ADK**: Agent Development Kit team
- **Kaggle**: Agents Intensive course instructors

---

**Built for**: Kaggle Agents Intensive Capstone Project  
**Track**: Freestyle  
**Date**: November 2025  
**Target Score**: 100/100 points
