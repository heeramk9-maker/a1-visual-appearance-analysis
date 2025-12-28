from importlib import import_module

m = import_module('tests.test_cache')
try:
    m.test_pipeline_uses_cache_and_skips_reanalysis()
    print('OK: cache test passed')
except AssertionError as e:
    print('FAIL: cache test failed', e)
except Exception as e:
    print('ERROR running cache test:', e)
