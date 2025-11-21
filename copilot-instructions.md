# Copilot Instructions for ARC-DSL Refactoring Agent System

## Project Overview

This is a **Freestyle Capstone Project** for the AI Agents Intensive course - a human-in-the-loop (HITL) multi-agent system that performs incremental refactoring of the ARC-DSL codebase using patch-based transformations.

**Key Innovation**: Meta-agent approach - agents that help refactor/improve code through iterative HITL approval cycles with automated testing and rollback capabilities.

## Git Workflow Guidelines

### When to Save to Git

**ALWAYS commit after:**
- ✅ Completing a major feature or system component
- ✅ Successfully passing all tests
- ✅ Fixing critical bugs that restore functionality
- ✅ Adding new agents or tools to the system
- ✅ Updating documentation (README, plan, progress)
- ✅ Before starting risky refactoring operations
- ✅ After successful HITL checkpoint approvals that maintain test baseline

**DO NOT commit:**
- ❌ Broken/incomplete code
- ❌ Failing tests (unless documenting a known issue)
- ❌ Debug/temporary files (already in .gitignore)
- ❌ API keys or sensitive credentials
- ❌ Work-in-progress experiments

### Commit Message Format

Use conventional commits format:

```
<type>(<scope>): <subject>

<optional body>

<optional footer>
```

**Types:**
- `feat`: New feature (e.g., `feat(agents): add patch-based refactoring agent`)
- `fix`: Bug fix (e.g., `fix(hitl): resolve KeyError in checkpoint feedback`)
- `docs`: Documentation changes (e.g., `docs(readme): add architecture diagrams`)
- `refactor`: Code refactoring (e.g., `refactor(tools): simplify MCP integration`)
- `test`: Test additions/changes (e.g., `test(validation): add 160-test baseline`)
- `chore`: Maintenance tasks (e.g., `chore(gitignore): add debug files`)

**Examples:**
```bash
git commit -m "feat(agents): implement two-stage HITL with automated testing"
git commit -m "fix(patch): use -p0 for exact path matching without prefix stripping"
git commit -m "docs(plan): update scoring to reflect 100/100 implementation points"
```

## Files Managed by Git

### Core Project Files (COMMIT)
- ✅ `code/arc-dsl-refactoring-agent.ipynb` - Main notebook
- ✅ `doc/plan-arcDslRefactoringAgent.prompt.md` - Project plan
- ✅ `doc/progress-arcDslRefactoringAgent.md` - Progress tracking
- ✅ `README.md` - Project documentation
- ✅ `copilot-instructions.md` - This file
- ✅ `.gitignore` - Git exclusions (single root-level file)
- ✅ `.env.example` - Example environment configuration
- ✅ `requirements.txt` - Python dependencies (if exists)

### Generated/Temporary Files (IGNORE)
- ❌ `code/debug_patch_*.patch` - Debugging patch files
- ❌ `code/*.backup.*` - Backup files from refactoring operations
- ❌ `code/refactoring_report_*.txt` - Session reports
- ❌ `code/refactoring_agent.log` - Debug logs
- ❌ `code/logger.log` - Additional logs
- ❌ `*.log` - All log files
- ❌ `.env` - Actual environment variables (secrets!)
- ❌ `__pycache__/` - Python bytecode
- ❌ `.pytest_cache/` - Test cache
- ❌ `code/arc-dsl/` - Cloned dependency (managed separately)
- ❌ `code/data/` - Data files
- ❌ `code/day-*.ipynb` - Course materials (already in doc/)
- ❌ `code/home_automation_agent/` - Course example
- ❌ `code/research-agent/` - Course example

## Project Architecture

### Multi-Agent System (5 Agents)

1. **Coordinator Agent** - Orchestrates refactoring workflow
2. **Analysis Agent** - Analyzes code for refactoring opportunities
   - Must read ACTUAL file contents
   - Must use EXACT variable names and line numbers
   - No hallucinations allowed!
3. **Refactor Agent** - Generates patch-based refactoring proposals
   - Uses unified diff format (NOT full-file replacements)
   - Patch context must EXACTLY match file content
   - Learns from previous patch failures in Memory Bank
4. **Validation Agent** - Tests and validates changes
5. **Documentation Agent** - Updates documentation

### Two-Stage HITL Workflow

**Stage 1 - Checkpoint #1 (Pre-Testing):**
1. Analysis Agent analyzes file
2. Refactor Agent proposes patches
3. Validation Agent reviews proposal
4. **HUMAN DECISION**: Approve/Reject/Skip/Abort
5. If approved → Apply patches + create timestamped backup

**Stage 2 - Automated Testing + Checkpoint #2:**
6. Run pytest on `arc-dsl/tests.py` automatically
7. Compare results to 160-test baseline
8. **HUMAN DECISION**: Commit (keep) or Rollback (restore backup)

### Key Components

- **Custom Tools**: read_file, write_file, analyze_type_usage, find_function_signatures, run_tests
- **MCP Integration**: mcp-python-refactoring (Rope, Radon, Vulture, Pyrefly, McCabe, Complexipy)
- **Session State**: Tracks refactoring progress across files
- **Memory Bank**: Stores HITL decisions and patch failure lessons for agent learning
- **Observability**: RefactoringMetrics class + logging (DEBUG to file, INFO to console)
- **Patch System**: Uses unified diff format with **`-p1`** (strips `a/` and `b/` prefixes from Git-style diffs)

## Critical Implementation Details

### Patch Format Requirements

**CRITICAL: We use Git-style unified diffs with `-p1` flag**

**CORRECT FORMAT** (what agents must generate):
```diff
--- a/arc-dsl/arc_types.py
+++ b/arc-dsl/arc_types.py
@@ -20,7 +20,7 @@
 Objects = FrozenSet[Object]
 Indices = FrozenSet[IntegerTuple]
 IndicesSet = FrozenSet[Indices]
-Patch = Union[Object, Indices]
+Patch: TypeAlias = Union[Object, Indices]  # Added type hint
 Element = Union[Object, Grid]
 Piece = Union[Grid, Patch]
```

**Key Requirements:**
- **MUST use `a/` and `b/` prefixes** (standard Git format: `--- a/file` and `+++ b/file`)
- Paths after prefix: `arc-dsl/arc_types.py` (HYPHEN not underscore!)
- Applied with `patch -p1` command (strips the `a/` and `b/` prefixes)
- 3+ lines of exact context before and after changes
- Context must match file VERBATIM (no paraphrasing!)

**Why `-p1`?**
- The patch header is `--- a/arc-dsl/constants.py`
- The `-p1` flag strips **1 directory level** from the path
- This removes the `a/` prefix, leaving `arc-dsl/constants.py`
- The file is then found in the workspace at `code/arc-dsl/constants.py`

**WRONG: Using `-p0`**
- Would try to find a file literally named `a/arc-dsl/constants.py`
- This file doesn't exist → "No file found--skip this patch?" error
- We previously had this bug and fixed it!

**Agent Instructions:**
- Refactor Agent system prompt explicitly states: "can be applied with `patch -p1`"
- All patches MUST follow Git unified diff format
- NO exceptions or variations

### Memory Bank Lessons

When patches fail, the system records:
```python
memory_bank[f"patch_failure_{timestamp}"] = {
    'file': file_path,
    'error': error_msg,
    'patch_content': patch_content,
    'lesson': 'Agents must read actual file contents carefully and use exact variable names.'
}
```

These lessons are fed back to agents in subsequent attempts.

### Test Baseline

- **Baseline**: 160 passing tests in `arc-dsl/tests.py`
- **Regression**: Any result < 160 tests triggers warning
- **Validation**: Automated pytest runs after every approved refactoring

## Scoring Tracker (100/120 points)

### Implementation Points: 70/70 ✅
- Multi-agent system: 5 agents with specialized roles
- Custom tools: 5 tools for file/code operations
- MCP tools: Professional Python analysis suite
- Sessions & Memory: Session state + Memory Bank with learning
- Observability: Comprehensive logging/metrics/tracing
- Context engineering: Specialized prompts + file content inclusion
- Agent evaluation: Two-stage HITL + automated pytest

### Pitch Points: 30/30 ✅
- Core concept: Meta-agent refactoring system (innovative!)
- Value proposition: Safe, iterative code improvement with human oversight
- Writeup: Comprehensive documentation in plan/progress/README

### Bonus Points: 15/20 ⏳
- Gemini use (5 pts): ✅ Gemini 2.5 Flash Lite powers all agents
- Deployment (5 pts): ⏳ Cloud Run deployment pending
- Video (10 pts): ⏳ NotebookLM video pending

**Current Total: 115/120 points** 🎯

## Development Workflow

### Before Starting Work
```bash
cd "/Users/pierre/Library/CloudStorage/GoogleDrive-pierre@baume.org/My Drive/AI Agents Intensive"
git status
git pull  # if working across machines
```

### After Completing Work
```bash
# Check what changed
git status
git diff

# Stage important files only (not debug/temp files)
git add code/arc-dsl-refactoring-agent.ipynb
git add doc/plan-arcDslRefactoringAgent.prompt.md
git add doc/progress-arcDslRefactoringAgent.md
git add README.md
# ... add other relevant files

# Commit with meaningful message
git commit -m "feat(feedback): add Memory Bank learning from patch failures"

# Push to remote
git push origin main
```

### Emergency Rollback
```bash
# Restore from backup file
cp arc-dsl/file.py.backup.TIMESTAMP arc-dsl/file.py

# Or use git to undo last commit
git reset --soft HEAD~1  # Keep changes
git reset --hard HEAD~1  # Discard changes (dangerous!)
```

## Common Issues & Solutions

### Issue: 503 UNAVAILABLE or other HTTP errors
**Symptoms**: `google.genai.errors.ServerError: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'The model is overloaded. Please try again later.', 'status': 'UNAVAILABLE'}}`

**Solution**: ✅ Automatic retry is now enabled!
- All agents use manual retry logic with HttpRetryOptions configuration
- Automatically retries on: 429, 500, 503, 504 errors
- Exponential backoff: 1s → 7s → 49s → 343s → 2401s (delay = initial_delay * exp_base^attempt)
- Maximum 5 retry attempts
- Console shows retry progress (e.g., "⚠️ Analysis Agent: HTTP error on attempt 2/5, Retrying in 7.0s...")
- No manual intervention needed - errors are handled automatically

**Technical details:**
- Uses `retry_config = types.HttpRetryOptions(attempts=5, exp_base=7, initial_delay=1, http_status_codes=[429, 500, 503, 504])`
- RefactoringAgent.call() implements retry loop with exponential backoff
- ObservableRefactoringAgent inherits retry logic and adds logging/metrics
- Compatible with `client.models.generate_content()` API (not ADK LlmAgent)

### Issue: Patch won't apply
**Symptoms**: "File to patch: No file found--skip this patch?"

**Solutions:**
1. Check debug_patch_*.patch file to see what LLM generated
2. Verify actual file has the variable names in the patch
3. Ensure agents receive actual file content in prompts
4. Memory Bank will record failure for agent learning

### Issue: Tests fail after refactoring
**Symptoms**: pytest shows < 160 passing tests

**Solutions:**
1. Use Checkpoint #2 "Rollback" decision to restore backup
2. Review what changed and why it broke compatibility
3. Update Memory Bank preferences to avoid similar changes

### Issue: LLM hallucinating variable names
**Symptoms**: Patch references variables that don't exist

**Solutions:**
1. Analysis Agent prompt now includes actual file content
2. Refactor Agent prompt emphasizes EXACT variable names
3. Memory Bank records hallucinations as failures
4. System learns to be more careful over time

## Next Steps (Deployment & Submission)

### Step 5: Deployment (5 bonus points)
- [ ] Create Cloud Run deployment configuration
- [ ] Set up web interface for HITL approvals
- [ ] Document deployment process in README
- [ ] Test deployed system end-to-end

### Step 6: Video & Submission (10 bonus points)
- [ ] Upload docs to NotebookLM
- [ ] Generate <3 min video covering:
  - Problem: ARC-DSL refactoring complexity
  - Solution: HITL multi-agent system
  - Architecture: 5 agents + 2-stage workflow
  - Demo: Before/after code examples
  - Build: Key implementation insights
- [ ] Publish to YouTube
- [ ] Submit to Kaggle before Dec 1, 2025

### Submission Checklist
- [ ] Title: "HITL Multi-Agent Code Refactoring System"
- [ ] Track: Freestyle
- [ ] GitHub repo: Public and accessible
- [ ] README: Complete with diagrams
- [ ] Video URL: YouTube link
- [ ] Writeup: <1500 words
- [ ] No API keys in code!

## Useful Commands

```bash
# Run tests
cd code
pytest arc-dsl/tests.py -v

# Check Python environment
python --version  # Should be 3.13.7

# View logs
tail -f code/refactoring_agent.log

# Count passing tests
pytest arc-dsl/tests.py --quiet | grep "passed"

# Clean up debug files
rm code/debug_patch_*.patch
rm code/*.backup.*
rm code/refactoring_report_*.txt
```

## References

- **Course Materials**: `doc/` folder (day-1 through day-5 PDFs)
- **Project Plan**: `doc/plan-arcDslRefactoringAgent.prompt.md`
- **Progress Log**: `doc/progress-arcDslRefactoringAgent.md`
- **ARC-DSL Repo**: https://github.com/michaelhodel/arc-dsl
- **Submission**: Kaggle Competitions writeup (before Dec 1, 2025)

---

**Remember**: This project demonstrates advanced agent concepts through a practical, real-world use case. The HITL pattern with automated testing and rollback ensures safety while the Memory Bank enables continuous learning. Document everything for maximum scoring! 🚀
