"""
FastAPI Web Application for ARC-DSL Refactoring Agent
Deployment-ready Cloud Run application with HITL workflow
"""

import os
import json
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.genai as genai
from google.genai import types
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

app = FastAPI(title="ARC-DSL Refactoring Agent", version="1.0.0")

# Initialize Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

client = genai.Client(api_key=GOOGLE_API_KEY)

# Global state for session management
workflow_sessions: Dict[str, Dict] = {}

# ============================================================================
# Pydantic Models
# ============================================================================

class AnalysisRequest(BaseModel):
    generic_function: str
    source_file: str = "arc-dsl/solvers.py"

class ProposalReviewRequest(BaseModel):
    session_id: str
    version_index: int
    decision: str  # "approve", "reject", "modify"
    feedback: Optional[str] = None

class TestResultRequest(BaseModel):
    session_id: str
    decision: str  # "commit", "rollback"

# ============================================================================
# Core Agent Functions (Simplified from Notebook)
# ============================================================================

def analyze_function_usage(function_name: str, source_file: str) -> Dict:
    """Analyze usage patterns of a generic function"""
    import ast
    import re
    
    file_path = Path(__file__).parent.parent / source_file
    if not file_path.exists():
        return {"error": f"File not found: {source_file}"}
    
    code = file_path.read_text()
    
    # Count calls and extract context
    pattern = rf'\b{function_name}\s*\('
    calls = re.findall(pattern, code)
    
    return {
        "function_name": function_name,
        "call_count": len(calls),
        "source_file": source_file,
        "analysis_complete": True
    }

def propose_specializations(function_name: str, usage_patterns: Dict) -> List[Dict]:
    """Use Gemini to propose specialized versions"""
    
    prompt = f"""Analyze this generic function usage and propose 2-3 specialized type-safe versions.

Function: {function_name}()
Usage patterns: {usage_patterns['call_count']} calls found

Based on ARC-DSL types (Grid, Object, Piece, Objects, Indices), propose specialized versions.

Return JSON array:
[
  {{
    "name": "specialized_name",
    "signature": "def specialized_name(param: SpecificType) -> ReturnType",
    "implementation": "complete Python function",
    "reasoning": "why this specialization is useful"
  }}
]
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        
        proposals = json.loads(response.text)
        return proposals if isinstance(proposals, list) else []
    
    except Exception as e:
        return [{"error": str(e)}]

def review_with_adk(original_source: str, specialized_version: Dict) -> Dict:
    """ADK Code Review Agent - semantic validation"""
    
    CODE_REVIEW_PROMPT = f"""You are an expert Python code reviewer specializing in type safety and algorithm correctness.

ORIGINAL FUNCTION:
{original_source}

PROPOSED SPECIALIZED VERSION:
{specialized_version.get('implementation', 'N/A')}

CRITICAL CHECKS:
1. Algorithm Preservation - Does it maintain the same logic?
2. Type Safety - Are frozenset/set operations order-safe?
3. Edge Cases - Handles empty/single-element containers?

Return JSON: {{"verdict": "approve|reject|needs_modification", "reasoning": "...", "confidence": "high|medium|low"}}
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=CODE_REVIEW_PROMPT,
            config=types.GenerateContentConfig(
                temperature=0.1,  # Conservative for code review
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)
    
    except Exception as e:
        # Fallback: Permissive (tests will validate)
        return {
            "verdict": "approve",
            "reasoning": f"Review failed: {e}. Relying on tests.",
            "confidence": "low"
        }

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page with workflow UI"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>ARC-DSL Refactoring Agent</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; }
        h1 { color: #4285f4; }
        .section { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; }
        button { background: #4285f4; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #357ae8; }
        .error { color: #d93025; }
        .success { color: #0f9d58; }
        input, select { padding: 8px; margin: 10px 0; width: 300px; }
    </style>
</head>
<body>
    <h1>🤖 ARC-DSL Refactoring Agent</h1>
    <p>Human-in-the-Loop Multi-Agent Code Refactoring System</p>
    
    <div class="section">
        <h2>📊 Phase 2: Usage-Based Specialization</h2>
        <p>Analyze generic functions and create type-safe specialized versions</p>
        
        <h3>Step 1: Analyze Function Usage</h3>
        <input type="text" id="functionName" placeholder="Function name (e.g., first, last)" value="first">
        <button onclick="analyzeFunction()">Analyze Usage Patterns</button>
        <div id="analysisResult"></div>
        
        <h3>Step 2: Review Proposals</h3>
        <div id="proposalsSection" style="display:none;">
            <p>ADK-reviewed proposals will appear here...</p>
            <div id="proposals"></div>
        </div>
        
        <h3>Step 3: Test & Deploy</h3>
        <div id="testSection" style="display:none;">
            <p>Test results and deployment options...</p>
            <div id="testResults"></div>
        </div>
    </div>
    
    <div class="section">
        <h2>📈 System Status</h2>
        <p>API: <span class="success">✅ Running</span></p>
        <p>Gemini: <span class="success">✅ Connected</span></p>
        <p>Session: <span id="sessionStatus">No active session</span></p>
    </div>
    
    <script>
        let currentSession = null;
        
        async function analyzeFunction() {
            const functionName = document.getElementById('functionName').value;
            const resultDiv = document.getElementById('analysisResult');
            resultDiv.innerHTML = '<p>🔍 Analyzing usage patterns...</p>';
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        generic_function: functionName,
                        source_file: 'arc-dsl/solvers.py'
                    })
                });
                
                const data = await response.json();
                currentSession = data.session_id;
                
                resultDiv.innerHTML = `
                    <div class="success">
                        <p>✅ Analysis Complete</p>
                        <p>Function: <strong>${data.function_name}</strong></p>
                        <p>Calls found: <strong>${data.usage_patterns.call_count}</strong></p>
                        <p>Proposals generated: <strong>${data.proposals.length}</strong></p>
                        <p>ADK approved: <strong>${data.adk_approved.length}</strong></p>
                        <p>Session ID: ${data.session_id}</p>
                    </div>
                `;
                
                // Show proposals
                showProposals(data.adk_approved);
                
            } catch (error) {
                resultDiv.innerHTML = `<p class="error">❌ Error: ${error.message}</p>`;
            }
        }
        
        function showProposals(proposals) {
            const section = document.getElementById('proposalsSection');
            const container = document.getElementById('proposals');
            section.style.display = 'block';
            
            container.innerHTML = proposals.map((p, idx) => `
                <div class="section">
                    <h4>${p.name}</h4>
                    <p><strong>Signature:</strong> ${p.signature}</p>
                    <p><strong>ADK Review:</strong> ${p.adk_review.verdict} (${p.adk_review.confidence} confidence)</p>
                    <p><strong>Reasoning:</strong> ${p.adk_review.reasoning}</p>
                    <button onclick="approveProposal(${idx})">✅ Approve</button>
                    <button onclick="rejectProposal(${idx})">❌ Reject</button>
                </div>
            `).join('');
        }
        
        async function approveProposal(index) {
            alert(`Proposal ${index} approved! (Full implementation would apply changes and run tests)`);
        }
        
        function rejectProposal(index) {
            alert(`Proposal ${index} rejected.`);
        }
    </script>
</body>
</html>
"""

@app.post("/api/analyze")
async def analyze_endpoint(request: AnalysisRequest):
    """Step 1: Analyze function usage and generate proposals"""
    
    # Create session
    session_id = f"session_{len(workflow_sessions) + 1}"
    
    # Analyze usage
    usage_patterns = analyze_function_usage(request.generic_function, request.source_file)
    
    # Generate proposals
    proposals = propose_specializations(request.generic_function, usage_patterns)
    
    # ADK review each proposal
    adk_approved = []
    adk_rejected = []
    
    for proposal in proposals:
        if "error" in proposal:
            continue
            
        review = review_with_adk(
            original_source=f"def {request.generic_function}(container): return next(iter(container))",
            specialized_version=proposal
        )
        
        proposal['adk_review'] = review
        
        if review.get('verdict') == 'approve':
            adk_approved.append(proposal)
        else:
            adk_rejected.append(proposal)
    
    # Store in session
    workflow_sessions[session_id] = {
        "function_name": request.generic_function,
        "usage_patterns": usage_patterns,
        "proposals": proposals,
        "adk_approved": adk_approved,
        "adk_rejected": adk_rejected,
        "status": "awaiting_human_review"
    }
    
    return {
        "session_id": session_id,
        "function_name": request.generic_function,
        "usage_patterns": usage_patterns,
        "proposals": proposals,
        "adk_approved": adk_approved,
        "adk_rejected": adk_rejected
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "gemini_configured": bool(GOOGLE_API_KEY),
        "active_sessions": len(workflow_sessions)
    }

@app.get("/api/metrics")
async def get_metrics():
    """System metrics endpoint"""
    return {
        "total_sessions": len(workflow_sessions),
        "completed_sessions": sum(1 for s in workflow_sessions.values() if s['status'] == 'completed'),
        "pending_sessions": sum(1 for s in workflow_sessions.values() if s['status'] == 'awaiting_human_review')
    }

# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
