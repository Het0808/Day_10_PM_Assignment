# 💼 Interview Answers — Scope, Memoization & Bugs

---

## Q1 — The LEGB Rule

### What is LEGB?

LEGB is Python's name resolution order — when Python encounters a variable name, it searches these scopes in order and stops at the first match:

```
┌─────────────────────────────────────────┐
│  L — Local                              │  ← searched first
│    variables defined inside the current │
│    function call frame                  │
├─────────────────────────────────────────┤
│  E — Enclosing                          │  ← closures / nested functions
│    variables in enclosing function      │
│    scopes (inner → outer)               │
├─────────────────────────────────────────┤
│  G — Global                             │  ← module-level names
│    names at the top of the .py file     │
├─────────────────────────────────────────┤
│  B — Built-in                           │  ← searched last
│    Python's builtins: print, len, etc.  │
└─────────────────────────────────────────┘
```

### Concrete Example

```python
x = "global_x"          # G

def outer():
    x = "enclosing_x"   # E  (enclosing scope for inner)

    def inner():
        x = "local_x"   # L  (local to inner)
        print(x)        # → "local_x"       (L found first)

    inner()
    print(x)            # → "enclosing_x"   (L gone, E found)

outer()
print(x)                # → "global_x"      (L & E gone, G found)
```

### Local vs Global Same Name

When a name exists in both local and global scope, the **local always wins** inside the function — the global is shadowed but never changed:

```python
count = 10              # G

def show():
    count = 99          # L — new local variable, shadows G
    print(count)        # → 99

show()
print(count)            # → 10  (G untouched)
```

---

### The `global` Keyword

`global name` tells Python: inside this function, treat `name` as the module-level variable rather than creating a local:

```python
total = 0

def increment():
    global total
    total += 1

increment()
print(total)   # → 1
```

### Why `global` is a Code Smell

1. **Hidden coupling** — function behaviour depends on invisible external state
2. **Not thread-safe** — concurrent calls can corrupt the shared global
3. **Untestable in isolation** — test outcome depends on global's current value
4. **Breaks re-entrancy** — can't safely call the function recursively

### The Pythonic Alternative

Return values instead of mutating globals; encapsulate shared state in a class:

```python
# ❌ global (code smell)
total = 0
def add(n):
    global total
    total += n

# ✅ pure function — explicit, testable, thread-safe
def add(total: int, n: int) -> int:
    return total + n

total = add(total, 5)

# ✅ class — encapsulate mutable state
class Cart:
    def __init__(self):
        self.total = 0
    def add(self, n: int) -> None:
        self.total += n
```

---

## Q2 — Memoize Decorator

```python
import functools
from typing import Callable, Any

def memoize(func: Callable) -> Callable:
    """
    Cache results of expensive function calls.
    Returns cached result when called with the same arguments.

    Args:
        func: The function to cache.

    Returns:
        Wrapped function with .cache dict and .cache_clear() method.

    Example:
        @memoize
        def fibonacci(n):
            if n <= 1: return n
            return fibonacci(n-1) + fibonacci(n-2)

        fibonacci(50)   # instant — O(n) instead of O(2^n)
    """
    cache: dict[tuple, Any] = {}

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    wrapper.cache_clear = cache.clear
    return wrapper


@memoize
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# fibonacci(50) = 12586269025  — computed instantly
# Cache holds exactly 51 entries (n=0..50)
# Without memoize: ~2^50 ≈ 1.1 quadrillion recursive calls
```

### Why It Works

Each unique `n` is computed once and stored. Subsequent recursive calls hit the cache in O(1). Time complexity drops from **O(2ⁿ)** → **O(n)**.

> In production, prefer `@functools.lru_cache(maxsize=None)` (or `@functools.cache` in Python 3.9+) which is implemented in C and handles edge cases.

---

## Q3 — Two Bugs: Mutable Default + Scope

### Buggy Code

```python
total = 0

def add_to_cart(item, cart=[]):      # Bug 1: mutable default
    cart.append(item)
    total = total + len(cart)         # Bug 2: scope issue
    return cart

print(add_to_cart('apple'))
print(add_to_cart('banana'))
```

---

### Bug 1 — Mutable Default Argument

**What the second call actually prints:** `['apple', 'banana']` — not `['banana']`.

**Why:** Default argument values are evaluated **once** when the `def` statement executes — not on every call. The `[]` is created once and stored inside the function object. Every call that uses the default `cart` mutates the **same list**.

```python
# Proof: inspect the function's default
print(add_to_cart.__defaults__)   # → (['apple', 'banana'],) ← same object persists
```

**Fix:** Use `None` as a sentinel — an immutable value that signals "no cart provided":

```python
def add_to_cart(item: str, cart: list | None = None):
    if cart is None:        # ✅ fresh list on every default call
        cart = []
    cart.append(item)
    ...
```

---

### Bug 2 — UnboundLocalError

**Error:** `UnboundLocalError: local variable 'total' referenced before assignment`

**Why:** The assignment `total = total + len(cart)` causes Python's compiler to classify `total` as **local** throughout the entire function — including the right-hand side. When that line first executes, the local `total` doesn't exist yet, so reading it raises `UnboundLocalError`.

This is Python's static scoping rule: if a name appears on the **left side of an assignment anywhere** in a function body, it is treated as local for the **entire** function scope.

**Fix:** Don't depend on global state — compute locally or use a class:

```python
# ✅ local variable, no global dependency
running_total = len(cart)
return cart, running_total
```

---

### Fully Fixed Version

```python
def add_to_cart(item: str, cart: list | None = None) -> tuple[list, int]:
    """
    Add item to cart; return (cart, total_item_count).

    Args:
        item: Item name to add.
        cart: Existing cart (creates new list if None).

    Returns:
        Tuple of (updated cart, number of items).
    """
    if cart is None:          # Bug 1 fixed: new list each default call
        cart = []
    cart.append(item)
    total = len(cart)         # Bug 2 fixed: purely local, no global
    return cart, total


c1, t1 = add_to_cart('apple')
c2, t2 = add_to_cart('banana')   # independent call — no shared state
print(c1, t1)   # ['apple'] 1
print(c2, t2)   # ['banana'] 1   ✅ now correct
```
