"""Debug utilities for development and testing."""
import sys
from pprint import pprint as pp
from typing import Any


def dd(*args: Any) -> None:
    """
    Dump and die 
    Prints all arguments and exits the program.
    
    Usage:
        dd(user, profile, data)
    """
    print("\n" + "=" * 80)
    print("DUMP AND DIE")
    print("=" * 80)
    for i, arg in enumerate(args, 1):
        print(f"\nArgument {i}:")
        pp(arg)
    print("\n" + "=" * 80)
    sys.exit(1)


def dump(*args: Any) -> None:
    """
    Dump variables without dying.
    Prints all arguments but continues execution.
    
    Usage:
        dump(user, profile, data)
    """
    print("\n" + "-" * 80)
    print("DUMP")
    print("-" * 80)
    for i, arg in enumerate(args, 1):
        print(f"\nArgument {i}:")
        pp(arg)
    print("-" * 80 + "\n")


def ddt(*args: Any) -> None:
    """
    Dump and die for tests - shows data and fails the test.
    Useful in pytest to inspect data.
    
    Usage:
        ddt(response.json(), user_data)
    """
    print("\n" + "=" * 80)
    print("TEST DUMP")
    print("=" * 80)
    for i, arg in enumerate(args, 1):
        print(f"\nArgument {i}:")
        pp(arg)
    print("\n" + "=" * 80)
    raise AssertionError("ddt() called - test stopped for debugging")
