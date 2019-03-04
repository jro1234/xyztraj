import os
import sys

import pytest

test_pkg = 'xyztraj'
cover_pkg = test_pkg

# where to write junit xml
junit_xml = os.path.join(os.getenv('TRAVIS_BUILD_DIR', os.path.expanduser('~')),
                                 'reports', 'junit.xml')

print("Current directory: ", os.getcwd())
print("'TRAVIS_BUILD_DIR': ", os.path.join(os.getenv('TRAVIS_BUILD_DIR', os.path.expanduser('~'))))

target_dir = os.path.dirname(junit_xml)

if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    print('junit destination:', junit_xml)
    njobs_args = '-p no:xdist' if os.getenv('TRAVIS') else '-n2'

    pytest_args = ("-v --pyargs {test_pkg} "
        "--cov={cover_pkg} "
        "--cov-report=xml:{dest_report} "
        "--doctest-modules "
        "{njobs_args} "
        "--junit-xml={junit_xml} "
        "-c {pytest_cfg}"
        #"--durations=20 "
        .format(test_pkg=test_pkg, cover_pkg=cover_pkg,
                junit_xml=junit_xml, pytest_cfg='setup.cfg',
                dest_report=os.path.join(os.path.expanduser('~/'), 'coverage.xml'),
                njobs_args=njobs_args,
        )
        .split(' '))

    print("args:", pytest_args)
    res = pytest.main(pytest_args)

    sys.exit(res)

