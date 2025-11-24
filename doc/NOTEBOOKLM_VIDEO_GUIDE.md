# NotebookLM Video Creation Guide

**Goal**: Create a <3 minute video explaining the ARC-DSL Refactoring Agent for Kaggle Capstone submission

**Worth**: 10/120 points (final requirement for 120/120)

---

## Step 1: Upload Source Materials to NotebookLM

Visit [NotebookLM](https://notebooklm.google.com/) and create a new notebook with these sources:

### Required Documents (Upload all)

1. **README.md** (main project overview)
   - Path: `/Users/pierre/Library/CloudStorage/GoogleDrive-pierre@baume.org/My Drive/AI Agents Intensive/README.md`
   - Contains: Problem statement, solution, architecture, results

2. **Architecture Document**
   - Path: `doc/architecture-arcDslRefactoringAgent.md`
   - Contains: Detailed 6-agent design, workflow diagrams

3. **Implementation Complete**
   - Path: `doc/IMPLEMENTATION_COMPLETE.md`
   - Contains: Phase 2 summary with ADK integration details

4. **Deployment Guide**
   - Path: `code/deployment/DEPLOYMENT.md`
   - Contains: Cloud Run deployment instructions

5. **Quick Reference**
   - Path: `doc/QUICK_REFERENCE.md`
   - Contains: Essential commands and workflows

---

## Step 2: Generate Audio Overview

Once sources are uploaded, NotebookLM will offer to generate an "Audio Overview":

1. Click **"Generate"** button
2. Wait 2-3 minutes for AI hosts to create discussion
3. Listen to the generated audio (usually 8-12 minutes)
4. Identify the best 3-minute segment covering:
   - Problem (type ambiguity in ARC-DSL)
   - Solution (HITL multi-agent with ADK review)
   - Innovation (usage-based specialization)
   - Results (91 opportunities, 0 regressions)

---

## Step 3: Create Video Content

### Option A: Screen Recording + Audio Overlay

**Tools**: QuickTime (macOS), OBS Studio (cross-platform)

**Content to Record**:
1. **Intro (30s)**: Show README title, problem statement
2. **Architecture (60s)**: Display 6-agent diagram from README
3. **Demo (90s)**: Show:
   - Notebook cell execution
   - ADK code review rejecting bad implementation
   - Tests passing (0 regressions)
4. **Results (30s)**: Show metrics (91 opportunities, 66% ADK precision)

### Option B: Slide Deck + NotebookLM Audio

**Create 6-8 slides covering**:

1. **Title Slide**: "ARC-DSL Refactoring Agent - HITL Multi-Agent System"
2. **Problem**: Show before/after code (generic vs specialized)
3. **Solution**: 6-agent architecture diagram
4. **Innovation**: Usage-based specialization vs direct refinement
5. **ADK Review**: Show rejection of frozenset bug
6. **Results**: 91 opportunities, 0 regressions, 110/120 points
7. **Deployment**: Cloud Run web UI screenshot
8. **Summary**: Top 3 Freestyle track considerations

**Export as video** using:
- Google Slides (File → Download → Microsoft PowerPoint, then export)
- Keynote (Export → Movie)
- PowerPoint (Export → Create Video)

---

## Step 4: Video Requirements Checklist

**Duration**: <3 minutes (strict requirement)  
**Quality**: 720p minimum, 1080p recommended  
**Format**: MP4, WebM, or MOV  
**Audio**: Clear narration (NotebookLM audio or voiceover)

**Must Cover** (from Kaggle rubric):
- ✅ **Problem Statement**: Type ambiguity in ARC-DSL (30s)
- ✅ **Why Agents**: 200+ manual hours → automated HITL (30s)
- ✅ **Architecture**: 6 specialized agents (Gemini-powered) (60s)
- ✅ **Demo**: Show ADK review catching bugs (45s)
- ✅ **Build Process**: Phase 1 → Phase 2 evolution (30s)

---

## Step 5: Upload to YouTube

1. **Create/login** to YouTube account
2. **Upload video**:
   - Click **Create** → **Upload videos**
   - Select your video file
   
3. **Video Details**:
   - **Title**: "ARC-DSL Refactoring Agent - HITL Multi-Agent Code Refactoring System"
   - **Description**:
     ```
     Kaggle AI Agents Intensive Capstone Project - Freestyle Track
     
     A Human-in-the-Loop (HITL) multi-agent system that uses AI to improve 
     code quality through intelligent, usage-based refactoring.
     
     Key Features:
     - 6 specialized agents (Analysis, Proposer, Refactor, Validation, 
       Specialization, Code Review)
     - Gemini-powered ADK semantic validation (66% bug rejection rate)
     - Usage-based specialization (91 type-safety improvements)
     - Zero regressions across 1000 solver functions
     - Deployed to Google Cloud Run
     
     GitHub: [Your repo URL]
     Kaggle: AI Agents Intensive - November 2024
     Track: Freestyle
     
     Score: 110/120 (Target: 120/120 with this video!)
     ```
   
   - **Visibility**: Unlisted or Public
   - **Category**: Science & Technology
   - **Tags**: kaggle, ai agents, gemini, code refactoring, multi-agent system, 
     python, type safety, HITL, cloud run

4. **Copy YouTube URL** (e.g., `https://youtu.be/xxxxx`)

---

## Step 6: Validate Video

**Before submitting to Kaggle, check**:
- [ ] Duration <3 minutes
- [ ] Audio clear and understandable
- [ ] Shows problem, solution, architecture, demo
- [ ] YouTube link works (test in incognito)
- [ ] No API keys or sensitive data visible

---

## Step 7: Submit to Kaggle

1. Go to Kaggle Competitions writeup section
2. Add **Media Gallery** → YouTube URL
3. Verify video embeds correctly
4. Complete submission

---

## Video Script Template

**Use this as a guide for narration (180 seconds total)**:

### Intro (0:00-0:30)
"Hi, I'm presenting the ARC-DSL Refactoring Agent, a meta-agent system that uses 
AI to improve code quality. The ARC Domain-Specific Language has 35 functions 
with type ambiguity - functions like 'first' and 'last' use generic 'Any' types 
that reduce safety and IDE support. Traditional refactoring would take 100+ hours."

### Solution (0:30-1:00)
"Our solution: A Human-in-the-Loop multi-agent system with 6 specialized agents. 
Three are powered by Gemini: the Proposer generates type refinements, the 
Specialization agent creates usage-based versions, and the Code Review agent 
validates semantic correctness. We added ADK code review as a quality gate 
between AI proposals and human approval."

### Innovation (1:00-1:45)
"Here's the innovation: Instead of refining generic functions directly - which 
produces no-ops - we analyze how they're actually used in 1000 solver functions. 
For example, 'first' is called 74 times with different types. We create specialized 
versions like 'first_grid' and 'first_object' that provide type safety while 
preserving the generic original. The ADK review catches semantic bugs like 
frozenset ordering issues - it rejected 66% of bad implementations."

### Results (1:45-2:15)
"Results: 91 specialization opportunities identified, 4 specialized functions 
created, zero regressions across all tests. The system maintains 100% backward 
compatibility. We deployed to Google Cloud Run with an interactive web UI for 
the HITL workflow."

### Closing (2:15-2:30)
"This project demonstrates all 8 course concepts: multi-agent collaboration, 
ADK integration, sessions, observability, and deployment. It's deployed, tested, 
and ready for production. Thank you!"

---

## Tips for Success

1. **Keep it concise**: Judges watch many videos, make yours punchy
2. **Show, don't just tell**: Screen recordings > static slides
3. **Highlight innovation**: Usage-based specialization is unique
4. **Emphasize results**: 0 regressions is impressive
5. **Professional quality**: Good audio is more important than video

---

## Estimated Time

- Upload sources to NotebookLM: 10 minutes
- Generate audio overview: 3 minutes (automatic)
- Create video slides/recording: 30-60 minutes
- Edit and export: 15-30 minutes
- Upload to YouTube: 10 minutes

**Total: 1-2 hours** to reach 120/120 points! 🎉

---

## Quick Wins

**Minimal Effort Option** (30 minutes):
1. Upload 5 documents to NotebookLM
2. Generate audio overview
3. Create simple slide deck (6 slides)
4. Export as video with NotebookLM audio
5. Upload to YouTube
6. Submit Kaggle writeup

**This gets you 10 points and completes the capstone!**
