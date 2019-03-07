# noqa E902
import os
import sys

import pytest


test_pkg = 'xyztraj'
cover_pkg = test_pkg

cwd = os.path.expandvars(os.getcwd())
build_dir = os.getenv('TRAVIS_BUILD_DIR', os.path.expanduser('~'))

# where to write reports
reports_dir = os.path.join(build_dir, 'reports')

# reports
junit_xml = os.path.join(reports_dir, 'junit.xml')
coverage_xml = os.path.join(reports_dir, 'coverage.xml')

if not os.path.exists(reports_dir):
    os.makedirs(reports_dir)
    print('junit destination:', junit_xml)

    pytest_args = (
        "-v --pyargs {test_pkg} "
        "--cov={cover_pkg} "
        "--cov-report=xml:{dest_report} "
        "--doctest-modules "
        "--junit-xml={junit_xml} "
        #"--durations=20 "
        .format(test_pkg=test_pkg, cover_pkg=cover_pkg,
                dest_report=coverage_xml, junit_xml=junit_xml,
        ).split(' '))

    print("args:", pytest_args)
    res = pytest.main(pytest_args)

    sys.exit(res)
