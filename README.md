# Annotation checker 
Checks that the parameters in functions and methods are annotated. _Annotation checker_ is intended to be used as a [pre-commit](https://pre-commit.com/) hook.

## Quick start
1. Install pre-commit hooks [https://pre-commit.com/#install](https://pre-commit.com/#install)
   ```shell
   pip install pre-commit
   ```

2. Create a `.pre-commit-hooks.yaml` or use your existing config file. Add the following lines:
   ```yaml
   repos:
   -   repo: https://github.com/PaulinaPacyna/annotation-checker
       rev: latest
       hooks:
       - id: annotation_checker
         name: annotation_checker
         description: Check that all python functions are annotated
         entry: annotation_checker
         language: python
         files: ".py"
         args: [--exit_zero, # always exit with 0 code
                --exclude_files=tests, 
                --exclude_parameters=^self$,
         ]
        verbose: true
   ```
3. Install the pre-commit hook
   ```
   pre-commit install
   ```
4. Commit a file

### Run annotation checker from terminal
0. If you already have it installed in pre-commit hooks:
   ```
   pre-commit run annotation_checker --all-files
   ```
1. Try the cli version out by running
   ```shell
   pip install annotation_checker
   ```
2. Run the tool using
   ```shell
   annotation_checker <path to file>
   ```
   or
   ```shell
   python -m annotation_checker <path to file>
   ```
 
## Arguments
It is understandable that there are different coding standards. You can customize the behavior of this pre-commit hook by adding the following options to your `.pre-commit-config.yaml`.


| Argument | Usage | Default value | Example values |
| - | - | - | - |
| `--exit_zero` | If this flag is checked, the program always exits with 0 (success) code. It is strongly advised to use this flag together with `verbose: true` option in pre-commit options. | Not checked by default. | Either add `"--exit_zero"` to the `args` or don't. |
| `--exclude_files` | Regex specifying which files should not be checked. | Empty (all files are checked) | `"--exclude_files=^test_"` |
| `--exclude_parameters` | Regex specifying which parameters should not be checked. | `^self$` | `"--exclude_parameters=''"` (check all params) `"--exclude_parameters='(^self$|logger)'"` |
| `--exclude_by_name` | Regex specifying names of functions, methods and classes that should not be checked | Empty (all functions, classes and methods are checked). | `"--exclude_by_name=^test_"` |
| `--log-level` | If set to debug, dispalays more logs. | `INFO` | `"--log-level=INFO"`,`"--log-level=DEBUG"` |
| `--ignore_comment` | You can change the comment that disables checking a given function or method. By default `#no-check` excludes the item from being checked. See below for more info. | `no-check` | `"--ignore_comment='hint-no-check'"` | 

## Use cases 
## Disable warnings
### For a certain path
### By a function name
### By a parameter name
### With a comment
### In case of fire
You can always commit without any pre-commit checks using 
```shell script
git commit --no-verify
```
## Tests
To run the tests, run 
```shell script
python -m pytest tests/
```