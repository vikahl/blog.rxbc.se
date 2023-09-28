---
title: "Updates in Python template"
date: 2023-09-28T22:23:27+02:00
---

I have just updated my [Python project template] cookiecutter to use PEP
621/"metadata in pyproject.toml" as well as other minor fixes.

The template is "reasonable modern", meaning that it is using the latest
standards, but still relying on tested and stable tools. For projects with many
collaborators and where stability is important (e.g., work), I think this is
the best approach.

I do like testing new package managers, tools and linters in my own projects
with no other developers. But not in work projects or projects that might be
handed over to others.

## Basic ideas

- Always package the Python code as a library, even if is a service that will
  not be distributed through PyPI. Doing this makes it easy to write tests or
  extend functionality in various directions.
- Use [Setuptools] as the build system. It is a proven build system that
  supports the latest standards. I do not see a reason to use another system.
- Use Github Actions to run tests configured in tox and build and upload to
  PyPI for libraries.
- Selection for library, cli and/or service support.

[Read more in the repository and try it
out](https://github.com/vikahl/python-template). If you find anything strange
or something you disagree with, please create an issue.

[Python project template]: https://github.com/vikahl/python-template
