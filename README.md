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

### Run annotation checker from terminal
0. If you already have it installed in pre-commit hooks:
   ```
   pre-commit run annotation_checker --all-files
   ```
1. Try the cli version out by running
   ```shell
   pip install annotation_checker
   annotation_checker <path to file>
   ```
#### Tests
To run the tests, run 
```shell script
python -m pytest tests/
```