# Coding standards

The standards in this document are largely prescriptive, i.e., they should be followed.

- *MUST*: Exceptions must be discussed and agreed to by the CAM SEs and noted in this document.
- *SHOULD*: Exceptions must be approved by the CAM SEs and documented in the ChangeLog.

While some legacy code will not follow these rules, efforts SHOULD be made to improve the code whenever you are working on it (e.g., bug fixes, enhancements).

## General coding standards
### MUST
- Always use spaces instead of tabs
- No trailing spaces (i.e., no spaces at the end of a line)

See [tips for configuring editors](#tips-for-configuring-editors)

### SHOULD

- Use comments to explain the purpose of the following code and/or include any important but non-obvious information. When working with code, always check the comments to make sure they are still correct and useful.
- Do not use comments to 'save code for later in case it might be useful'.
- Do not include a comment that merely restates the following code logic (e.g., 'Loop over variables')

## Python coding standards
We expect all python code to pass with a perfect score (10) using `pylint` with [this version](https://github.com/ESCOMP/CAM-SIMA/blob/development/test/.pylintrc) of `pylintrc`. However, external repos may have their own `pylintrc` version depending on their needs.

We also expect all python files to follow the [black code style and format](https://black.readthedocs.io/en/stable/the_black_code_style/index.html).

Finally, one can also follow the [Google Python](https://google.github.io/styleguide/pyguide.html) Style Guide.

## Fortran coding standards
The standards described in this section represent the CAM Fortran standards. Other Fortran standards:

- [CTSM Fortran Standards](https://wiki.ucar.edu/display/ccsm/Comprehensive+list+of+standards)
- [MOM Fortran Standards](https://github.com/mom-ocean/MOM6/wiki/Code-style-guide)

### MUST
* No naked `use` statements
* No continued single-line `if` statements (i.e., all `if` statements should have a `then` if the statement is on more than one line)
* Every namelist variable in each active namelist group is present in the namelist file. An active namelist group is one which may be read during the current run.
* All namelist variables except for logical quantities are initialized to invalid values (integer: `-HUGE(1)`, real: `NaN`, character: `'UNSET'`).
* Functions may _not_ have side effects, and should include the `pure` keyword.
* Do not combine statements on a single line (i.e., avoid use of the semi-colon to combine statements).
* Use `intent` for dummy arguments except for pointers.
* All variables of type real must have a specified kind, including literals.  For example, use `1.5_r8`, not `1.5` or `1.5D0`. Literals must also include the decimal point.
* All character declarations must use Fortran 90+ syntax (e.g., `character(len=*)` or `character(len=CL)`).
* All variable declarations must use Fortran 90+ syntax (i.e., must include the double colon between the attributes and the variable name).
* All type and procedure declarations must use Fortran 90+ syntax (i.e., must include the double colon before the type or procedure name).
* All modules should include an `implicit none` statement in the preamble (after the `use` statements). Module routines then do not need this statement.
* All optional arguments must be passed via keyword (e.g. use `call subroutine(x, optional_y=y)` instead of `call subroutine(x, y)` for the optional variable `optional_y`).
* Initialize local (non-parameter) variables in subroutines and functions at the top of the executable code, NOT on a variable declaration lines.
    - Initializing a local variable on a declaration line invokes the `SAVE` attribute and is not thread safe.
    - Local pointer variables MUST be initialized before other (non-initialization) statements. By default, use the `nullify` statement.
* All variables that are on the physics grid must have their horizontal dimension declared with `pcols`, even if only a subset of the variable is used in the subroutine or function. 
### SHOULD
* Avoid use of preprocessor directives (e.g., `#if`, `#ifdef`). Always try for runtime variable logic instead.
* Keep formula statements relatively short. Use temporary variables to break long formulas into easier-to-read sections.
* Use subroutines to avoid repeated (cut and paste) code logic.
* Avoid side effects in subroutines. Pass variables to routines instead of 'using' them from elsewhere.  
* Use the `pure` keyword if a subroutine has no side effects.
* List dummy arguments one per line, however, related items may be grouped.
* Dummy argument order should match the order in the argument list.
* Use symbolic numerical comparison operators (e.g., `==`, `/=`, `<`, `>=`) not old character versions (e.g., `.eq.`).
* Avoid the use of pointers as dummy arguments (exceptions must be discussed in design or code review)
* Modules should be default `private`. Public interfaces are declared after the `private` declaration.
* `private` module interfaces (i.e., subroutines and functions) should be declared private in the module header.
* Module names should conform to their filename (i.e., the module name should be the filename without the `.F90`).
* Functions _should_ use the `pure` attribute. If they cannot, the reason should be included as a comment in the function's preamble.
* All functions and subroutines should avoid un-necessary statements (e.g. a blank `return` at the end of a subroutine).
* `use` statements should be brought in at the smallest scope possible (e.g. inside individual subroutines instead of at the module level).

### Indentation and style

* *Scoping*: Indentation should follow scope. That is, whenever entering a new scope (e.g., `module`, `subroutine`, `if`, `do`), indent that scope relative to the scoping statement (recommended 3 spaces but each module should at least be self consistent).
* A single line should be less than 133 characters long.
* *Continue lines*: Indent continue lines 5 spaces or align with similar lines in statement.
* Use spaces to ease reading statements (e.g., before and after operators, after commas except in a dimensions list)
* Include a space after `if`, `else`, `end`, `do`, and `while`.
* Include a space before and after `::`
* No space after `only`, i.e., `only:`, not `only :`.
* When aligning code for readability, commas go immediately after a symbol (no space).

## Tips for configuring editors
### emacs (add to your `.emacs` file)
- To automatically remove trailing spaces whenever you save a file:
```
(add-hook 'before-save-hook 'delete-trailing-whitespace)
```
- To automatically indent with spaces instead of tabs:
```
(setq-default indent-tabs-mode nil)
```
- To use 4 spaces for each indent:
```
(setq tab-width 4)
```

### vi (add to your `.vimrc` file)
- To automatically remove trailing spaces whenever you save a file:
```
 autocmd BufWritePre * :%s/\s\+$//e
```