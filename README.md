# Type hint checker 
Checks that the parameters in functions and methods have type hints. _Type hint checker_ is intended to be used as a [pre-commit](https://pre-commit.com/) hook.

```python
def f1(a):
    pass
```
```shell script
> git commit 
type_hint_checker.......................................................Failed
    - hook id: type_hint_checker
    - duration: 0.33s
    - exit code: 1
    
    INFO:type_hint_checker:test.py: Missing type hint for parameter a (function f1), line 1
    INFO:type_hint_checker:test.py: Missing return type hint for function f1, line 1
```
## Quick start
1. Install pre-commit hooks [https://pre-commit.com/#install](https://pre-commit.com/#install)
   ```shell
   pip install pre-commit
   ```

2. Create a `.pre-commit-config.yaml` or use your existing config file. Add the following lines:
   ```yaml
   repos:
   -   repo: https://github.com/PaulinaPacyna/type-hint-checker
       rev: latest
       hooks:
       - id: type_hint_checker
         name: type_hint_checker
         description: Check that all python functions have type hints
         entry: type_hint_checker
         language: python
         verbose: true
         files: ".py$"
         args: [
           #--exit_zero, # always exit with 0 code
           #--exclude_files=tests, #exclude all paths that have the string tests inside
           #--exclude_parameters=^self$, #don't throw warnings about self parameter
        ]
   ```
3. Install the pre-commit hook
   ```
   pre-commit install
   ```
4. Commit a file
    ```shell
     echo  'def f1(a): pass' > test.py
     git commit test.py -m "Test type_hint_checker pre-commit hook"
    ```
   The output should be similar to this:
   ```
    type_hint_checker.......................................................Failed
    - hook id: type_hint_checker
    - duration: 0.33s
    - exit code: 1
    
    INFO:type_hint_checker:test.py: Missing type hint for parameter a (function f1), line 1
    INFO:type_hint_checker:test.py: Missing return type hint for function f1, line 1
   ```
   
### Run type hint checker from terminal
0. If you already have it installed in pre-commit hooks:
   ```
   pre-commit run type_hint_checker --all-files
   ```
1. Try the cli version out by running
   ```shell
   pip install type_hint_checker
   ```
2. Run the tool using
   ```shell
   type_hint_checker <path to file>
   ```
   or
   ```shell
   python -m type_hint_checker <path to file>
   ```
 
## Arguments
It is understandable that there are different coding standards. You can customize the behavior of this pre-commit hook by adding the following options to your `.pre-commit-config.yaml`.


| Argument | Usage | Default value | Example values |
| - | - | - | - |
| `--exit_zero` | If this flag is checked, the program always exits with 0 (success) code. It is strongly advised to use this flag together with `verbose: true` option in pre-commit options. | Not checked by default. | Either add `"--exit_zero"` to the `args` or don't. |
| `--exclude_files` | Regex specifying which files should not be checked. | Empty (all files are checked) | `"--exclude_files=^test_"` |
| `--exclude_parameters` | Regex specifying which parameters should not be checked. | `^self$` | `"--exclude_parameters=''"` (check all params) `"--exclude_parameters='(^self$\|logger)'"` |
| `--exclude_by_name` | Regex specifying names of functions, methods and classes that should not be checked | Empty (all functions, classes and methods are checked). | `"--exclude_by_name='^test_'"` |
| `--log-level` | If set to `DEBUG`, displays more logs. | `INFO` | `"--log-level=INFO"`,`"--log-level=DEBUG"` |
| `--ignore_comment` | You can change the content of the comment that disables checking a given function or method. By default `#no-check` excludes the item from being checked. See below for more info. | `no-check` | `"--ignore_comment='hint-no-check'"` | 

If you have troubles setting those values, it may be due to how your system parses special characters in command line options. Add `--log-level=DEBUG` to you `.pre-commit-config.yaml`. The log message will show you what values are passed as command line arguments.
```
DEBUG:type_hint_checker:{'filenames': ['test.py'],
 'exit_zero': False, 
'exclude_files': 'tests/', 
'exclude_parameters': '^self$', 
'exclude_by_name': '', 
'log_level': 'DEBUG', 
'ignore_comment': 'no-check'}

```
## Disable warnings
If you find type_hint_checker too restrictive, you are welcome to adjust its behavior. You can choose to ignore whole files, functions, parameters or single lines
### Ignore a path
If you don't want to check a certain file or folder, add the path to the `--exclude_files` argument. The argument must be a valid regex. To omit checking the directory `tests/` and the file `setup.py` use the following regex in your `.pre-commit-config`:
```yaml
args: ["--exclude_files='(tests/|setup.py)'" ]
```

### Ignore a function by name
You can disable checking functions that are named in a certain way. To disable checking all functions that begin with `test_` prefix, use:
```yaml
args: ["--exclude_by_name='^test_" ]
```
Then, for example this signature won't throw a warning:
```python
def test_filepath_in_log(caplog):
    ...
```
### Ignore a parameter by name
You can disable checking parameters with a regex, e.g. the `self` parameter
```yaml
args: [ --exclude_parameters=^self$ ]
```
With the option shown above, this method signature won't throw any warnings:
```python
class FileMaker:
    def read_file(self) -> str:
        ...
```
### With a comment
In special cases, you can just put `#no-check` comment next to the function, and the function will be omitted by this pre-commit hook.
```python 
def func(a: int, b: int, n): #no-check
    pass
```
The pre-commit hook will not warn you about the missing type hint for the return and parameter `n`.
You can customize the comment content using `--ignore_comment` option.
### In case of fire
You can always commit without any pre-commit checks using 
```shell script
git commit --no-verify
```
## Pep8 specification about type hints
The default formatting options were set in accordance to [PEP8 484](https://peps.python.org/pep-0484/)
## Tests
To run the tests, run 
```shell script
python -m pytest tests/
```
