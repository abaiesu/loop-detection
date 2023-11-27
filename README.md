# Loop Detection


[![PyPI Status](https://img.shields.io/pypi/v/loop-detection.svg)](https://pypi.python.org/pypi/loop-detection)
[![Build Status](https://github.com/abaiesu/loop-detection/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/abaiesu/loop-detection/actions?query=workflow%3Abuild)
[![Documentation Status](https://github.com/abaiesu/loop-detection/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/abaiesu/loop-detection/actions?query=workflow%3Adocs)
[![License](https://img.shields.io/github/license/abaiesu/loop-detection)](https://github.com/abaiesu/loop-detection/blob/main/LICENSE)
[![Code Coverage](https://codecov.io/gh/abaiesu/loop-detection/branch/main/graphs/badge.svg)](https://codecov.io/gh/abaiesu/loop-detection/tree/main)

Detects loops in a network from its forwarding tables. We use an algorithm that only requires set intersection, to avoid the increase in complexity when unions and complements are used.


- Free software: MIT license
- Documentation: https://abaiesu.github.io/loop-detection/.


## Features

- Classes for rule representation. Supported types of rules : ranges, wildcard expressions, n-tuples/multi-fields.
- An efficient algorithm to compute the equivalence classes of the header space from a set of rules.
- A loop detection function which returns the nodes and the rules involved in the network loop.

## Credits

This package was created with [Cookiecutter][CC] and the [Package Helper 3][PH3] project template.

[CC]: https://github.com/audreyr/cookiecutter
[PH3]: https://balouf.github.io/package-helper-3/
