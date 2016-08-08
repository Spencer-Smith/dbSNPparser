Recommended to use failfast if tests are failing. Failfast option ends testing as soon as a test fails.
This will allow you to compare output.txt to the "expected_..." output for the test.

command:
	python -m unittest test_parser.py -f