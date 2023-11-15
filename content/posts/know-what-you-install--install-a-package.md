---
title: "Know what you install: Install a package"
date: 2023-11-15
ShowToc: true
tags: ["know-what-you-install"]
---

> This post is the first in a series that explains potential issues related to
> dependencies. It does not attempt to explain all nuances of package
> management and supply chain security, but will try to give enough context so
> 
> In this post, we will go through what happens when you install a package and
> how to specify a version. We will also go through the dependency resolution
> that happens when pip tries to find compatible versions and lastly a short
> explanation about distribution formats.
> 
> [You can find all posts in the series here](/tags/know-what-you-install/)

# What gets installed when you install a package?

It is common to use pip, the Python package manager, to install external
dependencies into your Python projects. When you install a package pip will
reach out to a package index (normally [PyPI]), download the appropriate
version and install it. If no version is specified, it will install the latest
version available for your system.

The Python packaging user guide has a section _[Installing packages]_ that
explains more about the various ways of installing and different options.

Compare these two examples that install the excellent API framework [FastAPI].

The first example is installing in a Python 3.6 environment:

```shell {linenos=false,hl_lines=[10]}
$ python3 -V
Python 3.6.15
$ python3 -m pip install fastapi
Collecting fastapi

[ output omitted ]

Successfully installed anyio-3.6.2 contextlib2-21.6.0 contextvars-2.4
dataclasses-0.8
fastapi-0.83.0
idna-3.4 immutables-0.19 pydantic-1.9.2
sniffio-1.2.0 starlette-0.19.1 typing-extensions-4.1.1
```

The second is installing in a 3.12 environment:

```shell {linenos=false,hl_lines=[9]}
$ python3 -V
Python 3.12.0
$ python3 -m pip install fastapi
Collecting fastapi

[ output omitted ]

Successfully installed annotated-types-0.6.0 anyio-3.7.1
fastapi-0.104.1
idna-3.4 pydantic-2.4.2 pydantic-core-2.10.1 sniffio-1.3.0 starlette-0.27.0
typing-extensions-4.8.0
```

Two conclusions can be drawn from these commands:

1. Different versions of FastAPI were installed when using different Python
   versions.  
   The reason for this is simply that FastAPI dropped support for 3.6 after
   0.83.0 and pip will find the latest version that is compatible with the
   current environment.
2. Additional packages were installed.  
   FastAPI, just as most other packages, will have its own dependencies. These
   dependencies of dependencies are called _transitive dependencies_.

{{< box warning >}}
Problem 1: The "latest" package version is ambiguous

Omitting the obvious answer that newer versions can be released on PyPI at any
time, it is also important to note that the Python version, or in some cases
even factors such as the operating system can impact which versions that are
being installed.
{{< /box >}}

[FastAPI]: https://fastapi.tiangolo.com/

# Specify a version

The problem with unspecified versions can be solved by simply specifying a
version. Version specifiers are defined in _[PEP 440 – Version Identification
and Dependency Specification: Version specifiers][440VS]_.

Except from the PEP:

> A version specifier consists of a series of version clauses, separated by
> commas. For example:
> 
> ```
> ~= 0.9, >= 1.0, != 1.3.4.*, < 2.0
> ```
>
> The comparison operator determines the kind of version clause:
>
> - `~=`: Compatible release clause
> - `==`: Version matching clause
> - `!=`: Version exclusion clause
> - `<=`, `>=`: Inclusive ordered comparison clause
> - `<`, `>`: Exclusive ordered comparison clause
> - `===`: Arbitrary equality clause.

The different clauses are further explained in PEP 440, but you can get very
far by using the exact version matching (`==`) or the ordered comparison
clauses, also known as less/greater than (`<,>,<=,>=`).

If you for example rely on a feature that was released in FastAPI 0.95.0 and
therefore need to always install 0.95.0 or later, you will express that as:

```shell {linenos=false}
$ python3 -m pip install 'fastapi>=0.95.0'
```

_Note the apostrophes (`'`) around the package/version. They are needed since
otherwise `>` will be interpreted as a redirection by the shell._

Similarly, if you rely on a feature that was removed in a specific version and
do not yet have updated your code, you can use the `'package<0.95.0'` syntax
instead.

{{< box tip >}}
Solution 1: Specify version using version clauses

Specifying package version using version clauses will ensure that you get the
expected version.

For deployed code (e.g., services) it is recommended to specify an exact
version (`==`) to avoid surprises in the future.
{{< /box >}}

{{< box info >}}
Avoid over-restricting dependencies in libraries

Library developers should be very mindful in how they restrict dependency
versions. Too specific restrictions make it hard to install the library along
other libraries (which might have different restrictions).

Henry Schreiner has written a good post titled _[Should You Use Upper Bound
Version Constraints?](https://iscinumpy.dev/post/bound-version-constraints)_.
{{< /box >}}

# Wheels and source distributions (sdist)

Wheel is a format that distributes an installable version of a package in a
zip-file but with the file extension `.whl`. The archive contains the Python
code itself, metadata about the package and compiled binaries if the package
contains e.g., C-code.

For pure Python packages, the wheel files are universal, but for compiled code
the wheel is specific for an architecture, ABI, et c. This can be read from the
file name. The advantage of using wheels is that no build system (compiler, …)
needs to be present on the machine to install the package.

However, if you are using a strange architecture or are for example installing
an old package on a new Mac (with the M-series processor) there might not be
available wheels.

Sdist, or source distribution, is often a direct archive of the repository
(with non-relevant files omitted). Installing from sdist might require build
system and external dependencies if the package contains non-Python code.
Behind the scenes, pip will actually first build a wheel from the sdist and
then install the package from that wheel.

It is good to distribute both formats, but if you have to select one wheel is
probably the best for most occasions.

Read more about wheels in the Python packaging user guide _[Binary distribution
format]_.

# Dependency resolution

Dependency resolution is the problem to figure out packages and versions that
match the version clauses. A dependency resolver needs to take into
consideration both direct dependencies and the various transitive dependencies.

There are a few important points to know:

- Pip got a new resolver in 2020 (pip 20.3) that significantly improved it's
  capabilities.
- Dependency resolution can be slow if there are many constraints to take into
  consideration

If you are interested in this topic, pips documentation, _[Dependency
resolution]_, is a good read.

[440VS]: https://peps.python.org/pep-0440/#version-specifiers
[PyPI]: https://pypi.org
[Installing packages]: https://packaging.python.org/en/latest/tutorials/installing-packages/
[Dependency resolution]: https://pip.pypa.io/en/stable/topics/dependency-resolution/
[Binary distribution format]: https://packaging.python.org/en/latest/specifications/binary-distribution-format/#binary-distribution-format
