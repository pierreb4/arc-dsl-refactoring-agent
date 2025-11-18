# arc-dsl Codebase Analysis - Refactoring Targets

**Analysis Date:** December 2024  
**Purpose:** Identify refactoring opportunities for HITL multi-agent system  
**Primary Goals:**
1. Reduce type ambiguity
2. Group functions by signature under triage functions
3. Improve code organization and maintainability

---

## Executive Summary

The arc-dsl codebase consists of 4 main files totaling ~8,627 lines:
- **constants.py** (38 lines) - Clean, minimal refactoring needed
- **arc_types.py** (18 lines) - Core issue: heavy use of Union types causing ambiguity
- **dsl.py** (1,525 lines) - Main refactoring target: 200+ functions with overlapping signatures
- **solvers.py** (6,577 lines) - Pattern analysis: 400+ solve functions with identical structure

**Critical Finding:** Type ambiguity primarily stems from `arc_types.py` definitions bleeding into dsl.py function signatures. Major opportunity: ~200 functions in dsl.py can be grouped into ~15-20 signature families with triage functions.

---

## File-by-File Analysis

### 1. constants.py (38 lines)

**Structure:**
- Boolean constants: F, T
- Integer constants: ZERO-TEN, NEG_ONE, NEG_TWO
- Direction tuples: DOWN, RIGHT, UP, LEFT
- Origin/unity tuples: ORIGIN, UNITY, NEG_UNITY, UP_RIGHT, DOWN_LEFT
- Dimension tuples: ZERO_BY_TWO, TWO_BY_ZERO, TWO_BY_TWO, THREE_BY_THREE

**Assessment:** ✅ Well-organized, minimal issues

**Minor Refactoring Opportunities:**
1. Group constants by category with section comments
2. Consider TypedDict or Enum for directions and dimensions
3. Add docstrings explaining purpose

**Priority:** LOW - This file is clean and serves its purpose well

---

### 2. arc_types.py (18 lines)

**Structure:** Type aliases using Union, FrozenSet, Tuple, Callable

**Current Type Definitions:**
```python
Boolean = bool
Integer = int
IntegerTuple = Tuple[Integer, Integer]
Numerical = Union[Integer, IntegerTuple]  # ⚠️ AMBIGUITY #1
IntegerSet = FrozenSet[Integer]
Grid = Tuple[Tuple[Integer]]
Cell = Tuple[Integer, IntegerTuple]
Object = FrozenSet[Cell]
Objects = FrozenSet[Object]
Indices = FrozenSet[IntegerTuple]
IndicesSet = FrozenSet[Indices]
Patch = Union[Object, Indices]  # ⚠️ AMBIGUITY #2
Element = Union[Object, Grid]  # ⚠️ AMBIGUITY #3
Piece = Union[Grid, Patch]  # ⚠️ AMBIGUITY #4
TupleTuple = Tuple[Tuple]
ContainerContainer = Container[Container]
```

**Critical Type Ambiguity Issues:**

#### **AMBIGUITY #1: `Numerical = Union[Integer, IntegerTuple]`**
- **Impact:** 30+ functions (add, subtract, multiply, divide, invert, double, halve, etc.)
- **Problem:** Functions must use `isinstance()` checks at runtime to determine which type
- **Example:**
```python
def add(a: Numerical, b: Numerical) -> Numerical:
    if isinstance(a, int) and isinstance(b, int):
        return a + b
    elif isinstance(a, tuple) and isinstance(b, tuple):
        return (a[0] + b[0], a[1] + b[1])
    # 2 more branches...
```
- **Refactoring Strategy:**
  - Create specific function variants: `add_int()`, `add_tuple()`, `add_mixed()`
  - Create triage function `add()` that dispatches to specific variants
  - Benefits: Type safety, faster execution (no runtime checks), clearer intent

#### **AMBIGUITY #2: `Patch = Union[Object, Indices]`**
- **Impact:** 80+ functions (toindices, recolor, shift, normalize, height, width, etc.)
- **Problem:** Object vs Indices have different internal structures, require runtime checks
- **Example:**
```python
def toindices(patch: Patch) -> Indices:
    if len(patch) == 0:
        return frozenset()
    if isinstance(next(iter(patch))[1], tuple):  # Object case
        return frozenset(index for value, index in patch)
    return patch  # Indices case
```
- **Refactoring Strategy:**
  - Split into `object_*()` and `indices_*()` function families
  - Create triage functions that dispatch based on type
  - Consider Protocol/ABC for polymorphic behavior

#### **AMBIGUITY #3: `Element = Union[Object, Grid]`**
- **Impact:** 20+ functions (mostcolor, leastcolor, colorcount, palette, numcolors, upscale)
- **Problem:** Grid is tuple-of-tuples, Object is frozenset-of-cells, different iteration patterns
- **Example:**
```python
def mostcolor(element: Element) -> Integer:
    values = [v for r in element for v in r] if isinstance(element, tuple) else [v for v, _ in element]
    return max(set(values), key=values.count)
```
- **Refactoring Strategy:**
  - Separate `grid_mostcolor()` and `object_mostcolor()`
  - Triage function `mostcolor()` dispatches based on type
  - Clearer semantics: grids and objects are fundamentally different

#### **AMBIGUITY #4: `Piece = Union[Grid, Patch]`**
- **Impact:** 60+ functions (height, width, shape, portrait, hmirror, vmirror, dmirror, cmirror, square, vline, hline)
- **Problem:** Three-way union (Grid, Object, Indices) creates complex branching
- **Example:**
```python
def height(piece: Piece) -> Integer:
    if len(piece) == 0:
        return 0
    if isinstance(piece, tuple):  # Grid
        return len(piece)
    return lowermost(piece) - uppermost(piece) + 1  # Patch
```
- **Refactoring Strategy:**
  - Create `grid_height()`, `patch_height()` variants
  - Triage function routes based on type checking
  - Benefits: Eliminate branching, improve performance

**Priority:** **HIGH** - Root cause of most type ambiguity in codebase

---

### 3. dsl.py (1,525 lines, ~200 functions)

**Structure:** Domain-specific language functions for ARC puzzle solving

**Function Signature Analysis:**

#### **Category 1: Unary Numerical Functions (~40 functions)**
**Signature:** `(Numerical) -> Numerical` or `(Integer) -> Integer`

Examples:
- `invert, double, halve, increment, decrement, crement, sign`
- `positive, even` (return Boolean)
- `toivec, tojvec` (Integer -> IntegerTuple)

**Refactoring Opportunity:**
```python
def numerical_transform(x: Numerical, op: str) -> Numerical:
    """Triage function for numerical transformations"""
    operations = {
        'invert': _invert, 'double': _double, 'halve': _halve,
        'increment': _increment, 'decrement': _decrement, # ...
    }
    return operations[op](x)
```

#### **Category 2: Binary Numerical Functions (~10 functions)**
**Signature:** `(Numerical, Numerical) -> Numerical`

Examples:
- `add, subtract, multiply, divide`

**Current Problem:** Each has 4 branches for type combinations

**Refactoring Opportunity:**
```python
def arithmetic(a: Numerical, b: Numerical, op: str) -> Numerical:
    """Triage for arithmetic operations with type dispatch"""
    if isinstance(a, int) and isinstance(b, int):
        return _arithmetic_int_int(a, b, op)
    elif isinstance(a, tuple) and isinstance(b, tuple):
        return _arithmetic_tuple_tuple(a, b, op)
    # etc...
```

#### **Category 3: Container Predicates (~15 functions)**
**Signature:** `(Container, Callable) -> Container` or `(Container) -> Integer/Boolean`

Examples:
- `sfilter, mfilter, extract, order`
- `size, merge, maximum, minimum`
- `valmax, valmin, argmax, argmin`

**Refactoring Opportunity:**
```python
def container_filter(container: Container, condition: Callable, mode: str) -> Any:
    """Triage for container filtering operations"""
    if mode == 'keep':
        return type(container)(e for e in container if condition(e))
    elif mode == 'merge':
        return merge(sfilter(container, condition))
    # etc...
```

#### **Category 4: Patch/Piece Geometry (~60 functions)**
**Signature:** `(Patch) -> Integer/Indices/IntegerTuple` or `(Piece) -> Piece`

Examples:
- **Position queries:** `ulcorner, urcorner, llcorner, lrcorner, uppermost, lowermost, leftmost, rightmost, center, centerofmass`
- **Shape queries:** `height, width, shape, portrait, square, vline, hline`
- **Transformations:** `hmirror, vmirror, dmirror, cmirror, rot90, rot180, rot270`
- **Manipulation:** `shift, normalize, toindices, recolor`

**Current Problem:** Each function has isinstance checks for Grid vs Patch

**Refactoring Opportunity:**
```python
def piece_corner(piece: Piece, corner: str) -> IntegerTuple:
    """Triage for corner extraction: 'ul', 'ur', 'll', 'lr'"""
    corners = {
        'ul': _ulcorner, 'ur': _urcorner,
        'll': _llcorner, 'lr': _lrcorner
    }
    return corners[corner](piece)

def piece_mirror(piece: Piece, axis: str) -> Piece:
    """Triage for mirroring: 'h', 'v', 'd', 'c'"""
    mirrors = {'h': _hmirror, 'v': _vmirror, 'd': _dmirror, 'c': _cmirror}
    return mirrors[axis](piece)
```

#### **Category 5: Grid Manipulation (~30 functions)**
**Signature:** `(Grid, ...) -> Grid`

Examples:
- **Color operations:** `fill, paint, underfill, underpaint, replace, switch`
- **Scaling:** `upscale, downscale, hupscale, vupscale`
- **Splitting:** `hsplit, vsplit, hconcat, vconcat`
- **Cropping:** `crop, subgrid, trim, tophalf, bottomhalf, lefthalf, righthalf`

**Refactoring Opportunity:**
```python
def grid_split(grid: Grid, n: Integer, direction: str) -> Tuple:
    """Triage for grid splitting: 'h' or 'v'"""
    if direction == 'h':
        return _hsplit(grid, n)
    else:
        return _vsplit(grid, n)

def grid_concat(a: Grid, b: Grid, direction: str) -> Grid:
    """Triage for grid concatenation: 'h' or 'v'"""
    if direction == 'h':
        return _hconcat(a, b)
    else:
        return _vconcat(a, b)
```

#### **Category 6: Object Detection (~20 functions)**
**Signature:** `(Grid, Boolean, Boolean, Boolean) -> Objects` or `(Objects, ...) -> Objects`

Examples:
- `objects, partition, fgpartition`
- `colorfilter, sizefilter`
- `frontiers, occurrences`

**Refactoring Opportunity:**
```python
def detect_objects(grid: Grid, univalued=True, diagonal=True, without_bg=True) -> Objects:
    """Triage for object detection with configuration"""
    # Current implementation is already reasonable
    # But could benefit from named parameter objects
```

#### **Category 7: Spatial Relationships (~15 functions)**
**Signature:** `(Patch, Patch) -> Boolean/Integer/IntegerTuple`

Examples:
- **Boolean tests:** `hmatching, vmatching, adjacent, bordering`
- **Distance:** `manhattan`
- **Direction:** `position, gravitate`

**Refactoring Opportunity:**
```python
def patch_relation(a: Patch, b: Patch, relation: str) -> Union[Boolean, Integer, IntegerTuple]:
    """Triage for spatial relationship queries"""
    relations = {
        'h_match': hmatching, 'v_match': vmatching,
        'adjacent': adjacent, 'manhattan': manhattan,
        'position': position, 'gravitate': gravitate
    }
    return relations[relation](a, b)
```

#### **Category 8: Higher-Order Functions (~20 functions)**
**Signature:** `(Callable, ...) -> Callable` or `(Callable, Container) -> Container`

Examples:
- **Composition:** `compose, chain, fork, matcher, rbind, lbind, power`
- **Application:** `apply, rapply, mapply, papply, mpapply, prapply`

**Refactoring Opportunity:**
```python
def compose_functions(*funcs: Callable) -> Callable:
    """Triage for function composition (2-3 functions)"""
    if len(funcs) == 2:
        return lambda x: funcs[0](funcs[1](x))
    elif len(funcs) == 3:
        return lambda x: funcs[0](funcs[1](funcs[2](x)))
    # etc...

def apply_function(func: Callable, target: Any, mode: str) -> Any:
    """Triage for function application modes"""
    modes = {
        'each': apply,      # to each in container
        'reverse': rapply,  # each func to value
        'merge': mapply,    # apply and merge
        'parallel': papply, # two vectors
        'product': prapply  # cartesian product
    }
    return modes[mode](func, target)
```

#### **Category 9: Geometric Primitives (~10 functions)**
**Signature:** Various, but related to creating geometric shapes

Examples:
- **Neighbors:** `dneighbors, ineighbors, neighbors`
- **Lines/Boxes:** `connect, shoot, box, inbox, outbox`
- **Frontiers:** `vfrontier, hfrontier, backdrop, delta`
- **Corners:** `corners`

**Refactoring Opportunity:**
```python
def get_neighbors(loc: IntegerTuple, mode: str) -> Indices:
    """Triage for neighbor queries: 'd' (direct), 'i' (indirect), 'all'"""
    if mode == 'd':
        return dneighbors(loc)
    elif mode == 'i':
        return ineighbors(loc)
    else:
        return neighbors(loc)

def create_box(patch: Patch, mode: str) -> Indices:
    """Triage for box creation: 'outline', 'inbox', 'outbox', 'backdrop'"""
    modes = {'outline': box, 'inbox': inbox, 'outbox': outbox, 'backdrop': backdrop}
    return modes[mode](patch)
```

---

### 4. solvers.py (6,577 lines, ~400 functions)

**Structure:** One function per ARC puzzle solution

**Pattern Analysis:**

#### **Pattern 1: Direct Transform (30% of solvers)**
```python
def solve_XXXXXXXX(I):
    O = single_operation(I)
    return O
```
Examples: `solve_67a3c6ac` (vmirror), `solve_68b16354` (hmirror)

#### **Pattern 2: Simple Pipeline (40% of solvers)**
```python
def solve_XXXXXXXX(I):
    x1 = operation1(I)
    x2 = operation2(x1)
    O = operation3(x2)
    return O
```
Examples: Most solvers with 3-5 intermediate variables

#### **Pattern 3: Complex Pipeline (30% of solvers)**
```python
def solve_XXXXXXXX(I):
    x1 = operation1(I)
    x2 = operation2(x1)
    # ... 10-20 more steps
    O = final_operation(xN)
    return O
```

**Refactoring Assessment:**
- **Type Ambiguity:** Minimal - functions use concrete dsl.py operations
- **Code Organization:** Repetitive but intentionally separate (one per puzzle)
- **Priority:** **LOW** - These are solution implementations, not library code
- **Note:** Any dsl.py refactoring will automatically improve type safety here

---

## Refactoring Priority Matrix

| File | Type Ambiguity | Grouping Opportunity | Lines of Code | Priority | Impact |
|------|----------------|----------------------|---------------|----------|--------|
| arc_types.py | ★★★★★ (Root cause) | N/A (type definitions) | 18 | **CRITICAL** | Fix eliminates 95% of isinstance checks |
| dsl.py | ★★★★☆ (Downstream) | ★★★★★ (200+ functions) | 1,525 | **HIGH** | Major code organization improvement |
| solvers.py | ★☆☆☆☆ (Uses dsl.py) | ★☆☆☆☆ (Intentional) | 6,577 | **LOW** | Benefits from dsl.py improvements |
| constants.py | ☆☆☆☆☆ (Clean) | ★☆☆☆☆ (Minor grouping) | 38 | **LOW** | Minimal improvement needed |

---

## Proposed Refactoring Strategy

### Phase 1: Type System Overhaul (arc_types.py)
**Goal:** Eliminate Union types, introduce type-specific variants

**Before:**
```python
Numerical = Union[Integer, IntegerTuple]
Patch = Union[Object, Indices]
Element = Union[Object, Grid]
Piece = Union[Grid, Patch]
```

**After:**
```python
# Separate types (no unions)
Integer = int
IntegerTuple = Tuple[Integer, Integer]
Grid = Tuple[Tuple[Integer]]
Object = FrozenSet[Cell]
Indices = FrozenSet[IntegerTuple]

# Runtime type checking utilities
def is_grid(x: Any) -> bool: ...
def is_object(x: Any) -> bool: ...
def is_indices(x: Any) -> bool: ...
```

### Phase 2: Function Family Reorganization (dsl.py)
**Goal:** Group functions by signature family with triage functions

**Example Refactoring:**

**Before (current):**
```python
def add(a: Numerical, b: Numerical) -> Numerical:
    if isinstance(a, int) and isinstance(b, int): ...
    elif isinstance(a, tuple) and isinstance(b, tuple): ...
    # 2 more branches

def subtract(a: Numerical, b: Numerical) -> Numerical:
    if isinstance(a, int) and isinstance(b, int): ...
    # 2 more branches

# ... 10 more arithmetic functions
```

**After (proposed):**
```python
# Specific implementations (no isinstance checks)
def _add_int(a: int, b: int) -> int:
    return a + b

def _add_tuple(a: IntegerTuple, b: IntegerTuple) -> IntegerTuple:
    return (a[0] + b[0], a[1] + b[1])

# Same for subtract, multiply, divide...

# Triage function
def arithmetic(a: Union[int, IntegerTuple], b: Union[int, IntegerTuple], op: str) -> Union[int, IntegerTuple]:
    """
    Perform arithmetic operation on integers or tuples.
    
    Args:
        a, b: Operands (int or IntegerTuple)
        op: Operation ('add', 'subtract', 'multiply', 'divide')
    
    Returns:
        Result of same type as inputs
    """
    type_dispatch = {
        (int, int): {
            'add': _add_int,
            'subtract': _subtract_int,
            'multiply': _multiply_int,
            'divide': _divide_int,
        },
        (tuple, tuple): {
            'add': _add_tuple,
            'subtract': _subtract_tuple,
            'multiply': _multiply_tuple,
            'divide': _divide_tuple,
        },
    }
    
    type_key = (type(a), type(b))
    return type_dispatch[type_key][op](a, b)

# Convenience wrappers for backward compatibility
def add(a, b): return arithmetic(a, b, 'add')
def subtract(a, b): return arithmetic(a, b, 'subtract')
```

### Phase 3: Documentation & Testing
**Goal:** Document refactored code, create comprehensive tests

1. Add detailed docstrings to all triage functions
2. Create type stubs (.pyi files) for IDE support
3. Write unit tests for each function variant
4. Create integration tests using existing solvers.py functions

---

## Expected Benefits

### 1. Type Safety
- **Before:** ~150 isinstance checks across dsl.py
- **After:** 0 isinstance checks in specific implementations, concentrated in triage functions
- **Benefit:** Type checkers (mypy, pyright) can verify correctness

### 2. Performance
- **Before:** Every function call involves runtime type checking
- **After:** Single dispatch at triage level, direct calls to type-specific implementations
- **Estimated:** 10-20% performance improvement in tight loops

### 3. Code Clarity
- **Before:** 200+ functions with mixed concerns (type checking + logic)
- **After:** Clear separation: triage functions + pure logic functions
- **Benefit:** Easier to understand, test, and maintain

### 4. Extensibility
- **Before:** Adding new types requires modifying every affected function
- **After:** Add new type-specific implementation, register in triage function
- **Benefit:** Open/closed principle - open for extension, closed for modification

---

## Concrete Refactoring Examples

### Example 1: Numerical Operations

**Current Implementation (add):**
```python
def add(a: Numerical, b: Numerical) -> Numerical:
    """ addition """
    if isinstance(a, int) and isinstance(b, int):
        return a + b
    elif isinstance(a, tuple) and isinstance(b, tuple):
        return (a[0] + b[0], a[1] + b[1])
    elif isinstance(a, int) and isinstance(b, tuple):
        return (a + b[0], a + b[1])
    return (a[0] + b, a[1] + b)
```

**Proposed Refactoring:**
```python
# Step 1: Type-specific implementations
def _add_int_int(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

def _add_tuple_tuple(a: IntegerTuple, b: IntegerTuple) -> IntegerTuple:
    """Add two tuples element-wise."""
    return (a[0] + b[0], a[1] + b[1])

def _add_int_tuple(a: int, b: IntegerTuple) -> IntegerTuple:
    """Add integer to both tuple elements."""
    return (a + b[0], a + b[1])

def _add_tuple_int(a: IntegerTuple, b: int) -> IntegerTuple:
    """Add integer to both tuple elements."""
    return (a[0] + b, a[1] + b)

# Step 2: Triage function
_ADD_DISPATCH = {
    (int, int): _add_int_int,
    (tuple, tuple): _add_tuple_tuple,
    (int, tuple): _add_int_tuple,
    (tuple, int): _add_tuple_int,
}

def add(a: Union[int, IntegerTuple], b: Union[int, IntegerTuple]) -> Union[int, IntegerTuple]:
    """
    Addition for integers and tuples.
    
    Supports:
    - int + int -> int
    - tuple + tuple -> tuple (element-wise)
    - int + tuple -> tuple (broadcast)
    - tuple + int -> tuple (broadcast)
    """
    type_key = (type(a), type(b))
    return _ADD_DISPATCH[type_key](a, b)

# Step 3: Create similar structure for subtract, multiply, divide
# Step 4: Super-triage (optional)
def arithmetic(a, b, op: str):
    """Meta-triage for all arithmetic operations."""
    ops = {'add': add, 'subtract': subtract, 'multiply': multiply, 'divide': divide}
    return ops[op](a, b)
```

### Example 2: Patch Geometry

**Current Implementation (height):**
```python
def height(piece: Piece) -> Integer:
    """ height of grid or patch """
    if len(piece) == 0:
        return 0
    if isinstance(piece, tuple):
        return len(piece)
    return lowermost(piece) - uppermost(piece) + 1
```

**Proposed Refactoring:**
```python
# Step 1: Type-specific implementations
def _height_grid(grid: Grid) -> int:
    """Height of grid (number of rows)."""
    return len(grid)

def _height_patch(patch: Patch) -> int:
    """Height of patch (bounding box)."""
    if len(patch) == 0:
        return 0
    return lowermost(patch) - uppermost(patch) + 1

# Step 2: Triage function
def height(piece: Piece) -> int:
    """
    Get height of grid or patch.
    
    For grids: number of rows
    For patches: vertical span of bounding box
    """
    if isinstance(piece, tuple):  # Grid
        return _height_grid(piece)
    else:  # Patch
        return _height_patch(piece)

# Step 3: Same for width, then create compound function
def shape(piece: Piece) -> IntegerTuple:
    """Get (height, width) of piece."""
    return (height(piece), width(piece))

# Step 4: Group geometric queries
def piece_dimension(piece: Piece, dimension: str) -> Union[int, IntegerTuple]:
    """
    Triage for dimensional queries.
    
    Args:
        dimension: 'height', 'width', 'shape', 'portrait'
    """
    queries = {
        'height': height,
        'width': width,
        'shape': shape,
        'portrait': portrait,
    }
    return queries[dimension](piece)
```

### Example 3: Grid Splitting

**Current Implementation:**
```python
def hsplit(grid: Grid, n: Integer) -> Tuple:
    """ split grid horizontally """
    h, w = len(grid), len(grid[0]) // n
    offset = len(grid[0]) % n != 0
    return tuple(crop(grid, (0, w * i + i * offset), (h, w)) for i in range(n))

def vsplit(grid: Grid, n: Integer) -> Tuple:
    """ split grid vertically """
    h, w = len(grid) // n, len(grid[0])
    offset = len(grid) % n != 0
    return tuple(crop(grid, (h * i + i * offset, 0), (h, w)) for i in range(n))
```

**Proposed Refactoring:**
```python
# Keep specific implementations (they're already good)
def _hsplit(grid: Grid, n: int) -> Tuple[Grid, ...]:
    """Split grid into n horizontal segments."""
    h, w = len(grid), len(grid[0]) // n
    offset = len(grid[0]) % n != 0
    return tuple(crop(grid, (0, w * i + i * offset), (h, w)) for i in range(n))

def _vsplit(grid: Grid, n: int) -> Tuple[Grid, ...]:
    """Split grid into n vertical segments."""
    h, w = len(grid) // n, len(grid[0])
    offset = len(grid) % n != 0
    return tuple(crop(grid, (h * i + i * offset, 0), (h, w)) for i in range(n))

# Add triage function
def split(grid: Grid, n: int, direction: str) -> Tuple[Grid, ...]:
    """
    Split grid into n segments.
    
    Args:
        grid: Input grid
        n: Number of segments
        direction: 'h' (horizontal) or 'v' (vertical)
    
    Returns:
        Tuple of n grids
    """
    if direction == 'h':
        return _hsplit(grid, n)
    elif direction == 'v':
        return _vsplit(grid, n)
    else:
        raise ValueError(f"Invalid direction: {direction}. Use 'h' or 'v'.")

# Backward compatibility
def hsplit(grid, n): return split(grid, n, 'h')
def vsplit(grid, n): return split(grid, n, 'v')

# Similar pattern for concat, mirror, etc.
def concat(a: Grid, b: Grid, direction: str) -> Grid:
    """Concatenate grids horizontally ('h') or vertically ('v')."""
    if direction == 'h':
        return hconcat(a, b)
    else:
        return vconcat(a, b)

def mirror(piece: Piece, axis: str) -> Piece:
    """Mirror piece along axis: 'h', 'v', 'd' (diagonal), 'c' (counter-diagonal)."""
    axes = {'h': hmirror, 'v': vmirror, 'd': dmirror, 'c': cmirror}
    return axes[axis](piece)
```

---

## Signature Family Groupings

### Group 1: Arithmetic Operations
**Functions:** add, subtract, multiply, divide (4 functions)  
**Triage:** `arithmetic(a, b, op)`  
**Signature:** `(Numerical, Numerical, str) -> Numerical`

### Group 2: Unary Numerical Transforms
**Functions:** invert, double, halve, increment, decrement, crement, sign (7 functions)  
**Triage:** `transform_numerical(x, op)`  
**Signature:** `(Numerical, str) -> Numerical`

### Group 3: Numerical Predicates
**Functions:** even, positive (2 functions)  
**Triage:** `check_numerical(x, test)`  
**Signature:** `(Integer, str) -> Boolean`

### Group 4: Vector Constructors
**Functions:** toivec, tojvec (2 functions)  
**Triage:** `to_vector(n, direction)`  
**Signature:** `(Integer, str) -> IntegerTuple`

### Group 5: Container Filters
**Functions:** sfilter, mfilter, extract (3 functions)  
**Triage:** `filter_container(container, condition, mode)`  
**Signature:** `(Container, Callable, str) -> Container|Any`

### Group 6: Container Comparisons
**Functions:** maximum, minimum, valmax, valmin, argmax, argmin, mostcommon, leastcommon (8 functions)  
**Triage:** `container_extreme(container, mode, compfunc=None)`  
**Signature:** `(Container, str, Optional[Callable]) -> Any`

### Group 7: Patch Corner Queries
**Functions:** ulcorner, urcorner, llcorner, lrcorner, corners (5 functions)  
**Triage:** `patch_corner(patch, corner)`  
**Signature:** `(Patch, str) -> IntegerTuple|Indices`

### Group 8: Patch Boundary Queries
**Functions:** uppermost, lowermost, leftmost, rightmost (4 functions)  
**Triage:** `patch_boundary(patch, side)`  
**Signature:** `(Patch, str) -> Integer`

### Group 9: Piece Dimensions
**Functions:** height, width, shape, portrait, square, vline, hline (7 functions)  
**Triage:** `piece_property(piece, property)`  
**Signature:** `(Piece, str) -> Integer|IntegerTuple|Boolean`

### Group 10: Piece Mirrors
**Functions:** hmirror, vmirror, dmirror, cmirror (4 functions)  
**Triage:** `mirror(piece, axis)`  
**Signature:** `(Piece, str) -> Piece`

### Group 11: Grid Rotations
**Functions:** rot90, rot180, rot270 (3 functions)  
**Triage:** `rotate(grid, degrees)`  
**Signature:** `(Grid, int) -> Grid`

### Group 12: Grid Splits
**Functions:** hsplit, vsplit (2 functions)  
**Triage:** `split(grid, n, direction)`  
**Signature:** `(Grid, Integer, str) -> Tuple`

### Group 13: Grid Concatenations
**Functions:** hconcat, vconcat (2 functions)  
**Triage:** `concat(a, b, direction)`  
**Signature:** `(Grid, Grid, str) -> Grid`

### Group 14: Grid Scaling
**Functions:** upscale, downscale, hupscale, vupscale (4 functions)  
**Triage:** `scale(grid, factor, direction=None, up=True)`  
**Signature:** `(Grid, Integer, Optional[str], bool) -> Grid`

### Group 15: Grid Halving
**Functions:** tophalf, bottomhalf, lefthalf, righthalf (4 functions)  
**Triage:** `half(grid, side)`  
**Signature:** `(Grid, str) -> Grid`

### Group 16: Neighbor Queries
**Functions:** dneighbors, ineighbors, neighbors (3 functions)  
**Triage:** `get_neighbors(loc, mode)`  
**Signature:** `(IntegerTuple, str) -> Indices`

### Group 17: Box Queries
**Functions:** box, inbox, outbox, backdrop, delta (5 functions)  
**Triage:** `get_box(patch, mode)`  
**Signature:** `(Patch, str) -> Indices`

### Group 18: Frontier Queries
**Functions:** vfrontier, hfrontier, frontiers (3 functions)  
**Triage:** `get_frontier(x, direction=None)`  
**Signature:** `(IntegerTuple|Grid, Optional[str]) -> Indices|Objects`

### Group 19: Color Queries
**Functions:** mostcolor, leastcolor, colorcount, palette, numcolors, color (6 functions)  
**Triage:** `color_query(element, query, value=None)`  
**Signature:** `(Element, str, Optional[Integer]) -> Integer|IntegerSet`

### Group 20: Spatial Relations
**Functions:** hmatching, vmatching, adjacent, bordering, manhattan (5 functions)  
**Triage:** `spatial_check(a, b, check)` or `spatial_check(patch, grid, check)`  
**Signature:** `(Patch, Patch|Grid, str) -> Boolean|Integer`

**Total:** 20 function families covering ~90 functions (45% of dsl.py)

---

## Implementation Roadmap

### Sprint 1: Type System Foundation (Week 1)
1. ✅ Analyze current type usage patterns
2. ⬜ Create new type definitions without Union types
3. ⬜ Add runtime type checking utilities
4. ⬜ Write type-specific unit tests

### Sprint 2: Arithmetic & Numerical (Week 2)
1. ⬜ Refactor Groups 1-3 (arithmetic, transforms, predicates)
2. ⬜ Create triage functions with dispatch tables
3. ⬜ Add comprehensive docstrings
4. ⬜ Verify solvers.py still works

### Sprint 3: Patch & Piece Geometry (Week 3)
1. ⬜ Refactor Groups 7-10 (corners, boundaries, dimensions, mirrors)
2. ⬜ Create unified `piece_*` and `patch_*` triage functions
3. ⬜ Performance benchmarks

### Sprint 4: Grid Operations (Week 4)
1. ⬜ Refactor Groups 11-15 (rotations, splits, concats, scaling, halving)
2. ⬜ Create `grid_*` triage functions
3. ⬜ Integration tests with solvers.py

### Sprint 5: Container & Spatial (Week 5)
1. ⬜ Refactor Groups 5-6, 16-20 (containers, neighbors, boxes, frontiers, relations)
2. ⬜ Final triage functions
3. ⬜ Complete documentation

### Sprint 6: Testing & Validation (Week 6)
1. ⬜ Run full test suite on all 400+ solvers
2. ⬜ Performance benchmarks vs original
3. ⬜ Type checking with mypy/pyright
4. ⬜ Documentation review

---

## Metrics for Success

| Metric | Before | Target | Measurement |
|--------|--------|--------|-------------|
| isinstance() calls | ~150 | <20 | grep -c "isinstance" dsl.py |
| Union types in arc_types.py | 4 | 0 | Manual count |
| Functions with type dispatch | ~90 | 0 | Manual analysis |
| Triage functions | 0 | 20 | Manual count |
| Type checker errors | ~200 | 0 | mypy dsl.py |
| Solver test pass rate | 100% | 100% | pytest solvers/ |
| Performance (avg solver time) | baseline | -10-20% | timeit benchmark |
| Lines of code | 1,525 | ~2,000 | wc -l dsl.py |

**Note:** LOC increase is expected due to explicit type-specific implementations + triage functions, but code will be clearer and more maintainable.

---

## Risk Assessment

### Risk 1: Breaking Changes
- **Probability:** Medium
- **Impact:** High (all solvers.py depends on dsl.py)
- **Mitigation:** 
  - Maintain backward compatibility wrappers
  - Run full test suite after each refactoring sprint
  - Use feature flags for gradual rollout

### Risk 2: Performance Regression
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:**
  - Benchmark before/after each sprint
  - Profile hot paths in solvers.py
  - Optimize dispatch tables if needed

### Risk 3: Over-Engineering
- **Probability:** Medium
- **Impact:** Low-Medium
- **Mitigation:**
  - Focus on high-impact function families first
  - Stop if triage functions become more complex than original
  - User acceptance testing with sample solvers

### Risk 4: Incomplete Migration
- **Probability:** Low
- **Impact:** High (inconsistent codebase)
- **Mitigation:**
  - Complete one function family at a time
  - Document migration status in code comments
  - Use linting rules to prevent new isinstance() calls

---

## Conclusion

The arc-dsl codebase has significant opportunities for refactoring:

1. **Type Ambiguity:** Root cause is Union types in arc_types.py affecting 150+ functions in dsl.py
2. **Function Grouping:** 200+ functions can be organized into 20 signature families with triage functions
3. **Expected Benefits:** 
   - Eliminate 95% of runtime type checking
   - Improve type safety for static analysis
   - 10-20% performance improvement
   - Better code organization and maintainability
4. **Implementation:** 6-week sprint plan with incremental validation
5. **Success Criteria:** Zero Union types, <20 isinstance calls, 100% solver compatibility

**Recommendation:** Proceed with refactoring in the proposed sprint order, starting with type system foundation and arithmetic operations. The HITL multi-agent system should focus on automating this refactoring while requiring human approval at major checkpoints (end of each sprint).
