'''
Location of CAM's "generate" routines,
which are used to autogenerate fortran
source code based off of the registry
and physics suites chosen by the user.
'''

########################################
# Import needed python libraries/modules
########################################

import sys
import os
import logging
import shutil
import glob

# Check for the CIME library, and add it
# to the python path:
__CIMEROOT = os.environ.get("CIMEROOT")
if __CIMEROOT is None:
    raise SystemExit("ERROR: must set CIMEROOT environment variable")
sys.path.append(os.path.join(__CIMEROOT, "scripts", "lib"))

#pylint: disable=wrong-import-position
# Import needed CIME functions:
from CIME.utils import expect
#pylint: enable=wrong-import-position

# Acquire python logger:
_LOGGER = logging.getLogger(__name__)

###############################################################################

class CamConfigError(ValueError):
    """Class used to handle CAM config errors
    (e.g., log user errors without backtrace)"""
    # pylint: disable=useless-super-delegation
    def __init__(self, message):
        super(CamConfigError, self).__init__(message)
    # pylint: enable=useless-super-delegation

###############################################################################
def _find_file(filename, search_dirs):
###############################################################################
    """Find file <filename> in the list of search directories, <search_dirs>.
    Return the first match (full path, match dir) or None, None"""
    match_file = None
    match_path = None
    for sdir in search_dirs:
        test_path = os.path.join(sdir, filename)
        if os.path.exists(test_path):
            match_path = sdir
            match_file = test_path
            break
        # End if
    # End for
    return match_file, match_path

###############################################################################
def _update_file(filename, source_path, bld_dir):
###############################################################################
    """If <filename> does not exist in <bld_dir>, copy <source_path>
    into <bld_dir>.
    If the file in <source_path> is different than <bld_dir>/<filename>,
    overwrite it with <source_path>.
    Take no action if the file in <source_path> is the same as
    <bld_dir>/<filename>.
    """
    test_path = os.path.join(bld_dir, filename)
    if os.path.exists(test_path):
        if not filecmp.cmp(source_path, test_path, shallow=True):
            os.remove(test_path)
            shutil.copy2(source_path, bld_dir)
        # End if
    else:
        shutil.copy2(source_path, bld_dir)
    # End if

###############################################################################
def _find_scheme_source(metadata_path):
###############################################################################
    """Given a path to a metadata file, find the associated Fortran file
    in that directory. Log a warning if no Fortran file exists and return None.
    """

    #Set fortran extensions:
    fortran_extensions = ['.F90', '.F', '.f', '.f90']

    source_file = None
    base = metadata_path[0:-5]
    for ext in fortran_extensions:
        test_file = base + ext
        if os.path.exists(test_file):
            source_file = test_file
            break
        # End if
    # End for
    if not source_file:
        emsg = "WARNING: No Fortran for metadata file, '%s'"
        _LOGGER.warning(emsg, metadata_path)
    # End if
    return source_file

###############################################################################
def _find_schemes_in_sdf(suite_part):
###############################################################################
    """Parse the suite, <suite_part>, and find all of the scheme names
    called by the suite.
    NB: This function is recursive as schemes may be nested inside other
        suite objects (e.g., group, subcycle)"""
    scheme_list = list() # Attempt to retain ordering
    for section in suite_part:
        item_type = section.tag.lower()
        if item_type == 'scheme':
            scheme_name = section.text
            if scheme_name and (scheme_name not in scheme_list):
                scheme_list.append(scheme_name)
            # End if
        else:
            for sub_section in section:
                if sub_section.tag.lower() == 'scheme':
                    scheme_name = sub_section.text
                    if scheme_name and (scheme_name not in scheme_list):
                        scheme_list.append(scheme_name)
                    # End if
                else:
                    sub_schemes = _find_schemes_in_sdf(sub_section)
                    for sscheme in sub_schemes:
                        if sscheme not in scheme_list:
                            scheme_list.append(sscheme)
                        # End if
                    # End for
                # End if
            # End for
        # End if
    # End for
    return scheme_list

###############################################################################
def _find_metadata_files(source_dirs, scheme_finder):
###############################################################################
    """Find all the metadata files (with associated Fortran source) in
    <source_dirs>. Only include the first file with a given name.
    Return a dictionary with keys of scheme names and values a tuple of the
    metadata file containing that key scheme name and the associated Fortran
    file.
    <scheme_finder> is a function for finding schemes in a metadata file.
    """
    meta_files = {}
    for direc in source_dirs:
        for root, _, files in os.walk(direc):
            if '.git' not in root:
                for file in [x for x in files if x[-5:] == '.meta']:
                    if file not in meta_files:
                        path = os.path.join(root, file)
                        # Check for Fortran source
                        source_file = _find_scheme_source(path)
                        if source_file:
                            # Find all the schemes in the file
                            schemes = scheme_finder(path)
                            for scheme in schemes:
                                meta_files[scheme] = (path, source_file)
                            # End for
                        # End if
                    # End if
                # End for
            # End if
        # End for
    # End for
    return meta_files

###############################################################################
def generate_registry(data_search, build_cache, atm_root, bldroot,
                       source_mods_dir, dycore, gen_fort_indent,
                       reg_config):
###############################################################################
    """Generate the CAM data source and metadata from the registry,
    if required (new case or changes to registry source(s) or script)."""
    #pylint: disable=wrong-import-position
    #pylint: disable=import-outside-toplevel

    # Search for registry generator file and path:
    gen_reg_file, gen_reg_path = _find_file("generate_registry_data.py",
                                                data_search)

    # Add registry  generator path to python path:
    sys.path.append(gen_reg_path)

    # Import needed CCPP-framework scripts:
    try:
        from generate_registry_data import gen_registry
    except ImportError as ierr:
        emsg = "ERROR: Cannot find generate_registry_data in '{}'\n{}"
        raise CamConfigError(emsg.format(gen_reg_path, ierr))
    #pylint: enable=wrong-import-position
    #pylint: enable=import-outside-toplevel

    # Find the registry file, registry schema, and generation routine
    # Try SourceMods first for each one.
    registry_file, _ = _find_file("registry.xml", data_search)
    registry_files = [registry_file]
    genreg_dir = os.path.join(bldroot, "cam_registry")
    #Create empty registry file objects list:
    reg_files_list = list()
    # Figure out if we need to generate new data source and metadata files
    if os.path.exists(genreg_dir):
        do_gen_registry = build_cache.registry_mismatch(gen_reg_file,
                                                        registry_files,
                                                        dycore, reg_config)
    else:
        os.makedirs(genreg_dir)
        do_gen_registry = True
    # End if
    if do_gen_registry:
        for reg_file in registry_files:
            retcode, reg_file_list = gen_registry(reg_file, dycore, reg_config,
                                                  genreg_dir, gen_fort_indent,
                                                  source_mods_dir, atm_root,
                                                  logger=_LOGGER,
                                                  schema_paths=data_search,
                                                  error_on_no_validate=True)
            emsg = "Unable to generate CAM data structures from {}, err = {}"
            expect(retcode == 0, emsg.format(reg_file, retcode))

            #Add files to list:
            reg_files_list += reg_file_list
        # End for

        # Save build details in the build cache
        build_cache.update_registry(gen_reg_file, registry_files,
                                    dycore, reg_config)
    # End if

    return genreg_dir, do_gen_registry, reg_files_list

###############################################################################
def generate_physics_suites(ccpp_scripts_path, build_cache, case, config, atm_root,
                             bldroot, reg_dir, reg_files, source_mods_dir, force):
###############################################################################
    """Generate the source for the configured physics suites,
    if required (new case or changes to suite source(s) or metadata)."""
    #pylint: disable=wrong-import-position
    #pylint: disable=import-outside-toplevel

    # Add CCPP-framework path to python path:
    sys.path.append(ccpp_scripts_path)

    # Import needed CCPP-framework scripts:
    try:
        from ccpp_capgen import capgen
        from metadata_table import MetadataTable
        from parse_tools import read_xml_file
    except ImportError as ierr:
        emsg = "ERROR: Cannot find CCPP-framework routines in '{}'\n{}"
        raise CamConfigError(emsg.format(spin_scripts_path, ierr))
    #pylint: enable=wrong-import-position
    #pylint: enable=import-outside-toplevel

    # Physics source gets copied into blddir
    physics_blddir = os.path.join(bldroot, "ccpp_physics")
    if not os.path.exists(physics_blddir):
        os.makedirs(physics_blddir)
    # End if
    # Collect all source directories
    source_search = [source_mods_dir,
                     os.path.join(atm_root, "src", "physics", "ncar_ccpp")]
    # Find all metadata files, organize by scheme name
    all_scheme_files = _find_metadata_files(source_search,
                                            MetadataTable.find_scheme_names)
    # Find the SDFs
    sdfs = list()
    scheme_files = list()
    for sdf in config.get_value('physics_suites').split(';'):
        sdf_path, _ = _find_file("suite_{}.xml".format(sdf), source_search)
        if not sdf_path:
            emsg = "ERROR: Unable to find SDF for, suite '{}'"
            raise CamConfigError(emsg.format(sdf_path))
        # End if
        sdfs.append(sdf_path)
        # Given an SDF, find all the schemes it calls
        _, suite = read_xml_file(sdf_path)
        sdf_schemes = _find_schemes_in_sdf(suite)
        # For each scheme, find its metadata file
        for scheme in sdf_schemes:
            if scheme in all_scheme_files:
                scheme_file = all_scheme_files[scheme][0]
                if scheme_file not in scheme_files:
                    scheme_files.append(scheme_file)
                    scheme_src = all_scheme_files[scheme][1]
                    _update_file(os.path.basename(scheme_src),
                                 scheme_src, physics_blddir)
                # End if (else, it is already in the list)
            else:
                emsg = "ERROR: No metadata file found for physics scheme, '{}'"
                raise CamConfigError(emsg.format(scheme))
            # End if
        # End for
    # End for
    # Figure out if we need to generate new physics code
    genccpp_dir = os.path.join(bldroot, "ccpp")
    preproc_defs = case.get_value('CAM_CPPDEFS')
    kind_phys = 'REAL64'

    # reg_dir needs to be first as the DDTs are defined there.
    host_files = glob.glob(os.path.join(reg_dir, "*.meta"))

    # Loop over all registered files:
    for reg_file in reg_files:
        if reg_file.file_path:
            #If the file path is provided, then add it to
            #the host model files list for use by CCPP's capgen:
            host_files.append(reg_file.file_path)

    if os.path.exists(genccpp_dir):
        do_gen_ccpp = force or build_cache.ccpp_mismatch(sdfs, scheme_files,
                                                         preproc_defs,
                                                         kind_phys)
    else:
        os.makedirs(genccpp_dir)
        do_gen_ccpp = True
    # End if
    if do_gen_ccpp:
        cap_output_file = os.path.join(genccpp_dir, "capfiles.txt")
        gen_hostcap = True
        gen_docfiles = False
        host_name = case.get_value('COMP_ATM')

        # print extra info to bldlog if DEBUG is TRUE
        _LOGGER.debug("Calling capgen: ")
        _LOGGER.debug("   host files: %s", ", ".join(host_files))
        _LOGGER.debug("   scheme files: %s", ', '.join(scheme_files))
        _LOGGER.debug("   suite definition files: %s", ', '.join(sdfs))
        _LOGGER.debug("   preproc defs: %s", ', '.join(preproc_defs))
        _LOGGER.debug("   output directory: '%s'", genccpp_dir)
        _LOGGER.debug("   kind_phys: '%s'", kind_phys)

        # generate CCPP caps
        capgen(host_files, scheme_files, sdfs, cap_output_file,
               preproc_defs, gen_hostcap, gen_docfiles, genccpp_dir,
               host_name, kind_phys, _LOGGER)

        # save build details in the build cache
        build_cache.update_ccpp(sdfs, scheme_files, preproc_defs, kind_phys)
    # End if
    return [physics_blddir, genccpp_dir], do_gen_ccpp, cap_output_file

###############################################################################
def generate_init_routines(data_search, build_cache, bldroot,
                           reg_files, force_reg, force_ccpp,
                           gen_fort_indent, cap_datafile):
###############################################################################
    """Generate the host model initialization source code files
       (phys_vars_init_check.F90 and physics_inputs.F90) using
       both the registry and the CCPP physics suites if required
       (new case or changes to registry or CCPP source(s), meta-data,
       and/or script)."""
    #pylint: disable=wrong-import-position
    #pylint: disable=import-outside-toplevel

    # Search for the "write_init_files.py" file and path:
    gen_init_file, gen_init_path = _find_file("write_init_files.py",
                                              data_search)

    # Append init source writer to python path:
    sys.path.append(gen_init_path)

    # Loop over all registered files:
    try:
        import write_init_files as write_init
    except ImportError as ierr:
        emsg = "ERROR: Cannot find write_init_files in '{}'\n{}"
        raise CamConfigError(emsg.format(gen_init_path, ierr))
    # End try
    #pylint: enable=wrong-import-position
    #pylint: enable=import-outside-toplevel

    #Add new directory to build path:
    init_dir = os.path.join(bldroot, "phys_init")

    # Figure out if we need to generate new initialization routines:
    if os.path.exists(init_dir):
        #Check if registry or CCPP suites were modified:
        if force_reg or force_ccpp:
            do_gen_init = True
        else:
            #If not, then check cache to see if actual
            #"write_init_files.py" was modified:
            do_gen_init = build_cache.init_write_mismatch(gen_init_file)
    else:
        #If no directory exists, then one will need
        # to create new routines:
        os.mkdir(init_dir)
        do_gen_init = True
    # End if

    if do_gen_init:
        #Run initialization files generator:
        retmsg = write_init.write_init_files(reg_files, init_dir, gen_fort_indent,
                                             cap_datafile, _LOGGER)

        #Check that script ran properly:
        emsg = "Unable to generate CAM init source code, error message is:\n{}"
        expect(retmsg == "", emsg.format(retmsg))

        # save build details in the build cache
        build_cache.update_init_gen(gen_init_file)
    # End if

    return init_dir

