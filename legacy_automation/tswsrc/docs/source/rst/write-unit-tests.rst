Writing Unit tests
==================

Testing your code is very important.

Getting used to writing the testing code and the running code in parallel is
now considered a good habit.

Some general rules of testing:

- A testing unit should focus on one tiny bit of functionality and prove it
  correct.

- Each test unit must be fully independent. Each of them must be able to run
  alone, and also within the test suite, regardless of the order they are
  called.

- Learn your tools and learn how to run a single test or a test case.

- Always run the full test suite before a coding session, and run it again
  after. This will give you more confidence that you did not break anything
  in the rest of the code.

- Use long and descriptive names for testing functions. The style guide here
  is slightly different than that of running code, where short names are
  often preferred.

- When something goes wrong or has to be changed, and if your code has a
  good set of tests, you or other maintainers will rely largely on the
  testing suite to fix the problem or modify a given behavior. Therefore
  the testing code will be read as much as or even more than th

- Another use of the testing code is as an introduction to new developers. When
  someone will have to work on the code base, running and reading the related
  testing code is often the best they can do.

- The first step should be to add a test and, by this mean, ensure the new
  functionality is not already a working path that has not been plugged in the interface.


The Basics
::::::::::


Unittest
--------

:mod:`unittest` is the batteries-included test module in the Python standard
library. Its API will be familiar to anyone who has used any of the
JUnit/nUnit/CppUnit series of tools.

Creating test cases is accomplished by subclassing :class:`unittest.TestCase`.

.. code-block:: python

    import unittest

    def fun(x):
        return x + 1

    class MyTest(unittest.TestCase):
        def test(self):
            self.assertEqual(fun(3), 4)

