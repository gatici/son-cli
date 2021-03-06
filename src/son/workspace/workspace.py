#  Copyright (c) 2015 SONATA-NFV, UBIWHERE
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, UBIWHERE
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).

import logging
import coloredlogs
import sys
import os
from os.path import expanduser
import yaml

from son.workspace.project import Project

log = logging.getLogger(__name__)


class Workspace:
    BACK_CONFIG_VERSION = "0.03"
    CONFIG_VERSION = "0.05"
    DEFAULT_WORKSPACE_DIR = os.path.join(expanduser("~"), ".son-workspace")
    DEFAULT_SCHEMAS_DIR = os.path.join(expanduser("~"), ".son-schema")
    __descriptor_name__ = "workspace.yml"

    def __init__(self, ws_root, config=None, ws_name=None, log_level=None):

        self._ws_root = ws_root
        self._ws_config = dict()

        if config:
            self._ws_config = config

        else:
            self.load_default_config()
            if ws_name:
                self.config['name'] = ws_name
            if log_level:
                self.config['log_level'] = log_level

        coloredlogs.install(level=self.config['log_level'])

    @property
    def workspace_root(self):
        return self._ws_root

    @property
    def workspace_name(self):
        return self.config['name']

    @property
    def default_descriptor_extension(self):
        return self.config['default_descriptor_extension']

    @property
    def log_level(self):
        return self.config['log_level']

    @log_level.setter
    def log_level(self, value):
        self.config['log_level'] = value
        coloredlogs.install(level=value)

    @property
    def schemas_local_master(self):
        return self.config['schemas_local_master']

    @property
    def schemas_remote_master(self):
        return self.config['schemas_remote_master']

    @property
    def validate_watchers(self):
        return self.config['validate_watchers']

    @property
    def config(self):
        return self._ws_config

    @property
    def catalogues_dir(self):
        return self.config['catalogues_dir']

    @property
    def configuration_dir(self):
        return self.config['configuration_dir']

    @property
    def platforms_dir(self):
        return self.config['platforms_dir']

    @property
    def projects_dir(self):
        return self.config['projects_dir']

    @property
    def ns_catalogue_dir(self):
        return os.path.join(self.catalogues_dir, 'ns_catalogue')

    @property
    def vnf_catalogue_dir(self):
        return os.path.join(self.catalogues_dir, 'vnf_catalogue')

    def load_default_config(self):
        self.config['version'] = self.CONFIG_VERSION
        self.config['name'] = 'SONATA Workspace'
        self.config['log_level'] = 'INFO'

        self.config['catalogues_dir'] = 'catalogues'
        self.config['configuration_dir'] = 'configuration'
        self.config['platforms_dir'] = 'platforms'
        self.config['projects_dir'] = 'projects'

        self.config['schemas_local_master'] = Workspace.DEFAULT_SCHEMAS_DIR
        self.config['schemas_remote_master'] = \
            "https://raw.githubusercontent.com/sonata-nfv/son-schema/master/"

        self.config['default_descriptor_extension'] = 'yml'

        self.config['service_platforms'] = \
            {'sp1':
                {'url': 'http://sp.int3.sonata-nfv.eu:32001',
                 'credentials': {'username': 'sonata',
                                 'password': 's0n@t@',
                                 'token_file': 'token.txt',
                                 'signature': {'pub_key': '',
                                               'prv_key': '',
                                               'cert': ''
                                               }
                                 }
                 }
             }
        self.config['default_service_platform'] = 'sp1'
        self.config['validate_watchers'] = \
            {os.path.join(self.workspace_root, self.config['projects_dir']):
                {'type': 'project',
                 'syntax': True,
                 'integrity': True,
                 'topology': True
                 }
             }

    def create_dirs(self):
        """
        Create the base directory structure for the workspace
        Invoked upon workspace creation.
        """
        log.info('Creating workspace at %s', self.workspace_root)
        os.makedirs(self.workspace_root, exist_ok=False)

        dirs = [self.config['catalogues_dir'],
                os.path.join(self.config['catalogues_dir'], 'ns_catalogue'),
                os.path.join(self.config['catalogues_dir'], 'vnf_catalogue'),
                self.config['configuration_dir'],
                self.config['platforms_dir'],
                self.config['projects_dir'],
                ]

        for d in dirs:
            path = os.path.join(self.workspace_root, d)
            os.makedirs(path, exist_ok=True)

    def write_ws_descriptor(self):
        """
        Creates a workspace configuration file descriptor.
        This is triggered by workspace creation and configuration changes.
        """
        cfg_d = self.config.copy()
        ws_file_path = os.path.join(self.workspace_root,
                                    Workspace.__descriptor_name__)

        ws_file = open(ws_file_path, 'w')
        yaml.dump(cfg_d, ws_file, default_flow_style=False)

        return cfg_d

    def create_files(self):
        self.write_ws_descriptor()

    def check_ws_exists(self):
        ws_file = os.path.join(self.workspace_root,
                               Workspace.__descriptor_name__)
        return os.path.exists(ws_file) or os.path.exists(self.workspace_root)

    @staticmethod
    def __create_from_descriptor__(ws_root):
        """
        Creates a Workspace object based on a configuration descriptor
        :param ws_root: base path of the workspace
        :return: Workspace object
        """
        ws_filename = os.path.join(ws_root, Workspace.__descriptor_name__)
        if not os.path.isdir(ws_root) or not os.path.isfile(ws_filename):
            log.error("Unable to load workspace descriptor '{}'"
                      .format(ws_filename))
            return None

        ws_file = open(ws_filename, 'r')
        try:
            ws_config = yaml.load(ws_file)

        except yaml.YAMLError as exc:
            log.error("Error parsing descriptor file '{0}': {1}"
                      .format(ws_filename, exc))
            return
        if not ws_config:
            log.error("Couldn't read descriptor file: '{0}'"
                      .format(ws_filename))
            return

        if not ws_config['version'] == Workspace.CONFIG_VERSION:

            if ws_config['version'] < Workspace.BACK_CONFIG_VERSION:
                log.error("Workspace configuration version '{0}' is no longer "
                          "supported (<{1})"
                          .format(ws_config['version'],
                                  Workspace.BACK_CONFIG_VERSION))
                return
            if ws_config['version'] > \
                    Workspace.CONFIG_VERSION:
                log.error("Workspace configuration version '{0}' is ahead of "
                          "the current supported version (={1})"
                          .format(ws_config['version'],
                                  Workspace.CONFIG_VERSION))
                return

        ws = Workspace(ws_root, config=ws_config)

        # Make adjustments to support backwards compatibility
        # 0.03
        if ws_config['version'] == "0.03":
            ws.config['validate_watchers'] = \
                {os.path.join(ws.workspace_root, ws.config['projects_dir']):
                    {'type': 'project',
                     'syntax': True,
                     'integrity': True,
                     'topology': True
                     }
                 }

        # 0.04
        if ws_config['version'] <= "0.04":
            sps = ws.config['service_platforms']
            for sp_key, sp in sps.items():
                sp['credentials']['signature'] = dict()
                sp['credentials']['signature']['pub_key'] = ''
                sp['credentials']['signature']['prv_key'] = ''
                sp['credentials']['signature']['cert'] = ''

        if ws_config['version'] < Workspace.CONFIG_VERSION:
            log.warning("Loading workspace with an old configuration "
                        "version ({0}). Updated configuration: {1}"
                        .format(ws_config['version'], ws.config))
        return ws

    @property
    def default_service_platform(self):
        return self.config['default_service_platform']

    @default_service_platform.setter
    def default_service_platform(self, sp_id):
        self.config['default_service_platform'] = sp_id

    @property
    def service_platforms(self):
        return self.config['service_platforms']

    @service_platforms.setter
    def service_platforms(self, sps):
        self.config['service_platforms'] = sps

    def get_service_platform(self, sp_id):
        if sp_id not in self.service_platforms.keys():
            return
        return self.service_platforms[sp_id]

    def add_service_platform(self, sp_id):
        if sp_id in self.service_platforms.keys():
            return
        self.service_platforms[sp_id] = {'url': '',
                                         'credentials': {'username': '',
                                                         'password': '',
                                                         'token_file': '',
                                                         'signature': {
                                                             'pub_key': '',
                                                             'prv_key': '',
                                                             'cert': ''
                                                         }}
                                         }

    def config_service_platform(self, sp_id, default=None, url=None,
                                username=None, password=None, token=None,
                                pub_key=None, prv_key=None, cert=None):

        if sp_id not in self.service_platforms.keys():
            return

        sp = self.service_platforms[sp_id]

        if url:
            sp['url'] = url

        if username:
            sp['credentials']['username'] = username

        if password:
            sp['credentials']['password'] = password

        if token:
            sp['credentials']['token_file'] = token

        if pub_key:
            sp['credentials']['signature']['pub_key'] = pub_key

        if prv_key:
            sp['credentials']['signature']['prv_key'] = prv_key

        if cert:
            sp['credentials']['signature']['cert'] = cert

        if default:
            self.default_service_platform = sp_id

        # update workspace config descriptor
        self.write_ws_descriptor()

    def __eq__(self, other):
        """
        Function to assert if two workspaces have the
        same configuration. It overrides the super method
        as is only the need to compare configurations.
        """
        return isinstance(other, type(self)) \
            and self.workspace_name == other.workspace_name \
            and self.workspace_root == other.workspace_root \
            and self.config == other.config


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate new sonata workspaces and project layouts")

    parser.add_argument(
        "--init",
        help="Create a new sonata workspace",
        action="store_true")

    parser.add_argument(
        "--workspace",
        help="location of existing (or new) workspace. "
             "If not specified will assume '{}'"
             .format(Workspace.DEFAULT_WORKSPACE_DIR),
        required=False)

    parser.add_argument(
        "--project",
        help="create a new project at the specified location",
        required=False)

    parser.add_argument(
        "--debug",
        help="increases logging level to debug",
        required=False,
        action="store_true")

    args = parser.parse_args()

    log_level = "INFO"
    if args.debug:
        log_level = "DEBUG"
        coloredlogs.install(level=log_level)

    # Ensure that one argument is given (--init, --workspace or --project)
    if not args.init and not args.workspace and not args.project:
        parser.print_help()
        return

    # Ensure that argument --workspace is not alone
    if not args.init and args.workspace and not args.project:
        parser.print_help()
        return

    # If workspace arg is not given, create a workspace in user home
    if args.workspace is None:
        ws_root = Workspace.DEFAULT_WORKSPACE_DIR

        # If a workspace already exists at user home, throw an error and quit
        if args.init and os.path.isdir(ws_root):
            print("A workspace already exists in {}. "
                  "Please specify a different location.\n"
                  .format(ws_root), file=sys.stderr)
            exit(1)

    else:
        ws_root = expanduser(args.workspace)

    if args.init:
        ws = Workspace(ws_root, log_level=log_level)
        if ws.check_ws_exists():
            print("A workspace already exists at the "
                  "specified location, exiting",
                  file=sys.stderr)
            exit(1)

        log.debug("Attempting to create a new workspace")
        cwd = os.getcwd()
        ws.create_dirs()
        ws.create_files()
        os.chdir(cwd)
        log.debug("Workspace created.")
    else:
        ws = Workspace.__create_from_descriptor__(ws_root)
        if not ws:
            print("Could not find a SONATA workspace "
                  "at the specified location",
                  file=sys.stderr)
            exit(1)

    if args.project is not None:
        log.debug("Attempting to create a new project")

        prj_root = os.path.expanduser(args.project)
        proj = Project(ws, prj_root)
        proj.create_prj()

        log.debug("Project created.")
