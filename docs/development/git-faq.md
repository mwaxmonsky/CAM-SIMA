# git & GitHub FAQ

## Q: How can I clone someone's git clone to my directory on the same machine?
*A*: `git clone <path_name> [<local_dir>]` where `<path_name>` is the location of the source git clone and the optional `<local_dir>` is the name of the clone (default is a local directory of the same name as the original).

## Q: How can I clone someone's git clone to my directory on a different machine?
*A*: `git clone ssh://<user>@<machine>:<path_name> [<local_dir>]` where `<user>` is your user name on the remote machine, `<machine>` is the machine name (e.g., derecho.hpc.ucar.edu), `<path_name>` is the location of the source git clone on the remote machine, and the optional `<local_dir>` is the name of the clone (default is a local directory of the same name as the original).

## Q: How can I look at someone's PR code?
*A*: There a a few ways to do this:

- On GitHub (like looking at any other code on GitHub)
- Add the PR fork to my remote (allows using tools such as [`git diff` or `git difftool`](git-basics.md#comparing-differences-using-git-diff) with your existing branches or `development`)
- As a clone (standalone clone on your machine).

A first step is to find the link to the fork's branch. Just below the PR is a line that starts with a colored oval (e.g., "Open" in green) and looks something like:
```
Octocat wants to merge 123 commits into ESCOMP:development from Octocat:amazing-new-feature
```

Clicking on the last part (`Octocat:amazing-new-feature`) will take you to the correct branch where you can browse the code (the first method above). If you want to download that code, click the green "Code" button and then click the clipboard icon. Be sure to take note of the branch name.

- To load this code into your clone, cd to your clone directory, add the PR fork as a new remote, and checkout the branch. For instance:
```
    git remote add octocat https://github.com/octocat/CAM-SIMA.git
    git fetch --no-tags octocat
    git checkout octocat/amazing-new-feature
```

Instead of the `checkout` you can also do diffs:
```
    git difftool origin/development octocat/amazing-new-feature
```

- If you want to make a new clone with the PR code, simply do:
```
    git clone -b amazing-new-feature octocat https://github.com/octocat/CAM-SIMA.git octocat_cam
    cd octocat_cam-sima
```

## Q: Why do Pull Request (PR) code review take so long?
*A*: A code review must fulfill three purposes:

- Code reviewers must make sure that new and/or changed code does not affect any currently-supported functionality (i.e., it cannot break anything).
    - While regression tests will catch many of these issues, reviewers must also check for usage of or reliance on deprecated code, and also for any code which is not supported on all platforms and compilers used by the CESM community.
- Code reviewers must make sure that any new functionality or changes are implemented correctly and at least somewhat efficiently. They must also ensure that important changes are tested against future regressions.
- The CAM SE team is almost always engaged in several projects to implement new CAM functionality along with supporting infrastructure. Each CAM SE usually looks at each PR in order to prevent new code from interfering with those plans.

The first two steps are usually completed by a single SE although SEs engaged in a final review will often find missed errors. This is similar to peer reviewers finding problems with a paper even after reviews done by colleagues.

## Q: How do I update my branch to the current cam_development?
*A*: [see this section](git-basics.md#updating-your-branch-to-latest-development)