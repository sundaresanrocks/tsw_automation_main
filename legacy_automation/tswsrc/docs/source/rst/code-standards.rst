Coding Standards & Best practices
=================================

Some of the python coding conventions are listed here.

The complete set of conventions can be found at http://www.python.org/dev/peps/pep-0008

Summary
-------
- Maximum line length:  120
- Indentation: 4 spaces
- Say NO to tabs in python files
- Always use LF only line ending. Never mix line endings in any python file.(Also ensure before and after check in)
- Naming convention:
    - Class: CamelCase
    - Constants: Capitals
    - Methods and variables: lower case separated by _
- Use """ for doc strings
- Use ''' for multi line strings
- Avoid cyclic imports
- Catch exceptions with "as" instead of ","
- Separate top-level function and class definitions with two blank lines.
- Name unit test modules with "test_" as prefix
- Use parenthesis for all prints
- Write code compatible for python 3.4 and 2.7 as much as possible

Code lay-out
------------
•	Use 4 spaces per indentation level.
•	Never mix tabs and spaces.
•	Maximum Line Length: Limit all lines to a maximum of 79 characters.
•	Separate top-level function and class definitions with two blank lines.
•	Method definitions inside a class are separated by a single blank line.
•	Extra blank lines may be used (sparingly) to separate groups of related
        functions.  Blank lines may be omitted between a bunch of related
        one-liners (e.g. a set of dummy implementations).
•	Use blank lines in functions, sparingly, to indicate logical sections.

Naming Conventions
------------------
•	Modules: Modules should have short, all-lowercase names.
•	Packages: Python packages should also have short, all-lowercase names, although the use of underscores is discouraged.
•	Class: They use the CapWords convention. Classes for internal use have a leading underscore in addition.
•	Exception: Because exceptions should be classes, the class naming convention applies here.  However, you should use the suffix "Error" on your exception names
•	Functions: Function names should be lowercase, with words separated by underscores as necessary to improve readability.
•	Constants: Constants are usually defined on a module level and written in all capital letters with underscores separating words.  Examples include MAX_OVERFLOW and TOTAL

Special Naming constructs
-------------------------
•	_underscore: weak "internal use" indicator.
        E.g. ``from M import *`` does not import objects whose name starts with an underscore.
•	single_trailing_underscore_: used by convention to avoid conflicts with Python keyword,

::

    e.g. Tkinter.Toplevel(master, class_='ClassName')

•	__double_leading_underscore: when naming a class attribute, invokes name mangling

::

    (inside class FooBar, __boo becomes _FooBar__boo; see below).

•	__double_leading_and_trailing_underscore__: "magic" objects or attributes that live in user-controlled namespaces.

::

    E.g. __init__,__import__ or __file__.  Never invent such names; only use them as documented.

Imports
-------
•	Imports should usually be on separate lines
•	Imports are always put at the top of the file, just after any module comments and docstrings, and before module globals and constants.
•	Imports should be grouped in the following order:
        #. standard library imports
        #. related third party imports
        #. local application/library specific imports

Whitespace
----------
Avoid extraneous whitespace in the following situations:
- Immediately inside parentheses, brackets or braces.

::

    Yes: spam(ham[1], {eggs: 2})
    No:  spam( ham[ 1 ], { eggs: 2 } )

•	Immediately before a comma, semicolon, or colon:

::

    Yes: if x == 4: print x, y; x, y = y, x
    No:  if x == 4 : print x , y ; x , y = y , x

•	Immediately before the open parenthesis that starts the argument list of a function call:

::

    Yes: spam(1)
    No:  spam (1)

•	Immediately before the open parenthesis that starts an indexing or slicing:

::

    Yes: dict['key'] = list[index]
    No:  dict ['key'] = list [index]

•	More than one space around an assignment (or other) operator to align it with another.

::

    Yes:
    x = 1
    y = 2
    long_variable = 3
    No:
    x             = 1
    y             = 2
    long_variable = 3

•	Always surround these binary operators with a single space on
        either side: assignment (=), augmented assignment (+=, -= etc.),
        comparisons (==, <, >, !=, <>, <=, >=, in, not in, is, is not),
        Booleans (and, or, not).
•	Use spaces around arithmetic operators:
•	Don't use spaces around the '=' sign when used to indicate a
        keyword argument or a default parameter value.
•	Compound statements (multiple statements on the same line) are
        generally discouraged.
•	While sometimes it's okay to put an if/for/while with a small
        body on the same line, never do this for multi-clause
        statements.  Also avoid folding such long lines!

Programming Recommendations
---------------------------
•	When raising an exception, use "raise ValueError('message')" instead of
        the older form "raise ValueError, 'message'"
•	for all try/except clauses, limit the 'try' clause
        to the absolute minimum amount of code necessary.  Again, this
        avoids masking bugs.

python::

    try:
      value = collection[key]
    except KeyError:
      return key_not_found(key)
    else:
      return handle_value(value)

•	Use string methods instead of the string module.
•	Use ''.startswith() and ''.endswith() instead of string slicing to check
        for prefixes or suffixes. startswith() and endswith() are cleaner and less error prone.
        For example:

::

    Yes: if foo.startswith('bar'):
    No:  if foo[:3] == 'bar':

•	Object type comparisons should always use isinstance() instead
        of comparing types directly.

•	For sequences, (strings, lists, tuples), use the fact that empty
        sequences are false.

::

    Yes: if not seq:
               if seq:
    No: if len(seq)
              if not len(seq)

•	Don't compare boolean values to True or False using ==


::

    Yes:   if greeting:
    No:    if greeting == True:
    Worse: if greeting is True:


