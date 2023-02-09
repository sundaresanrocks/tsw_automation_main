.. _compound:

*******************
Compound statements
*******************

.. index:: pair: compound; statement

Compound statements contain (groups of) other statements;





Default parameter values are evaluated when the function definition is executed. This means that the expression is evaluated once, when the function is defined, and that the same �pre-computed� value is used for each call. This is especially important to understand when a default parameter is a mutable object, such as a list or a dictionary: if the function modifies the object (e.g. by appending an item to a list), the default value is in effect modified. This is generally not what was intended. A way around this is to use None as the default, and explicitly test for it in the body of the function, e.g.:


. Default paramerter should not be mutable objects.(list, dict).  Use None in such cases.

>>>
    def whats_on_the_telly(penguin=None):
        if penguin is None:
            penguin = []


Loops have else: part!
======================

for loops can have else too. When loop is not executed even once, they come into play!

.. productionlist::
   if_stmt: "if" `expression` ":" `suite`
          : ( "elif" `expression` ":" `suite` )*
          : ["else" ":" `suite`]
.. productionlist::
   while_stmt: "while" `expression` ":" `suite`
             : ["else" ":" `suite`]
.. productionlist::
   for_stmt: "for" `target_list` "in" `expression_list` ":" `suite`
           : ["else" ":" `suite`]



The :keyword:`try` statement
============================

.. index::
   statement: try
   keyword: except
   keyword: finally

The :keyword:`try` statement specifies exception handlers and/or cleanup code
for a group of statements:

.. productionlist::
   try_stmt: try1_stmt | try2_stmt
   try1_stmt: "try" ":" `suite`
            : ("except" [`expression` [("as" | ",") `target`]] ":" `suite`)+
            : ["else" ":" `suite`]
            : ["finally" ":" `suite`]
   try2_stmt: "try" ":" `suite`
            : "finally" ":" `suite`


The :keyword:`except` clause(s) specify one or more exception handlers. When no
exception occurs in the :keyword:`try` clause, no exception handler is executed.
When an exception occurs in the :keyword:`try` suite, a search for an exception
handler is started.  This search inspects the except clauses in turn until one
is found that matches the exception.  An expression-less except clause, if
present, must be last; it matches any exception.  For an except clause with an
expression, that expression is evaluated, and the clause matches the exception
if the resulting object is "compatible" with the exception.  An object is
compatible with an exception if it is the class or a base class of the exception
object, or a tuple containing an item compatible with the exception.

If no except clause matches the exception, the search for an exception handler
continues in the surrounding code and on the invocation stack.

If the evaluation of an expression in the header of an except clause raises an
exception, the original search for a handler is canceled and a search starts for
the new exception in the surrounding code and on the call stack (it is treated
as if the entire :keyword:`try` statement raised the exception).

When a matching except clause is found, the exception is assigned to the target
specified in that except clause, if present, and the except clause's suite is
executed.  All except clauses must have an executable block.  When the end of
this block is reached, execution continues normally after the entire try
statement.  (This means that if two nested handlers exist for the same
exception, and the exception occurs in the try clause of the inner handler, the
outer handler will not handle the exception.)



The :keyword:`with` statement
=============================

With more than one item, the context managers are processed as if multiple
:keyword:`with` statements were nested::

   with A() as a, B() as b:
       suite

is equivalent to ::

   with A() as a:
       with B() as b:
           suite






Class definitions
=================

.. index::
   object: class
   statement: class
   pair: class; definition
   pair: class; name
   pair: name; binding
   pair: execution; frame
   single: inheritance
   single: docstring

A class definition defines a class object (see section :ref:`types`):

.. productionlist::
   classdef: "class" `classname` [`inheritance`] ":" `suite`
   inheritance: "(" [`expression_list`] ")"
   classname: `identifier`

A class definition is an executable statement.  It first evaluates the
inheritance list, if present.  Each item in the inheritance list should evaluate
to a class object or class type which allows subclassing.  The class's suite is
then executed in a new execution frame (see section :ref:`naming`), using a
newly created local namespace and the original global namespace. (Usually, the
suite contains only function definitions.)  When the class's suite finishes
execution, its execution frame is discarded but its local namespace is
saved. A class object is then created using the inheritance list for the
base classes and the saved local namespace for the attribute dictionary.  The
class name is bound to this class object in the original local namespace.

**Programmer's note: Variables defined in the class definition are class
variables; they are shared by all instances.  To create instance variables, they
can be set in a method with ``self.name = value``. ** 

Both class and instance
variables are accessible through the notation "``self.name``", and an instance
variable hides a class variable with the same name when accessed in this way.

Class variables can be used as defaults for instance variables, but using
mutable values there can lead to unexpected results.  For :term:`new-style
class`\es, descriptors can be used to create instance variables with different
implementation details.

Class definitions, like function definitions, may be wrapped by one or more
:term:`decorator` expressions.  