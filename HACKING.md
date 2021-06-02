Developer notes
===============

This document is for people who maintain and contribute to this
repository.


How to run tests
----------------

This repo uses [tox](https://tox.readthedocs.io/) for unit and
integration tests. It does not install `tox` for you, you should
follow [the installation
instructions](https://tox.readthedocs.io/en/latest/install.html) if
your local setup does not yet include `tox`.

You are encouraged to set up your checkout such
that the tests run on every commit, and on every push. To do so, run
the following command after checking out this repository:

```bash
git config core.hooksPath .githooks
```

Once your checkout is configured in this manner, every commit will run
a code style check (with [Flake8](https://flake8.pycqa.org/)), and
every push to a remote topic branch will result in a full `tox` run.

In addition, we use [GitHub
Actions](https://docs.github.com/en/actions) to run the same checks
on every push to GitHub.

*If you absolutely must,* you can use the `--no-verify` flag to `git
commit` and `git push` to bypass local checks, and rely on GitHub
Actions alone. But doing so is strongly discouraged.
