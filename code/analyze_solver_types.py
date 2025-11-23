#!/usr/bin/env python3
"""
Type Inference Tool for ARC-DSL Solvers

This tool analyzes DSL function signatures and solver code to generate
type annotations that can be added through the HITL refactoring agent system.

Usage:
    python analyze_solver_types.py <solver_name>
    python analyze_solver_types.py --all  # Analyze all solvers
    python analyze_solver_types.py --export-json  # Export type mappings
"""

import ast
import inspect
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class DSLTypeAnalyzer:
    """Analyzes DSL functions to build type mappings."""
    
    def __init__(self, dsl_file='arc-dsl/dsl.py'):
        self.dsl_file = dsl_file
        self.type_mapping: Dict[str, str] = {}
        self.callable_functions = set()
        self._build_type_mapping()
    
    def _build_type_mapping(self):
        """Parse dsl.py to extract function return types."""
        with open(self.dsl_file, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                
                # Extract return type annotation
                if node.returns:
                    return_type = ast.unparse(node.returns)
                    self.type_mapping[func_name] = return_type
                    
                    # Track functions that return Callable
                    if 'Callable' in return_type:
                        self.callable_functions.add(func_name)
    
    def get_return_type(self, function_name: str) -> Optional[str]:
        """Get the return type of a DSL function."""
        return self.type_mapping.get(function_name)
    
    def is_callable_function(self, function_name: str) -> bool:
        """Check if a function returns a Callable."""
        return function_name in self.callable_functions
    
    def export_mapping(self, output_file='arc-dsl/dsl_type_mapping.json'):
        """Export type mapping to JSON for agent consumption."""
        data = {
            'type_mapping': self.type_mapping,
            'callable_functions': list(self.callable_functions)
        }
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Exported type mapping to {output_file}")
        return output_file


class SolverTypeInference:
    """Infers variable types in solver functions."""
    
    def __init__(self, dsl_analyzer: DSLTypeAnalyzer):
        self.dsl = dsl_analyzer
        self.constants_types = {
            'T': 'Boolean',
            'F': 'Boolean',
            'ZERO': 'Integer',
            'ONE': 'Integer',
            'TWO': 'Integer',
            'THREE': 'Integer',
            'FOUR': 'Integer',
            'FIVE': 'Integer',
            'SIX': 'Integer',
            'SEVEN': 'Integer',
            'EIGHT': 'Integer',
            'NINE': 'Integer',
            'TEN': 'Integer',
            'NEG_ONE': 'Integer',
            'NEG_TWO': 'Integer',
            'ORIGIN': 'IntegerTuple',
            'UNITY': 'IntegerTuple',
            'DOWN': 'IntegerTuple',
            'UP': 'IntegerTuple',
            'RIGHT': 'IntegerTuple',
            'LEFT': 'IntegerTuple',
            'ZERO_BY_TWO': 'IntegerTuple',
            'TWO_BY_ZERO': 'IntegerTuple',
            'TWO_BY_TWO': 'IntegerTuple',
            'THREE_BY_THREE': 'IntegerTuple',
        }
    
    def analyze_solver(self, solver_func, solver_name: str) -> Dict[str, Any]:
        """Analyze a solver function and infer variable types."""
        source = inspect.getsource(solver_func)
        lines = source.split('\n')
        
        # Parse function to extract variable assignments
        variables = {}
        variables['I'] = 'Grid'  # Input is always Grid
        
        for line in lines[1:-1]:  # Skip def line and return line
            line = line.strip()
            if ' = ' in line and not line.startswith('#'):
                var_name, expression = line.split(' = ', 1)
                var_name = var_name.strip()
                
                # Extract function call
                func_match = expression.split('(')[0].strip()
                
                # Infer type based on function return type
                if func_match in self.dsl.type_mapping:
                    var_type = self.dsl.type_mapping[func_match]
                    variables[var_name] = var_type
                elif func_match in self.constants_types:
                    # Direct constant assignment
                    variables[var_name] = self.constants_types[func_match]
                elif var_name == 'O':
                    # Output is always Grid
                    variables[var_name] = 'Grid'
        
        return {
            'solver_name': solver_name,
            'variables': variables,
            'has_callables': any(
                self.dsl.is_callable_function(func) 
                for line in lines 
                for func in line.split('(')[0].split()
                if func in self.dsl.callable_functions
            )
        }
    
    def generate_annotated_code(self, solver_func, solver_name: str) -> str:
        """Generate solver code with type annotations."""
        analysis = self.analyze_solver(solver_func, solver_name)
        source = inspect.getsource(solver_func)
        lines = source.split('\n')
        
        # Add TYPE_CHECKING import at top of file (to be added once)
        annotated_lines = []
        
        # Annotate function signature
        annotated_lines.append(f"def {solver_name}(I: Grid) -> Grid:")
        
        # Annotate each variable assignment
        for line in lines[1:]:
            stripped = line.strip()
            if ' = ' in stripped and not stripped.startswith('#') and not stripped.startswith('return'):
                var_name = stripped.split(' = ')[0].strip()
                if var_name in analysis['variables']:
                    var_type = analysis['variables'][var_name]
                    indent = len(line) - len(line.lstrip())
                    annotated_lines.append(f"{' ' * indent}{var_name}: {var_type} = {stripped.split(' = ', 1)[1]}")
                else:
                    annotated_lines.append(line.rstrip())
            else:
                annotated_lines.append(line.rstrip())
        
        return '\n'.join(annotated_lines)
    
    def generate_refactoring_script(self, solver_func, solver_name: str) -> Dict[str, str]:
        """Generate a refactoring script for the HITL agent system."""
        annotated_code = self.generate_annotated_code(solver_func, solver_name)
        analysis = self.analyze_solver(solver_func, solver_name)
        
        return {
            'file': 'arc-dsl/solvers.py',
            'solver': solver_name,
            'description': f'Add type annotations to {solver_name}',
            'script': f'''# Generated type annotation script for {solver_name}

# Parse the file to find the solver function
import re

lines = original_content.split('\\n')
new_lines = []
in_solver = False
solver_started = False

for i, line in enumerate(lines):
    if line.strip().startswith(f'def {solver_name}(I):'):
        # Replace function signature
        indent = len(line) - len(line.lstrip())
        new_lines.append(' ' * indent + f'def {solver_name}(I: Grid) -> Grid:')
        in_solver = True
        solver_started = True
    elif in_solver:
        # Check if we've reached the next function or end of file
        if line.strip().startswith('def ') and solver_started:
            in_solver = False
            new_lines.append(line)
        elif ' = ' in line and not line.strip().startswith('#') and not line.strip().startswith('return'):
            # Add type annotation to variable
            var_name = line.split(' = ')[0].strip()
            var_types = {json.dumps(analysis['variables'])}
            if var_name in var_types:
                indent = len(line) - len(line.lstrip())
                rest = line.split(' = ', 1)[1]
                new_lines.append(f"{{' ' * indent}}{{var_name}}: {{var_types[var_name]}} = {{rest}}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

new_content = '\\n'.join(new_lines)
''',
            'variables_annotated': len(analysis['variables']),
            'has_callables': analysis['has_callables']
        }


def main():
    """Main CLI interface."""
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    # Initialize analyzer
    print("🔍 Analyzing DSL type signatures...")
    dsl_analyzer = DSLTypeAnalyzer()
    print(f"   Found {len(dsl_analyzer.type_mapping)} DSL functions")
    print(f"   Identified {len(dsl_analyzer.callable_functions)} Callable-returning functions")
    
    if '--export-json' in sys.argv:
        output = dsl_analyzer.export_mapping()
        print(f"\n✅ Type mapping exported to: {output}")
        print("   This can be used by your refactoring agents!")
        return
    
    # Import solvers
    sys.path.insert(0, 'arc-dsl')
    import solvers
    
    inferencer = SolverTypeInference(dsl_analyzer)
    
    if '--all' in sys.argv:
        # Analyze all solvers
        solver_names = [name for name in dir(solvers) if name.startswith('solve_')]
        print(f"\n📊 Analyzing {len(solver_names)} solvers...")
        
        results = []
        for solver_name in solver_names[:5]:  # Show first 5 as examples
            solver_func = getattr(solvers, solver_name)
            analysis = inferencer.analyze_solver(solver_func, solver_name)
            results.append(analysis)
            print(f"\n{solver_name}:")
            print(f"  Variables: {len(analysis['variables'])}")
            print(f"  Has Callables: {analysis['has_callables']}")
            for var, vtype in list(analysis['variables'].items())[:3]:
                print(f"    {var}: {vtype}")
        
    else:
        # Analyze specific solver
        solver_name = sys.argv[1]
        if not solver_name.startswith('solve_'):
            solver_name = f'solve_{solver_name}'
        
        if not hasattr(solvers, solver_name):
            print(f"❌ Solver {solver_name} not found")
            return
        
        solver_func = getattr(solvers, solver_name)
        
        print(f"\n📋 Analysis for {solver_name}:")
        analysis = inferencer.analyze_solver(solver_func, solver_name)
        
        print(f"\nVariables ({len(analysis['variables'])}):")
        for var, vtype in analysis['variables'].items():
            print(f"  {var}: {vtype}")
        
        print(f"\nHas Callables: {analysis['has_callables']}")
        
        print(f"\n{'='*60}")
        print("Generated Annotated Code:")
        print('='*60)
        print(inferencer.generate_annotated_code(solver_func, solver_name))
        
        print(f"\n{'='*60}")
        print("HITL Refactoring Script Info:")
        print('='*60)
        script_info = inferencer.generate_refactoring_script(solver_func, solver_name)
        print(f"File: {script_info['file']}")
        print(f"Description: {script_info['description']}")
        print(f"Variables to annotate: {script_info['variables_annotated']}")


if __name__ == '__main__':
    main()
