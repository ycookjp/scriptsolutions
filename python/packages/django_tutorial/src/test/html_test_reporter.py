import os
from django.test.runner import DiscoverRunner
from HtmlTestRunner import HTMLTestRunner

class MyHTMLTestRunner(HTMLTestRunner):
    def __init__(self, **kwargs):
        # Pass any required options to HTMLTestRunner 
        super().__init__(
                output=os.path.dirname(__file__) + '/../../target/site/test-report',
                report_name='python-progs',
                add_timestamp=False,
                combine_reports=True,
                **kwargs
        )

class HtmlTestReporter(DiscoverRunner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Patch over the test_runner in the super class.
        html_test_runner = MyHTMLTestRunner
        self.test_runner=html_test_runner
