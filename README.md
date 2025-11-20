# HITL Multi-Agent Code Refactoring System

**Kaggle Agents Intensive Capstone Project - Freestyle Track**

A human-in-the-loop (HITL) multi-agent system that incrementally refactors the [arc-dsl codebase](https://github.com/michaelhodel/arc-dsl) through intelligent analysis, proposal generation, automated testing, and documentation. Features a **two-stage HITL workflow**: review proposals before testing, then commit or rollback based on test results. This "meta-agent" approach—agents that help refactor and improve code—demonstrates an innovative application of AI agents for software engineering.

## 🎯 Project Overview

### The Problem

The ARC-DSL (Abstraction and Reasoning Corpus Domain Specific Language) codebase suffers from:
- **Type Ambiguity**: Overuse of Union types and isinstance checks making code hard to reason about
- **Poor Organization**: 200+ functions in `dsl.py` with identical signatures but no grouping mechanism
- **Complexity**: Manual refactoring is risky due to tight coupling and limited test coverage

### The Solution

A multi-agent system with two-stage human oversight that:
1. **Analyzes** code for refactoring opportunities using MCP professional tools (Rope, Radon, Vulture, Pyrefly)
2. **Proposes** incremental, backward-compatible changes in structured JSON format
3. **Reviews** at Checkpoint #1: Human approves/rejects proposal before any changes
4. **Tests** automatically via pytest if approved, with backup creation
5. **Reviews** at Checkpoint #2: Human commits or rolls back based on test results
6. **Documents** all changes with migration guides (if committed)
7. **Learns** from human approval patterns via Memory Bank

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
    │ • Find type  │  │ • Generate   │  │ • Check      │
    │   issues     │  │   proposals  │  │   backwards  │
    │ • Group      │  │ • Ensure     │  │   compat     │
    │   functions  │  │   compat     │  │ • Assess risk│
    │ • MCP tools  │  │ • JSON fmt   │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                   ┌─────────────────┐
                   │ CHECKPOINT #1   │
                   │ Review Proposal │
                   │                 │
                   │ Approve/Reject/ │
                   │ Skip/Abort      │
                   └─────────────────┘
                            │ (if approved)
                            ▼
                   ┌─────────────────┐
                   │  Apply Changes  │
                   │  Create Backup  │
                   └─────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Run pytest on  │
                   │ arc-dsl/tests.py│
                   └─────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ CHECKPOINT #2   │
                   │ Review Tests    │
                   │                 │
                   │ Commit/Rollback/│
                   │ Abort           │
                   └─────────────────┘
                            │ (if committed)
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
    # Basic file operations
    read_file(file_path)           # Load source code
    write_file(file_path, content) # Save refactored code (with timestamped backup)
    
    # MCP-enhanced analysis (uses mcp-python-refactoring package)
    analyze_type_usage(file_path)  # Find isinstance checks & Union types
                                   # Falls back to MCP: Rope, Radon, Vulture, Pyrefly
    
    # Code structure analysis
    find_function_signatures(...)  # Identify functions with identical signatures
    
    # Testing (used by two-stage HITL workflow)
    run_tests(test_file)           # Execute pytest suite
```

**MCP Integration**: Analysis Agent uses professional refactoring tools via MCP:
- **Rope**: Refactoring analysis
- **Radon**: Complexity metrics (cyclomatic, maintainability index)
- **Vulture**: Dead code detection
- **Pyrefly**: Type checking
- **McCabe**: Complexity analysis
- **Complexipy**: Advanced complexity metrics

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
   - Review formatted analysis, proposal, and validation
   - Choose: `approve`, `skip`, `reject`, or `abort`
   - Provide feedback for rejected proposals
   - System learns from your decisions and continues
   - Abort cleanly stops the workflow at any point

### Example Session

```
📊 ANALYSIS SUMMARY
--------------------------------------------------------------------------------
  🔍 Issues Found: 8
     1. [HIGH] type_ambiguity at line 45
        Union[Grid, np.ndarray] creates type confusion...
     2. [MEDIUM] isinstance_check at line 127
        Multiple isinstance checks indicate need for type refinement...
  
  📦 Function Grouping Opportunities: 3
     1. 12 functions with signature: (Grid) -> Grid

  💡 Top Recommendations:
     1. [Priority 1, Risk: low] Replace Union types with dedicated classes...

================================================================================
🔨 REFACTORING PROPOSAL
--------------------------------------------------------------------------------
  🎯 Target: Eliminate Union[Grid, np.ndarray] type ambiguity
  📋 Strategy: Create dedicated Grid class with np.ndarray wrapper...
  📝 Proposed Changes: 1 file(s)
     1. arc_types.py: ~45 lines
        Before: Grid = Union[List[List[int]], np.ndarray]...
        After:  class Grid: def __init__(self, data: np.ndarray)...

================================================================================
✅ VALIDATION RESULTS
--------------------------------------------------------------------------------
  ✅ Overall Status: PASS
  ✅ Backward Compatible: True
  
  ⚠️ Risks Identified: 2
     1. Existing code using isinstance(x, np.ndarray) needs wrapper...
     2. Performance impact minimal but requires testing...

================================================================================
DECISION OPTIONS:
  • approve (a/yes/y) - Apply this refactoring
  • skip (s)          - Skip this file, continue to next
  • reject (r/no/n)   - Reject this refactoring
  • abort (stop/quit) - Stop the entire workflow
================================================================================

🤔 Your decision: approve

✅ Refactoring APPROVED
📝 Generating documentation...
✓ Documentation generated
```

## 📊 Key Concepts Demonstrated

This project demonstrates **7 out of 8** core course concepts:

- ✅ **Multi-agent system**: 5 specialized agents (Coordinator, Analysis, Refactor, Validation, Documentation) with sequential workflow
- ✅ **Tools - Custom**: 5 custom tools (read_file, write_file, analyze_type_usage, find_function_signatures, run_tests)
- ✅ **Tools - MCP**: mcp-python-refactoring integration (Rope, Radon, Vulture, Pyrefly, McCabe, Complexipy)
- ✅ **Sessions & Memory**: session_state dict tracking + memory_bank for learning human preferences
- ✅ **Observability**: RefactoringMetrics class + file/console logging with DEBUG/INFO levels
- ✅ **Context engineering**: Specialized system prompts per agent role
- ✅ **Agent evaluation**: Automated pytest testing + two-stage HITL validation + metrics
- ✅ **Gemini**: Gemini 2.5 Flash Lite powers all 5 agents
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

### Two-Stage HITL Workflow

**Stage 1: Checkpoint #1 - Review Proposal**
```python
def hitl_checkpoint(result):
    """First checkpoint: Review agent proposal before testing"""
    
    # Display formatted sections (parses JSON, extracts key info)
    print("📊 ANALYSIS SUMMARY")
    print(_format_analysis(result['analysis']))  # Issues, grouping, recommendations
    
    print("🔨 REFACTORING PROPOSAL")
    print(_format_proposal(result['proposal']))   # Target, strategy, changes
    
    print("✅ VALIDATION RESULTS")
    print(_format_validation(result['validation']))  # Status, risks, compatibility
    
    # Present clear decision options
    print("DECISION OPTIONS:")
    print("  • approve (a/yes/y) - Apply this refactoring and run tests")
    print("  • skip (s)          - Skip this file, continue to next")
    print("  • reject (r/no/n)   - Reject this refactoring")
    print("  • abort (stop/quit) - Stop the entire workflow")
    
    decision = input("Your decision: ").strip().lower()
    
    if decision in ['approve', 'a', 'yes', 'y']:
        store_memory('approval', context=result['file'])
        return {'status': 'approve'}  # Proceed to Stage 2
    # ... handle skip/reject/abort
```

**Stage 2: Apply, Test, and Checkpoint #2 - Commit/Rollback**
```python
# If approved at Checkpoint #1:

# 1. Apply refactoring and create backup
backup_path = write_file(file_path, refactored_code)  # Auto-creates timestamped backup

# 2. Run automated tests
test_result = subprocess.run(['python', '-m', 'pytest', 'arc-dsl/tests.py', ...])
test_passed = (test_result.returncode == 0)

# 3. Second checkpoint: Show test results
print("👤 CHECKPOINT #2: COMMIT OR ROLLBACK")
print(f"🧪 Test Result: {'✅ PASSED' if test_passed else '❌ FAILED'}")
print(f"💾 Backup: {backup_path}")

print("DECISION OPTIONS:")
if test_passed:
    print("  • commit (c/yes/y)  - Keep the changes (tests passed!)")
    print("  • rollback (r/no/n) - Restore backup (despite passing tests)")
else:
    print("  • commit (c/yes/y)  - Keep the changes (despite test failures)")
    print("  • rollback (r/no/n) - Restore backup (recommended - tests failed!)")
print("  • abort (stop/quit) - Stop the entire workflow")

commit_decision = input("Your decision: ").strip().lower()

if commit_decision in ['rollback', 'r', 'no', 'n']:
    subprocess.run(['cp', backup_path, file_path])  # Restore original
    print("✅ Original file restored")
elif commit_decision in ['commit', 'c', 'yes', 'y']:
    print("✅ Changes committed")
    # Generate documentation, update metrics, etc.
```

**Key Features:**
- **Two Decision Points**: Review before testing, commit after seeing results
- **Automated Testing**: pytest runs automatically between checkpoints
- **Safe Rollback**: Timestamped backups enable instant restore
- **Test Transparency**: See exact pass/fail before committing
- **Smart Formatting**: Parses JSON, shows prioritized info (top 3 issues/risks)
- **Abort Anywhere**: Clean exit at either checkpoint
- **Memory Learning**: Stores all decisions for pattern recognition

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
