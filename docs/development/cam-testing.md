# Testing

This page describes the various automated and manual tests that are run for CAM-SIMA whenever the code is modified, as well as instructions for how to add new tests.

## Python unit testing
CAM-SIMA supports two kinds of python unit tests, `doctest` and `unittest` tests, both of which are part of the standard python library.  

All `unittest` tests should  be in:

`CAM-SIMA/test/unit`

while all files used by the tests should be in:

`CAM-SIMA/test/unit/sample_files`

All `unittest` tests are automatically run via Github Actions whenever a Pull Request (PR) is opened, modified, or merged.  

All `doctest` tests are also run automatically as long as the scripts they are located in are under `CAM-SIMA/cime_config` or `CAM-SIMA/src/data`.

To manually run all of the unit tests at any time, simply run the following shell script:

`CAM-SIMA/test/run_tests.sh`

Finally, when adding new tests, determine if the test can be done in only a few lines with minimal interaction with external files or variables.  If so, then it would likely be best as a `doctest`.  Otherwise it should be a `unittest` test.  Failure to follow this rule of thumb could result in test failures in the Github Actions workflow.  Also remember to add your new tests to the `run_tests.sh` script so future users can easily run the tests manually.

## Static Source Code Analysis

### Python

Any python script which is added or modified via a PR will automatically be analyzed using `pylint`, and must have a score of 9.5 or greater in order to not be marked as a test failure.  The hidden `pylintrc` file used for the analysis can be found here:

`CAM-SIMA/test/.pylintrc`

Users can also manually run `pylint` against the core python build scripts by running the following shell script:

`CAM-SIMA/test/pylint_test.sh`

Please note that `pylint` is not part of the standard python library, and so it may need to be installed before being able to run the shell script.

## Regression Testing
### Running the regression tests (manual)

**NOTE:  Regression testing on Derecho should be done for every PR before merging!**

Users can manually run regression tests on Derecho to ensure that the model builds correctly in various configurations.  The tests can be run with a local copy of CAM-SIMA by using the `test_driver.sh` script under `$CAM-SIMA/test/system`.  To run the tests associated with a particular compiler option one can do the following commands:

For running GNU tests*:
```
env CAM_FC=gnu ./test_driver.sh -f
```

For running Intel tests*:
```
env CAM_FC=intel ./test_driver.sh -f
```

Running the script will produce a directory in your scratch space labeled `aux_sima_<CAM_FC>_<timestamp>`, where `<CAM_FC>` is the compiler you chose, and `<timestamp>` is the timestamp (starting with the date) of when the tests were started, along with a job submitted to the local batch system.

Inside the directory you should see an executable labeled `cs.status.*`.  Running that command after the submitted job has finished will display the test results.  Currently for all tests everything should be labeled `PASS` except the `SUBMIT` step, which should be labeled `PEND`.  Any other label indicates that a test may have failed, and should be investigated.

Finally, the tests themselves are listed in `<CAM-SIMA>/cime_config/testdefs/testlist_cam.xml`.  Any files that need to be included in order for the tests to run properly are located in `<CAM-SIMA/cime_config/testdefs/testmods_dirs/cam/outfrq_XXX`, where `XXX` is the name of the test.  Additional information on the CIME testing system, which is what this testing infrastructure is built on, can be found [online here](https://esmci.github.io/cime/versions/master/html/users_guide/testing.html). 

*Note: you may also have to include the environment variable `CAM_ACCOUNT` on derecho, which points to your account key

### Adding a new regression test

The test list can be found here: `$CAM-SIMA/cime_config/testdefs/testlist_cam.xml`

- If you are adding a new machine, compiler or category for an existing test, add a new `<machine>` XML entry
- If you are adding a fully new test, add a new `<test>` XML entry with the following structure:
```
<test compset="<COMPSET_NAME>" grid="<GRID_ALIAS>" name="<TEST_TYPE>_<TEST_MOD>" testmods="<RELPATH_TO_TESTMODS_DIR>">
  <machines>
    <machine name="<MACH_NAME>" compiler="<COMPILER>" category="<TEST_CATEGORY>"/>
  </machines>
  <options>
    <option name="comment">COMMENT HERE</option>
    <option name="wallclock">WALLCLOCK_TIME</option>
  </options>
</test>
```

- `<COMPSET_NAME>`: component set alias (or long name) - you can see more about compsets [here](../usage/creating-a-case.md)
- `<GRID_ALIAS>`: model grid/resolution you'd like to run on - you can see more about grids [here](../usage/creating-a-case.md)
- `<TEST_TYPE>`: type of test to be run. You can find the testing types [here](https://esmci.github.io/cime/versions/master/html/users_guide/testing.html#testtype).
- `<TEST_MOD>`: test modifier that changes the default behavior of the test type. More [here](https://esmci.github.io/cime/versions/master/html/users_guide/testing.html#modifiers)
- `<RELPATH_TO_TESTMODS_DIR>`: relative path to the testmods directory for this run; usually looks something like `"cam/some_directory_name/"`
    - The testmods directory will contain any namelist mods and XML configuration variable changes for the test (`user_nl_cam` and/or `shell_commands`)
    - testmods directories can be found in `$CAM-SIMA/cime_config/testdefs/testmods_dirs/cam/`
- `<MACH_NAME>`: machine name - will almost definitely be either `derecho` or `izumi`
- `<COMPILER>`: compiler to be used (options: `gnu`, `nag`, `intel`, `nvhpc`)
- `<TEST_CATEGORY>`: group of tests that this test belongs to - the default run by `test_driver.sh` is `aux_sima` (which is run for each PR to CAM-SIMA)
- `WALLCLOCK_TIME`: maximum amount of time that the job will be allowed to run

Here is an example test entry for a 2-timestep smoke test of kessler physics on the MPAS grid, run with both intel and gnu 
```
  <test compset="FKESSLER" grid="mpasa480_mpasa480" name="SMS_Ln2" testmods="cam/outfrq_kessler_mpas_derecho_nooutput/">
    <machines>
      <machine name="derecho" compiler="intel" category="aux_sima"/>
      <machine name="derecho" compiler="gnu" category="aux_sima"/>
    </machines>
    <options>
      <option name="wallclock">00:10:00</option>
      <option name="comment">GNU build test for MPAS dycore (with Kessler physics)</option>
    </options>
  </test>
```