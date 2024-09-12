# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from webdriver.common.fedcm_account import FederatedCredentialManagementAccount

class FederatedCredentialManagementDialog:
    DIALOG_TYPE_ACCOUNT_LIST = "AccountChooser"
    DIALOG_TYPE_AUTO_REAUTH = "AutoReauthn"

    def __init__(self, execute_method):
        self.execute_method = execute_method

    def cancel_dialog(self):
        self.execute_method("cancelDialog")

    def select_account(self, index):
        self.execute_method("selectAccount", {"accountIndex": index})

    def get_dialog_type(self):
        return self.execute_method("getFedCmDialogType")

    def get_title(self):
        result = self.execute_method("getFedCmTitle")
        return result.get("title")

    def get_subtitle(self):
        result = self.execute_method("getFedCmTitle")
        return result.get("subtitle")

    def get_accounts(self):
        account_list = self.execute_method("getAccounts")
        return [FederatedCredentialManagementAccount(account) for account in account_list]
