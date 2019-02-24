# Contributing to fMRIflows

Welcome to the fMRIflows repository! We're excited you're here and want to contribute.

These guidelines are designed to make it as easy as possible to get involved. If you have any questions that aren't discussed below, please let us know by opening an [issue][https://github.com/miykael/fmriflows/issues]!

Before you start you'll need to set up a free [GitHub][https://github.com] account and sign in. Here are some [instructions][https://help.github.com/articles/signing-up-for-a-new-github-account/].
If you are not familiar with version control systems such as git,
 [introductions and tutorials](http://www.reproducibleimaging.org/module-reproducible-basics/02-vcs/)
 may be found on [ReproducibleImaging.org](https://www.reproducibleimaging.org).

Already know what you're looking for in this guide? Jump to the following sections:
- [Contributing to fMRIflows](#contributing-to-fmriflows)
  - [Issue labels](#issue-labels)
  - [Making a change](#making-a-change)
  - [Notes for New Code](#notes-for-new-code)
      - [Catching exceptions](#catching-exceptions)
      - [Testing](#testing)
  - [Recognizing contributions](#recognizing-contributions)
  - [Thank you!](#thank-you)

## Issue labels

* [![Bugs](https://img.shields.io/badge/-bugs-fc2929.svg)][link_bugs] *These issues point to problems in the project.*

    If you find new a bug, please provide as much information as possible to recreate the error.
    The [issue template][link_issue_template] will automatically populate any new issue you open, and contains information we've found to be helpful in addressing bug reports.
    Please fill it out to the best of your ability!

    If you experience the same bug as one already listed in an open issue, please add any additional information that you have as a comment.

* [![Help Wanted](https://img.shields.io/badge/-help%20wanted-c2e0c6.svg)][link_helpwanted] *These issues contain a task that a member of the team has determined we need additional help with.*

    If you feel that you can contribute to one of these issues, we especially encourage you to do so!
    Issues that are also labelled as [good-first-issue][link_good_first_issue] are a great place to start if you're looking to make your first contribution.

* [![Enhancement](https://img.shields.io/badge/-enhancement-00FF09.svg)][link_enhancement] *These issues are asking for new features to be added to the project.*

    Please try to make sure that your requested enhancement is distinct from any others that have already been requested or implemented.
    If you find one that's similar but there are subtle differences, please reference the other request in your issue.

* [![Orphaned](https://img.shields.io/badge/-orphaned-9baddd.svg)][link_orphaned] *These pull requests have been closed for inactivity.*

    Before proposing a new pull request, browse through the "orphaned" pull requests.
    You may find that someone has already made significant progress toward your goal, and you can re-use their
    unfinished work.
    An adopted PR should be updated to merge or rebase the current master, and a new PR should be created (see
    below) that references the original PR.

## Making a change

We appreciate all contributions to fMRIflows, but those accepted fastest will follow a workflow similar to the following:

**1. Comment on an existing issue or open a new issue referencing your addition.**

This allows other members of the fMRIflows development team to confirm that you aren't overlapping with work that's currently underway and that everyone is on the same page with the goal of the work you're going to carry out.

[This blog][https://www.igvita.com/2011/12/19/dont-push-your-pull-requests/] is a nice explanation of why putting this work in up front is so useful to everyone involved.

**2. [Fork][https://help.github.com/articles/fork-a-repo/] the [fMRIflows repository][https://github.com/miykael/fmriflows] to your profile.**

This is now your own unique copy of the fMRIflows repository.
Changes here won't affect anyone else's work, so it's a safe space to explore edits to the code!

You can clone your fMRIflows repository in order to create a local copy of the code on your machine.
To install your version of fMRIflows, and the dependencies needed for development,
in your Python environment, run `pip install -e ".[dev]"` from your local fMRIflows
directory.

Make sure to keep your fork up to date with the original fMRIflows repository.
One way to do this is to [configure a new remote named "upstream"](https://help.github.com/articles/configuring-a-remote-for-a-fork/)
 and to [sync your fork with the upstream repository][https://help.github.com/articles/syncing-a-fork/].

**3. Make the changes you've discussed.**

Before pushing your changes to GitHub, run `make check-before-commit`. This will remove trailing spaces, create new auto tests,
test the entire package, and build the documentation.
If you get no errors, you're ready to submit your changes!

It's a good practice to create [a new branch](https://help.github.com/articles/about-branches/)
of the repository for a new set of changes.


**4. Submit a [pull request][link_pullrequest].**

A new pull request for your changes should be created from your fork of the repository.

When opening a pull request, please use one of the following prefixes:


* **[ENH]** for enhancements
* **[FIX]** for bug fixes
* **[TST]** for new or updated tests
* **[DOC]** for new or updated documentation
* **[STY]** for stylistic changes
* **[REF]** for refactoring existing code

<br>
Pull requests should be submitted early and often (please don't mix too many unrelated changes within one PR)!
If your pull request is not yet ready to be merged, please also include the **[WIP]** prefix (you can remove it once your PR is ready to be merged).
This tells the development team that your pull request is a "work-in-progress", and that you plan to continue working on it.

Review and discussion on new code can begin well before the work is complete, and the more discussion the better!
The development team may prefer a different path than you've outlined, so it's better to discuss it and get approval at the early stage of your work.

One your PR is ready a member of the development team will review your changes to confirm that they can be merged into the main codebase.

## Notes for New Code

#### Catching exceptions
In general, do not catch exceptions without good reason.
For non-fatal exceptions, log the exception as a warning and add more information about what may have caused the error.

If you do need to catch an exception, raise a new exception using ``raise_from(NewException("message"), oldException)`` from ``future``.
Do not log this, as it creates redundant/confusing logs.

#### Testing
New code should be tested, whenever feasible.
Bug fixes should include an example that exposes the issue.
Any new features should have tests that show at least a minimal example.
If you're not sure what this means for your code, please ask in your pull request.

## Recognizing contributions

We welcome and recognize all contributions from documentation to testing to code development.

The development team member who accepts/merges your pull request will update the CHANGES file to reference your contribution.

## Thank you!

You're awesome. :wave::smiley:

<br>

*&mdash; Based on contributing guidelines from the [STEMMRoleModels][link_stemmrolemodels] project.*
