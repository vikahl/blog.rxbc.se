---
title: "Know what you install: Controlling transitive dependencies"
date: 2023-11-06T16:16:12+01:00
ShowToc: true
tags: ["know-what-you-install"]
draft: true
---

> This post is the second in a series that attempts to show several potential
> issues when installing Python packages and explain solutions to them.
> 
> In this post, we will discuss transitive dependencies a bit more, and how to
> control versions for them.
> 
> [You can find all posts in the series here](/tags/know-what-you-install/)

Transitive dependencies are dependencies defined by your direct dependencies.

To give an example:

- Your project depends on package _A_.
- _A_ in turn depends directly on _B_ and _D_.
- B depends on _C_.
- Both _B_ and _D_ depends on _E_.

```goat
A -+----> B --> C
   |      |
   '-> D -'-> E
```

In this example, _A_ is a direct dependency, and the rest are transitive
dependencies.

Transitive dependency versions are controlled by the dependency that pulls them
in, and pip will try to find a version that is compatible with all constraints
_see [Dependency resolution]_.

In the above examples, FastAPI depended on Pydantic and might restrict
which Pydantic versions that are compatible.

We can look in the [pyproject.toml file for FastAPI][fast-toml] and see that
there are several restrictions in place for Pydantic.

```toml {linenostart=42,hl_lines=[3]}
dependencies = [
    "starlette>=0.27.0,<0.28.0",
    "pydantic>=1.7.4,!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0",
    "typing-extensions>=4.8.0",
    # TODO: remove this pin after upgrading Starlette 0.31.1
    "anyio>=3.7.1,<4.0.0",
]
```

This mean that even if we have a direct dependency of Pydantic and therefore
want to install Pydantic and FastAPI together we will have problems for the
versions `fastapi==0.104.1` and `pydantic==2.0.0`.

```shell {linenos=false}
$ python3 -m pip install fastapi==0.104.1 pydantic==2.0.0

[ output omitted ]

ERROR: Cannot install fastapi==0.104.1 and pydantic==2.0.0 because these
package versions have conflicting dependencies.

The conflict is caused by:
    The user requested pydantic==2.0.0
    fastapi 0.104.1 depends on pydantic!=1.8, !=1.8.1, !=2.0.0, !=2.0.1,
    !=2.1.0, <3.0.0 and >=1.7.4

To fix this you could try to:
1. loosen the range of package versions you've specified
2. remove package versions to allow pip attempt to solve the dependency
   conflict

ERROR: ResolutionImpossible: for help visit
https://pip.pypa.io/en/latest/topics/dependency-resolution/#dealing-with-dependency-conflicts
```

The only reasonable way to solve this is to relax one of your version
constraints so that they are compatible. If you remove your pin on Pydantic,
pip will figure out a version that is compatible with both your and FastAPI's
requirements.

However, if you do not specify a version you cannot be sure that the same
Pydantic version will be installed every time as other direct dependencies can
restrict the version.

Compare these two installations, the first we installed FastAPI version 0.104.1
together with an unpinned Pydantic:

```shell {linenos=false,hl_lines=[6]}
$ python3 -m pip install 'fastapi==0.104.1' pydantic

[ output omitted ]

Successfully installed annotated-types-0.6.0 anyio-3.7.1 idna-3.4 
fastapi-0.104.1 pydantic-2.4.2
pydantic-core-2.10.1 sniffio-1.3.0 starlette-0.27.0
typing-extensions-4.8.0
```

Here we got Pydantic 2.4.2. However, if we install the same version of FastAPI
with an unpinned Pydantic and an unpinned SQLModel.

```shell {linenos=false,hl_lines=[6]}
$ python3 -m pip install 'fastapi==0.104.1' pydantic sqlmodel

[ output omitted ]

Successfully installed SQLAlchemy-1.4.50 anyio-3.7.1
fastapi-0.104.1 pydantic-1.10.13
greenlet-3.0.1 idna-3.4 sniffio-1.3.0
sqlalchemy2-stubs-0.0.2a36 sqlmodel-0.0.11 starlette-0.27.0
typing-extensions-4.8.0
```

As can be seen by the example above, we get a different version of Pydantic
because SQLModel had a different restrictions. This is all fine, this is how
you expect a dependency resolver to function. If we are picky about a package
version we need to introduce version constraints and might run into scenarios
where installation is not possible.

{{< box info >}}
Transitive dependencies version constraints are fully in the control of our
direct dependencies, unless we bring them in as direct dependencies.
{{</ box >}}

[fast-toml]: https://github.com/tiangolo/fastapi/blob/0.104.1/pyproject.toml#L42-L48

# Specifying transitive dependency versions

To achieve stability in deployed code or services, it is important to ensure
that the same dependency versions get installed every time. For example, it
would be frustrating if tests passes in CI, but crashes in production only
because a new version of a transitive dependency has been released.

Therefore, we want to specify version of transitive dependencies as well, but
as shown above, we need to find a version that is compatible with our other
dependencies.

A naive approach is to run `pip freeze` after installing the packages in a
local environment. To re-use the environment above where we installed FastAPI,
Pydantic and SQLModel, we see a list of eleven installed packages.

```shell {linenos=false}
$ python3 -m pip freeze
anyio==3.7.1
fastapi==0.104.1
greenlet==3.0.1
idna==3.4
pydantic==1.10.13
sniffio==1.3.0
SQLAlchemy==1.4.50
sqlalchemy2-stubs==0.0.2a36
sqlmodel==0.0.11
starlette==0.27.0
typing_extensions==4.8.0
```

However, maintaining this list manually is very hard as it is not clear which
of the dependencies here are our direct dependencies and which are transitive
dependencies.

Instead, it is wise to use a tool built for this, for example [pip-compile from
pip-tools][PT]. The tool takes an input file such as `pyproject.toml`
(recommended) or `requirements.in` and generates a text file with all
direct and transitive dependencies pinned.

In the example below we use a `requirements.in` file for simplicity, with the
following content:

```text
fastapi==0.104.1
pydantic
sqlmodel
```

Running `pip-compile` will generate a "compiled" requirements file that can be
saved to e.g., `requirements.txt`.

```shell {linenos=false}
$ pip-compile requirements.in

[ output omitted ]
#
# This file is autogenerated by pip-compile with Python 3.12
# by the following command:
#
#    pip-compile requirements.in
#
anyio==3.7.1
    # via
    #   fastapi
    #   starlette
fastapi==0.104.1
    # via -r requirements.in
greenlet==3.0.1
    # via sqlalchemy
idna==3.4
    # via anyio
pydantic==1.10.13
    # via
    #   -r requirements.in
    #   fastapi
    #   sqlmodel
sniffio==1.3.0
    # via anyio
sqlalchemy==1.4.50
    # via sqlmodel
sqlalchemy2-stubs==0.0.2a36
    # via sqlmodel
sqlmodel==0.0.11
    # via -r requirements.in
starlette==0.27.0
    # via fastapi
typing-extensions==4.8.0
    # via
    #   fastapi
    #   pydantic
    #   sqlalchemy2-stubs
```

This setup is much easier to manage that `pip freeze` as you can control your
dependencies in one file and then run `pip compile` to generate a new file with
all direct and transitive dependencies pinned.

# Dependency resolution speeds up installs

As mentioned earlier in this post, when you install packages pip needs to
figure out a version that that is compatible with all available version
constraints (from direct or transitive dependencies).

Historically, pip had a very naive approach, but the dependency resolver
introduced in 2020 improved this process and it now takes all constraints into
consideration.

However, this process can be slow, especially if there are many constraints to
take into consideration. A pre-compiled file improves this as dependency
resolution needs to happen only when the file is generated and not during each
install.

For more information about how to use tox to compile dependencies in a
convenient way, see my post _[Compile and use dependencies for multiple Python
versions in Tox]({{< ref "compile-and-use-dependencies-for-multiple-python-versions-in-tox.md" >}})_.

{{< box warning >}}
Problem 2: Transitive dependency versions are hard to control manually
{{</ box >}}

{{< box tip >}}
Solution 2: Compile all your dependencies with `pip-compile` from pip-tools

- Compile direct and transitive dependencies into pinned versions with
  `pip-compile`.
- Use the following flags with Pip-tools version 7.x: `--allow-unsafe`,
  `--resolver=backtracking`, `--strip-extras` ([will be default in the next
  major release ](https://github.com/jazzband/pip-tools#deprecations)).
- Check in the compiled files into git and install from this during deployment.
- _(if you are using tox)_: Set up a tox env to make it easier for developers
  to run the compilation with the correct Python version.
{{</ box >}}

[PT]: https://github.com/jazzband/pip-tools 
[Dependency resolution]: {{< ref "know-what-you-install--install-a-package.md#dependency-resolution" >}}
