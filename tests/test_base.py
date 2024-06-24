"""Base module tests for brooks_xpeel_module."""

import unittest


class TestModule_Base(unittest.TestCase):
    """Base test class for brooks_xpeel_module."""

    pass


class TestImports(TestModule_Base):
    """Test the imports of the module are working correctly"""

    def test_driver_import(self):
        """Test the driver and rest node imports"""
        import brooks_xpeel_driver
        import old_node

        assert brooks_xpeel_driver
        assert old_node


if __name__ == "__main__":
    unittest.main()
