# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
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

"""XAgent Email Extension"""
from XAgentServer.application.core.envs import XAgentServerEnv


def email_content(user):
    html_body = f"""
<body style="font-family: Arial, sans-serif;background-color: #f5f5f5;margin: 0; padding: 0;">
    <div style="background-color: #ffffff;margin: 0 auto;padding: 20px;border-radius: 10px;box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
        <h1 style="font-size: 28px;margin-bottom: 20px;">Hello {user['name']},</h1>
        <p style="font-size: 16px;line-height: 1.5;color: #333333;text-indent:2em;">Welcome to XAgent, your personal assistant! Thanks for signing up for XAgent. There are some information about your account:</p>
        <p style="font-size: 16px;line-height: 1.5;color: #333333;text-indent:2em;">Your XAgent Account: <b>{user["email"]}</b></p>
        <p style="font-size: 16px;line-height: 1.5;color: #333333;text-indent:2em;">You need to use this token for authentication on subsequent logins: </p>
        <p style="font-size: 16px;line-height: 1.5;color: #333333;text-indent:2em;">You need to use this token for authentication on subsequent logins: </p>
        <p style="font-size: 16px;line-height: 1.5;color: #333333;text-indent:2em;">Token: <b>{user["token"]}</b></p>
        
        <p style="font-size: 16px;line-height: 1.5;color: #333333;text-indent:2em;">Next is an activation link. You need to click on this link to activate your account. After that, you will be able to use XAgent happily:<a href="{XAgentServerEnv.Email.auth_server}/auth?user_id={user["user_id"]}&token={user["token"]}">{XAgentServerEnv.Email.auth_server}/auth?user_id={user["user_id"]}&token={user["token"]}</a>! This Verification link will expire in 7 days.</p>
        <p>If you have any questions, please contact us at yourxagent@gmail.com .</p>
        <p style="margin-top: 20px;font-size: 14px;color: #999999;text-indent:2em;">Best wishes!</p>
        <p style="margin-top: 20px;font-size: 14px;color: #999999;">XAgent Team</p>
    </div>
</body>"""
    return html_body
