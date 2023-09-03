# Annotation checker 
Checks that arguments in functions and methods are annotated. _Annotation checker_ is intended to be used as a [pre-commit](https://pre-commit.com/) hook.

## Quick start
0. Install pre-commit hooks [https://pre-commit.com/#install](https://pre-commit.com/#install)
   ```shell
   pip install pre-commit
   ```
1. Try the cli version out by running
   ```shell
   annotation_checker <path to file>
   ```
3. Create a `.pre-commit-hooks.yaml` or use your existing config file. Add the following lines:
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
      args: [--strict=True]
  ``` 
