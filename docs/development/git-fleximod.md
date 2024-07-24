# git-fleximod
## Populate and/or update your externals
Run `bin/git-fleximod update`

The process will either:

- complete and you're good to go
- indicate to you that modifications have been made in certain modules
    - this means you should either go commit those mods or remove them
    - you can also (if you're sure!) run `bin/git-fleximod update -f` to force overwrite all externals

## Update external repo or tag
To add or update an external repo to CAM-SIMA, the following steps must be done:

1. Modify the `.gitmodules` file at the head of CAM-SIMA to add or update the external.  Explanations for what each entry in the `.gitmodules` file is can be found on Github [here](https://github.com/ESMCI/git-fleximod?tab=readme-ov-file#supported-gitmodules-variables)
1. Once the `.gitmodules` file has been updated, go to the head of CAM-SIMA and run `bin/git-fleximod update`.  This will bring in the new external code into your local repo (but will not commit them).
1. Once you are ready to officially commit the changes, then make sure to commit both the modified `.gitmodules` file, and the updated submodule itself.  An easy way to make sure you have commited everything is to run `git status` and make sure there are no files or directories that have been modified but are still un-staged.

Once all of that is done then congrats!  A new external has been successfully added/updated.   
