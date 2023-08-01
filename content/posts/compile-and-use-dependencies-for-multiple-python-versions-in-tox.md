---
title: "Compile and use dependencies for multiple Python versions in Tox"
date: 2023-08-01
draft: true
---

This post shows a way to easily compile and use requirement files for multiple
Python versions in tox. I plan to expand my thoughts about dependency
management and compiled requirements in future posts and this post therefore
only contains a small motivation why you should compile.

## Why compile dependencies?

Compiled dependencies are mainly a tool for services or other Python code that
will be deployed in one way or another. Libraries that will be installed
together with other code should not compile, or overly restrict dependencies as
it will be difficult for users to install them into their environments.

When adding dependencies to you project, you will almost always indirectly
bring in transitive dependencies, dependencies used by "your" dependencies. If
you want predictable deployments and reproducible builds you need to specify
versions for all dependencies, including the transitive ones. 

One popular way to do this is to use pip-compile from [pip-tools] to generate
compiled requirements files based on your loosely pinned requirements.

## When do you need to compile requirements for multiple versions?

When compiling requirements with pip-tools, environment markers are resolved so
the generated file will be specific to a Python version, CPU architecture, etc.

My original need for this was a service and a library that was built from the
same code base. Since this was a small internal service we set it up this way
to easy maintenance. The library was used by consumers of the service and we
needed to support multiple Python versions and thus also run the test suite in
these versions.

I have used the same pattern for code with multiple deployments with external
restrictions on supported Python versions, e.g., when deployed in provided
containers or when running non-containerized.

## Compile requirements in a tox environment

_The configuration below assumes tox 4. You can use the same technique in tox 3
but need to modify the config._

Compiling requirements in a tox environment provides a good interface for
developers as they do not need to know the different flags to pip-compile, nor
do they need to install it. You can easily control which Python version that
will be used, allowed platforms, allowed pip-tools versions, et c. The
developers just runs the tox environment to get compile requirements.

By using [generative section names] we can create one test section that
generates requirements for several Python versions. The section name can then
be referenced as `{envname}` in the output file name.

Adding a label makes it easy to just run `tox run -m requirements` to
regenerate all requirements and `CUSTOM_COMPILE_COMMAND` will write the new
command to the header of the compiled requirement file.

The configuration below assumes dependencies are specified in pyproject.toml
and that the dev dependencies are specified in the `dev`-extra. See [pip-tools]
documentation and [Python Packaging User Guide] for more information how to
specify dependencies

```ini
[testenv:requirements-py{38,39,310,311}]
; Generate new requirements files
labels = requirements
deps = pip-tools
skip_install = true
setenv =
  CUSTOM_COMPILE_COMMAND='tox run -m requirements'
commands =
  pip-compile pyproject.toml --output-file requirements/{envname}.txt
  pip-compile --extras dev pyproject.toml --output-file requirements/{envname}-dev.txt
```

## Use the requirement files

Since we cleverly named out requirement-generating environments
`requirements-py{version}` _(note the py-part which is needed if you use the
common pyXX notation for environments)_ and saved the file named as
`requirements-{envname}-dev.txt` we can easily reference them in the `deps`
key.

```ini
[testenv]
deps = -r{toxinidir}/requirements/requirements-{envname}-dev.txt
```

The `py38` environment will use Python 3.8, and the `requirements-py38-dev.txt`
file.

## Example tox config

The tox config below is an example where the above techniques are used
(together with a few other things).

```ini
[tox]
min_version = 4.0
envlist =
    lint,
    py38,
    py39,
    py310
    py311
isolated_build = true

[testenv]
deps = -r{toxinidir}/requirements/requirements-{envname}-dev.txt
commands =
  pytest

[testenv:lint]
basepython = python3.10
; Example with hardcoded deps file
deps = -r{toxinidir}/requirements/requirements-py310-dev.txt
skip_install = true
commands =
  pylint

[testenv:requirements-py{38,39,310,311}]
; Generate new requirements files
; only run this on linux as compiled requirements are platform dependent and
; this code is deployed in linux containers.
; Would be better to only run this on a specific processor architecture, but
; this is not supported in tox at the moment.
labels = requirements
platform = linux
deps = pip-tools
skip_install = true
setenv =
  ; will show `tox run -m requirements` in the top of the generated files.
  CUSTOM_COMPILE_COMMAND='tox run -m requirements'
commands =
; explanation of flags used
; --upgrade: upgrade all dependencies to latest version. normally pip-compile
;   change as little as possible, but without constraints it means that
;   it will never update transitive dependencies.
; --resolver backtracking: use the "new" improved backtracking resolver from
;   pip. this will be default in pip-tools 7.
; --allow-unsafe: allow the "unsafe" packages, which will be default behaviour
;   in upcoming pip-tools version.
  pip-compile --upgrade --resolver backtracking --allow-unsafe pyproject.toml --output-file requirements/{envname}.txt
  pip-compile --upgrade --resolver backtracking --allow-unsafe pyproject.toml --output-file requirements/{envname}-dev.txt
```

Compile requirements with

```shell
$ tox run -m requirements
```

Hope that this was interesting and could be useful.

If you have comments or thoughts, [please send me an email](/about/#contact-me).

[generative section names]: https://tox.wiki/en/latest/user_guide.html#generative-environments
[pip-tools]: https://github.com/jazzband/pip-tools
[Python Packaging User Guide]: https://packaging.python.org/en/latest/
