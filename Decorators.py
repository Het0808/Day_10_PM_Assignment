# ============================================================
#  decorators.py
#  Three production-grade decorators built from scratch
#  Covers: closures, functools.wraps, *args/**kwargs
# ============================================================

"""
SELF-STUDY: How Decorators Work
────────────────────────────────
A decorator is syntactic sugar for:

    @timer
    def my_func(): ...

which is exactly equivalent to:

    def my_func(): ...
    my_func = timer(my_func)

Three key concepts make decorators possible:

1. CLOSURES
   A closure is a function that remembers variables from its enclosing
   scope even after the outer function has returned.

        def outer(x):
            def inner():        # inner "closes over" x
                return x * 2
            return inner        # returns the function object

   Decorators exploit this: the wrapper function closes over `func`.

2. functools.wraps
   Without it, `my_func.__name__` becomes 'wrapper', breaking help(),
   introspection, and logging. @wraps(func) copies the original
   function's __name__, __doc__, __module__, __qualname__, __annotations__,
   and __wrapped__ onto the wrapper.

3. *args / **kwargs
   Allow a single wrapper to forward any argument signature unchanged:

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

   Without *args/**kwargs the decorator would only work for one
   specific function signature.
"""

import functools
import time
import logging
from typing import Callable, Any

# Set up module-level logger (self-study: logging module)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
_log = logging.getLogger("decorators")


# ─────────────────────────────────────────────────────────────
#  1. @timer
#     Measures and prints execution time of any function.
# ─────────────────────────────────────────────────────────────

def timer(func: Callable) -> Callable:
    """
    Decorator: measure and print execution time of any function.

    Attaches `.last_duration` attribute to the wrapper so tests
    can inspect timing programmatically.

    Args:
        func: The function to wrap.

    Returns:
        Wrapper function with identical signature.

    Example:
        @timer
        def slow_sort(lst):
            return sorted(lst)
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start  = time.perf_counter()
        result = func(*args, **kwargs)
        end    = time.perf_counter()
        duration = end - start
        wrapper.last_duration = duration
        print(f"⏱  {func.__name__!r} executed in {duration:.6f}s")
        return result

    wrapper.last_duration = 0.0   # initialise attribute
    return wrapper


# ─────────────────────────────────────────────────────────────
#  2. @logger
#     Logs function name, arguments, and return value.
# ─────────────────────────────────────────────────────────────

def logger(func: Callable) -> Callable:
    """
    Decorator: log function name, arguments, and return value.

    Uses Python's logging module (not print) so output integrates
    with application-level logging configuration.

    Args:
        func: The function to wrap.

    Returns:
        Wrapper function with identical signature.

    Example:
        @logger
        def add(a, b):
            return a + b
        # Logs: Calling add(1, 2) → 3
    """
    fn_log = logging.getLogger(func.__module__ or "app")

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Format args/kwargs for readable output
        arg_parts = [repr(a) for a in args]
        kwarg_parts = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(arg_parts + kwarg_parts)

        fn_log.debug(f"→ Calling {func.__name__}({signature})")
        result = func(*args, **kwargs)
        fn_log.debug(f"← {func.__name__} returned {result!r}")
        return result

    return wrapper


# ─────────────────────────────────────────────────────────────
#  3. @retry(max_attempts=3)
#     Retries a function on exception, with exponential back-off.
# ─────────────────────────────────────────────────────────────

def retry(max_attempts: int = 3, delay: float = 0.0, exceptions: tuple = (Exception,)):
    """
    Decorator factory: retry a function up to max_attempts times
    if it raises an exception.

    This is a *decorator factory* — it takes configuration parameters
    and RETURNS the actual decorator. That's why usage is @retry(max_attempts=3)
    rather than @retry.

    Args:
        max_attempts: Maximum number of total attempts (default 3).
        delay:        Seconds to wait between attempts (default 0).
                      Use exponential back-off in production.
        exceptions:   Tuple of exception types to catch (default: all).

    Returns:
        Decorator that wraps the target function with retry logic.

    Raises:
        The last exception raised if all attempts are exhausted.
        ValueError: If max_attempts < 1.

    Example:
        @retry(max_attempts=3, delay=0.5)
        def unstable_api_call():
            ...
    """
    if max_attempts < 1:
        raise ValueError(f"max_attempts must be ≥ 1, got {max_attempts}")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None

            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        print(f"✅ {func.__name__!r} succeeded on attempt {attempt}/{max_attempts}")
                    return result
                except exceptions as exc:
                    last_exc = exc
                    print(f"⚠️  {func.__name__!r} attempt {attempt}/{max_attempts} failed: {exc}")
                    if attempt < max_attempts and delay > 0:
                        time.sleep(delay)

            raise last_exc   # re-raise after all attempts exhausted

        return wrapper
    return decorator


# ─────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────

def _demo() -> None:
    print("\n" + "═" * 55)
    print("  @timer demo")
    print("═" * 55)

    @timer
    def bubble_sort(lst: list) -> list:
        """Intentionally slow sort for demo purposes."""
        lst = lst[:]
        for i in range(len(lst)):
            for j in range(len(lst) - i - 1):
                if lst[j] > lst[j + 1]:
                    lst[j], lst[j + 1] = lst[j + 1], lst[j]
        return lst

    bubble_sort(list(range(300, 0, -1)))
    print(f"  Stored duration: {bubble_sort.last_duration:.6f}s")
    print(f"  __name__ preserved: {bubble_sort.__name__!r}")   # functools.wraps check

    print("\n" + "═" * 55)
    print("  @logger demo")
    print("═" * 55)

    @logger
    def calculate_gpa(math: float, python: float) -> float:
        return round((math + python) / 2 / 10, 2)

    calculate_gpa(85, 92)
    calculate_gpa(math=90, python=88)
    print(f"  __name__ preserved: {calculate_gpa.__name__!r}")

    print("\n" + "═" * 55)
    print("  @retry demo")
    print("═" * 55)

    call_count = {"n": 0}

    @retry(max_attempts=4)
    def flaky_service() -> str:
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise ConnectionError("Service temporarily unavailable")
        return "SUCCESS"

    result = flaky_service()
    print(f"  Final result: {result!r}  (took {call_count['n']} calls)")
    print(f"  __name__ preserved: {flaky_service.__name__!r}")

    print("\n" + "═" * 55)
    print("  @retry exhausted — re-raises last exception")
    print("═" * 55)

    @retry(max_attempts=2)
    def always_fails():
        raise ValueError("Permanent failure")

    try:
        always_fails()
    except ValueError as e:
        print(f"  Caught expected exception: {e!r}")

    print()


if __name__ == "__main__":
    _demo()
