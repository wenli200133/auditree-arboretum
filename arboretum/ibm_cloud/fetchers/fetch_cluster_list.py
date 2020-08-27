# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""IBM Cloud cluster list fetcher."""

import json

from compliance.evidence import store_raw_evidence
from compliance.fetch import ComplianceFetcher

from ..util.iam import get_tokens


class ClusterListFetcher(ComplianceFetcher):
    """Fetch the list of IBM Cloud clusters."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        headers = {'Accept': 'application/json'}
        cls.session('https://containers.cloud.ibm.com', **headers)

        return cls

    @classmethod
    def tearDownClass(cls):
        """Destroys the fetcher object."""
        cls.session().close()

    @store_raw_evidence('ibm_cloud/cluster_list.json')
    def fetch_cluster_list(self):
        """Fetch IBM Cloud cluster list."""
        accounts = self.config.get('org.ibm_cloud.accounts')
        cluster_list = {}
        for account in accounts:
            cluster_list[account] = self._get_cluster_list(account)
        return json.dumps(cluster_list)

    def _get_cluster_list(self, account):

        # get credential for the account
        api_key = getattr(self.config.creds['ibm_cloud'], f'{account}_api_key')
        tokens = get_tokens(api_key)
        access_token = tokens['access_token']
        # get cluster list
        # https://cloud.ibm.com/apidocs/kubernetes#getclusters
        headers = {'Authorization': f'Bearer {access_token}'}
        resp = self.session().get('/global/v1/clusters', headers=headers)
        resp.raise_for_status()
        return resp.json()
