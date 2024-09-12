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

class FederatedCredentialManagementAccount:
    LOGIN_STATE_SIGNIN = "SignIn"
    LOGIN_STATE_SIGNUP = "SignUp"

    def __init__(self, account_dict):
        self.account_id = account_dict.get("accountId")
        self.email = account_dict.get("email")
        self.name = account_dict.get("name")
        self.given_name = account_dict.get("givenName")
        self.picture_url = account_dict.get("pictureUrl")
        self.idp_config_url = account_dict.get("idpConfigUrl")
        self.login_state = account_dict.get("loginState")
        self.terms_of_service_url = account_dict.get("termsOfServiceUrl")
        self.privacy_policy_url = account_dict.get("privacyPolicyUrl")

    def get_account_id(self):
        return self.account_id

    def get_email(self):
        return self.email

    def get_name(self):
        return self.name

    def get_given_name(self):
        return self.given_name

    def get_picture_url(self):
        return self.picture_url

    def get_idp_config_url(self):
        return self.idp_config_url

    def get_login_state(self):
        return self.login_state

    def get_terms_of_service_url(self):
        return self.terms_of_service_url

    def get_privacy_policy_url(self):
        return self.privacy_policy_url

