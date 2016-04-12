import unittest
from unittest import mock
import pkg_resources
import os
from urllib.error import HTTPError
from son.package.package import Packager, load_local_schema, load_remote_schema
from son.workspace.workspace import Workspace
from unittest.mock import patch


class IntPDTester(unittest.TestCase):

    __pfd__ = {
        'name': 'sonata-project-sample',
        'group': 'com.sonata.project',
        'version': '0.0.1',
        'maintainer': 'Name, Company, Contact',
        'description': 'Project description',
        'catalogues': ['personal'],
        'publish_to': ['personal']
    }

    def __init__(self, *args, **kwargs):
        super(IntPDTester, self).__init__(*args, **kwargs)
        ws = Workspace("")
        self.pck = Packager(workspace=ws, prj_path='/', generate_pd=False)

    def test_correct_gds(self):
        """ Test the correct general description section """
        print("test_correct_gds")
        gsd = self.pck.package_gds(IntPDTester.__pfd__)
        self.assertNotEqual(gsd, False)
        print("END test_correct_gds")

    def test_incomplete_gds(self):
        """ Test the returning message when the provided project has incomplete information."""
        print("test_incomplete_gds")
        pfd = IntPDTester.__pfd__
        pfd.pop('name')
        gsd = self.pck.package_gds(pfd)
        self.assertEqual(gsd, False)
        print("END test_incomplete_gds")


class IntLoadSchemaTests(unittest.TestCase):

    def test_load_invalid_local_template(self):
        """Test if the load schema is loading only available templates"""
        print("test_load_invalid_local_template")
        self.assertRaises(FileNotFoundError, load_local_schema, "test")
        print("END test_load_invalid_local_template")

    def test_load_valid_local_schema(self):
        """ Test if the load schema is correctly loading the templates """
        # Access to local stored schemas for this test
        schema_f = pkg_resources.resource_filename(__name__, os.path.join("son-schema", 'pd-schema.yml'))
        schema = load_local_schema(schema_f)
        self.assertIsInstance(schema, dict)

        schema_f = pkg_resources.resource_filename(__name__, os.path.join("son-schema", 'nsd-schema.yml'))
        schema = load_local_schema(schema_f)
        self.assertIsInstance(schema, dict)

        schema_f = pkg_resources.resource_filename(__name__, os.path.join("son-schema", 'vnfd-schema.yml'))
        schema = load_local_schema(schema_f)
        self.assertIsInstance(schema, dict)

    def test_load_invalid_remote_template_unavailable(self):
        """ Test if it raises a HTTP error with a valid but unavailable schema URL """
        self.assertRaises(HTTPError, load_remote_schema, "http://somerandomurl.com/artifact.yml")

    def test_load_invalid_remote_template_invalid(self):
        """ Test if it raises an error with an invalid schema URL """
        self.assertRaises(ValueError, load_remote_schema, "some.incorrect/..url")

    def test_load_valid_remote_schema(self):
        """ Test if the load_remote_schema is retrieving and loading the templates correctly """
        schema = load_remote_schema(Packager.schemas[Packager.SCHEMA_PACKAGE_DESCRIPTOR]['remote'])
        self.assertIsInstance(schema, dict)