---
title: "Know what you install: Extra PyPI indices"
date: 2023-12-04
ShowToc: true
tags: ["know-what-you-install"]
---

> This is a post in a series that explains potential issues related to
> dependencies. It does not attempt to explain all nuances of package
> management and supply chain security, but can serve as an introduction to
> some Python-specific parts.
> 
> In this post, we will go through what happens when you use Pip together with
> multiple indices and show problems related to it.
> 
> [You can find all posts in the series here](/tags/know-what-you-install/)


# Extra PyPI indices

It is common for companies or organisations to build internal packages, for
example a SDK developed by a central team that is used to interact with the
internal platform. These packages are seldom uploaded on PyPI.org because they
often contain proprietary code and are not meant to be used by the public.

The packages are instead uploaded to internal package indices. Pip has flags to
either switch index, `--index-url`, or use additional indices, `--extra-index-url`.

When determining the source of the package, Pip will take all indices into
consideration and might therefore install `my-internal-package` from PyPI.org
if it is available there.

This opens up for _dependency confusion_ attacks, where you expect
your internal package but instead get a package with malicious code that
someone has uploaded to PyPI.org.

{{< box warning >}}
Problem: Pip regards all indices as equal

When specifying multiple indices with `--extra-index-url`, Pip will regard all
indices as equal and will fetch packages from one of them.
{{</ box >}}

{{< box tip >}}
Solution: Be very careful when using `--extra-index-url`

Be very careful when using `--extra-index-url` and mitigate the risk of
dependency confusion attacks by one or several of the steps below.

- Only use one index and configure that to mirror packages to PyPI.org. You can
  put additional security measures here as well, e.g., scan packages, remove
  known vulnerable packages etc. 
- Upload a dummy package on PyPI.org to block the name and ensure no one else
  can upload `my-internal-package` there.

There is no easy solution to the problem of using multiple indices, but it is
being worked on and e.g., [PEP 708](https://peps.python.org/pep-0708/) will
help when it has been accepted and implemented.
{{< /box >}}

## Use hashes to get reproducible builds

With the above in mind, we know that a package with the same version can exist
on multiple indices, but contain different code. Furthermore, some indices
allow for reuploading package versions. So how can we determine that we get the
same content each time we install?

Pip supports [hash checking], where the hash is used to verify the downloaded
package. If any part of the package changes, so will the hash, so this way you
are guaranteed that you download the same content every time. You can find
hashes on PyPI.org at _Download files_ and _view hashes_ for the relevant file.

Specify the hash in your requirements-files (it is not supported on the command
line, see [pypa/pip#3257]).

```no-highlight {linenos=false}
pip==23.3.1 --hash=sha256:55eb67bb6171d37447e82213be585b75fe2b12b359e993773aca4de9247a052
```

When hashes are used, all requirements need to be pinned to exact versions and
have hashes specified. Therefore it is not really manageable to do this
manually, you need a tool like [pip-tools] that can generate a "compiled"
requirements file with versions and hashes specified based on your dependencies
in e.g., `pyproject.toml` or a `requirements.in`.

A future post will explain more about transitive dependencies and how to
compiled requirements-files. The post _[Compile and use dependencies for
multiple Python versions in Tox]_ contains example how to do this.

[Compile and use dependencies for multiple Python versions in Tox]: {{< ref "compile-and-use-dependencies-for-multiple-python-versions-in-tox.md" >}} 

{{<box info >}}
Hash checking will only ensure the same package is installed every time

Checking the hashes will ensure that the intended package content is installed,
but it will have no effect mitigating dependency confusion attacks if the
hash points towards the malicious package.

Therefore, hash checking in itself is not sufficient to mitigate the risk of
using multiple indices, but can be one part in the mitigation.

{{< /box >}}

[hash checking]: https://pip.pypa.io/en/stable/topics/repeatable-installs/#hash-checking
[pypa/pip#3257]: https://github.com/pypa/pip/issues/3257
[pip-tools]: https://github.com/jazzband/pip-tools



## Would you like to know more?

- [Dependency notation including the index URL](https://discuss.python.org/t/dependency-notation-including-the-index-url/5659)  
- [Motivation for PEP 708](https://peps.python.org/pep-0708/#motivation)



