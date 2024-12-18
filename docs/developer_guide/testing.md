# Testing

After updating the code, ensure that all tests pass. To run the tests, use the following command. 

```bash
hatch run test
```

If you would like to run the tests in your IDE, use the `default` virtual environment.

To generate a coverage report with the tests, run the following command.

```bash
hatch run test-and-report
```

Once new commits are pushed to the `main` branch, the [`test.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/test.yaml) workflow will be automatically triggered, and the tests will run.

## About [`testdata`](https://github.com/rendercv/rendercv/tree/main/tests/testdata) folder

In some of the tests:

- RenderCV generates an output with a sample input.
- Then, the output is compared with a reference output, which has been manually generated and stored in `testdata`. If the files differ, the tests fail.


When the `testdata` folder needs to be updated, it can be manually regenerated by setting `update_testdata` to `True` in `conftest.py` and running the tests.

!!! warning
    - Whenever the `testdata` folder is generated, the files should be reviewed manually to ensure everything works as expected.
    - `update_testdata` should be set to `False` before committing the changes.
