# Design goals & features

Motivated by the Singletrack project (a precursor to [SIMA](https://sima.ucar.edu/about)), the CAM-SIMA project was created to build a new CAM infrastructure to meet the SIMA science and computational needs. This page documents those needs and some of the features that implement them.

## CAM needs to be more run-time configurable

- To make CAM and CESM more available, e.g., for usage in containers and the cloud, a build of CAM should be more configurable than it is at present.
- One feature that makes CAM more run-time configurable is moving physics suites to the [CCPP](https://dtcenter.org/community-code/common-community-physics-package-ccpp). By allowing CAM to compile in more than one physics suite, the physics suite can be selected at run time (e.g., as a namelist variable).
- Another feature needed to make CAM more run-time configurable is making dycores themselves more run-time configurable. For instance, the SE dycore will no longer require the number of advected constituents to be specified at compile time.

## Remove obstacles to use of specialized high-performance processing units (e.g., GPUs, FPGAs)

The chunk structure in CAM physics served its purpose when threading was the only way to accelerate code. However, to make the best use of both threading and modern accelerators, a flexible chunking mechanism is required. The new infrastructure enables this by using flat arrays for all fields.

- Moving to flexible precision of data is important for being able to test both performance improvements and the affect on model quality. **The CCPP is explicitly designed to allow for compile-time selection of precision at the physics suite level as well as for individual fields.** In addition, the new infrastructure is explicitly designed to handle the case where the dycore is running at a different precision than the physcs (i.e., by using proper field promotion and demotion primitives).
- Pointers in Fortran are less efficient because they prevent some optimization techniques. The new infrastructure avoids pointers as much as possible by making use of the automatic data management capability of the CCPP (which does not create pointers).
- The new infrastructure provides greater flexibility in that the model can be built with multiple physics suites to increase run-time flexibility. There is a tradeoff in that building more physics suites will often increase build time. Builds with a single suite should be faster than now since only the schemes that are required for the suite are compiled (currently most schemes are compiled all the time even if they will not be used).

## Modularity
In order to continue to allow CAM to grow without an ever increasing cost of bringing in new features, CAM must be more modular. A classic example is chemistry which ACOM would like to make modular but which is currently entwined with CAM in many areas (e.g., code in CAM repository, extensive configuration code dedicated to chemistry, extensive namelist building code and data dedicated to chemistry, large number of use cases containing chemistry configuration data). The new CAM infrastructure contains features to increase modularity.

- Support for multiple namelists. This allows modular components to contain their own namelist (run-time configuration options). The active namelists are combined to produce atm_in.
- Flexible handling of constituent information. Modular components can provide constituent information via metadata (if component is a CCPP scheme) or at run time.

Modularity will allow CAM to move components to external repositories. This process cuts development costs for both CAM and for the component (e.g., as has happened with PUMAS). Some ways this is accomplished are listed here:

- Code reviews are more efficient since CAM SEs do not have to review every routine in the external module so they can just focus on the interfaces. The external developers do not have to be involved in CAM modifications.
- Externals can develop and maintain they own namelist definition files, they do not have to coordinate with the larger CAM namelist (which itself has been broken into several smaller namelists).
- Namelists associated with physics schemes do not have to have separate namelist-reading code. The new infrastructure automatically creates an appropriate Fortran module to read in the runtime data from atm_in. The system then also ensures that all active namelists are called at run time. This process ensures that namelists are always read correctly while not requiring coding or reviews to keep up to date with namelist changes.

Use of the CCPP to build physics suites also makes CAM more modular because the CCPP treats physics schemes as modular which allows flexibility in building physics suites. The CCPP takes care of making sure variables are available before they are used and also builds the code currently handled via hand-written code in the various versions of physpkg.F90.

## Run-time data checking
CAM needs data to run but the data needs vary with the simulation. The new infrastructure facilitates this.

- Before running physics, the new infrastructures queries the physics suite as to what input fields are required (using a CCPP interface). Then it makes sure that all of these fields have been initialized or reads the values from the initial data file. Any uninitialized fields that are not found on the initial data file will trigger a run-time error.

## Efficient offline testing and simulation

CAM currently has a few ways to run offline testing (e.g., SCAM, PORT). The new infrastructure builds these capabilities in for more efficient and flexible use.

- The new infrastructure has the ability to run without a dycore.
- Offline mode (NULL dycore) can be run with any number of columns.
- Offline mode does not required gridded input.

## Software quality control
To enable efficient quality control, the new infrastructure implements a number of continuous integration (CI) techniques.

- To implement all the flexibility mentioned above, the new infrastructure makes extensive use of python scripts.
    - Python scripts make extensive use of python doctests (for simpler tests).
    - There are python unit tests to cover more complicated situations.
    - The GitHub CI also runs a static analysis tool (pylint) to provide feedback on potential coding issues.
    - Python tests can easily be run by hand but are also automatically run on GitHub
- The new infrastructure will use offline mode (see above) to run many physics configurations quickly without requiring large machines.
    - This will enable quick testing during development on a laptop.
    - We hope many of these tests can also be run automatically on GitHub.