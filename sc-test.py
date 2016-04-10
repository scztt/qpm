#!/usr/bin/env python
import sys
import qpmlib
import qpmlib.sclang_testing as testing

def generate_summary(test_plan, duration):
    total = 0
    failed = 0
    for test in test_plan.get('tests', []):
        for subtest in test.get('results', []):
            total += 1
            if not(subtest.get('pass')):
                failed += 1

    return {
        'total_tests': total,
        'failed_tests': failed,
        'duration': duration
    }

sclang = '/Users/fsc/Documents/_code/SuperCollider-qt-compilation/build-debugger/Install/SuperCollider/SuperCollider.app/Contents/MacOS/sclang'
classlib = '/Users/fsc/Documents/_code/SuperCollider-qt-compilation/build-debugger/Install/SuperCollider/SuperCollider.app/Contents/Resources/SCClassLibrary'

test_plan = {
    'tests': []
}

for test_specifier in ["*:*"]:
    test_suite, test_name = test_specifier.split(':')
    test_plan['tests'].append({
        'suite': test_suite, 'test': test_name
    })

test_run = testing.SCTestRun(sclang, classlib, test_plan)
test_run.print_stdout = True
result = test_run.run()
summary = generate_summary(result, test_run.duration)

for test in result['tests']:
    print { 'test_result': test }
print { 'test_summary': summary }

if summary['failed_tests'] > 0:
    sys.exit(summary['failed_tests'])

