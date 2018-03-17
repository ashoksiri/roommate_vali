from linkedin.linkedin import LinkedInApplication ,LinkedInAuthentication
from linkedin.models import AccessToken
from linkedin.utils import enum

permissions = [
     'r_basicprofile',
     'r_emailaddress',
     'w_share',
     #'rw_company_admin',
     #'r_fullprofile',
     #'r_contactinfo'
     ]


import sys, os

from oauthlib import *

print(permissions)


PORT = 8888

# ============ Client Application Credentials ============ #
# Can be found here: https://www.linkedin.com/developer/apps

CLIENT_ID = '864hkqrc6ic9cn' #msrcosmos
CLIENT_SECRET = 'suuvLPuO3dC1KzG6' #msrcosmos

#CLIENT_ID = '816iemep7p4xfn'
#CLIENT_SECRET = 'eksJR6F31Dg8vOjO'

# ============ Authorization Code ============ #
# If not used, please set its value to: None
AUTH_CODE = None
# AUTH_CODE     = "##############################################################################################################################################################"

# Set it correctly or assign it to: None
AUTH_TOKEN = None

code = """AQQJjJM3UvkiHidbNQlkLooyxBN88y0nCferoT1_-PNWPhUtQ6IxCfAEghY1uGcL2J26BS6pnp6R9LVffTjZw-ppbR-mkzN4g8EOhsC0xLeNTCX3MYTplDxMUjkzf0QX_loaBznULxmhowpto2CZnON7jXZ2ng"""
state = "4762936a29becfae6fec5d12459b94cc"

#access_token = """AQWwXpwhaVmiFVbEpSnUpxsc6IlobsU9qPnjnBrpMFV-vgB93hawth6lRKBgO2KwO9TOWsErQPz5W7km6lgvn2orG69zCfFuq7OyWsRnHt9m7pLhsfYEGPEVxOsoobqExxW18NhyjAvy5hZj-O_DSdl4TFtKMOCDEnQ8B6GGLua0fClioafjhCBT5MOApuFj0D9tFS42Mlnj8JMhY4b49p6rJhMBm4JjC4hTnFCC4wUW9uVyClMU2Uth0UDx0DqCvHNOYWMeMX9dDmYvLaCEMkFXUwC5rAX5aKuSPQgJfS7NM4SK4nnnDoy0yePMx_y4Vt1QTtjquwcaP824Ahco86Yzo1gLrQ"""

authentication = LinkedInAuthentication(
                CLIENT_ID,
                CLIENT_SECRET,
                'http://localhost:8888/code',
                permissions=permissions

            )

#print(authentication.authorization_url)

# authentication.authorization_code = code
# authentication.state = state
# #
# print(authentication.get_access_token())

#sys.exit(0)
authentication.token= AccessToken(access_token='AQXRw7aKOIQpyDS1CqhceHUGssNbPwG-FTH3985dW7Qc0-e-_lqZErrGnntJPzw_KWeH-2V7bzH01UkC1wV_I4qQRJfcXG2MDo38yVCWjtCkvCgKrCsqZIhiBmlzGr0AWtUgOiRV_gy7nMzlAzCEv0R64CRrw1A7jaiRgdCT8sznO6MlC__psorX5xECT45ORyQTieFfE1M2bH9wKgut13Ng9y2WrN0Ja6eeP2ADSlxMUbg04RjAd7z4VndqlFFQv7hddOh3JhOToUCmIcxoWH5qaFOuZ6rgJ27qcZeSTPpPcdlg8ISjtkA4uU85WdavE9wTJ2ElV4eJBYZA5n6NKdTPSie9Lg', expires_in=5183999)
app = LinkedInApplication(authentication=authentication)
result = app.search_company(selectors=[{'companies': ['name', 'universal-name', 'website-url']}],
                                            params={'keywords': 'apple microsoft'})


#result = app.search_profile(selectors=[{'people': ['first-name', 'last-name']}], params={'keywords': 'apple microsoft'})

#app

#result = app.get_companies()

print(result)



# authentication.authorization_code = code
# authentication.state = state
# print(authentication.get_access_token())

#print(authentication.authorization_url)
#authentication.authorization_code = code
#print(authentication.authorization_url)
#print(authentication.get_access_token())
import sys
sys.exit(0)
# application = linkedin.LinkedInApplication(authentication)
# print(application.get_profile())

# AUTH_TOKEN    = '###################################################################################################################################################################################'

class LinkedInWrapper(object):

    def __init__(self, id, secret, port, auth_token=None, auth_code=None):
        self.id = id
        self.secret = secret

        self.callback_url = 'http://localhost:{0}/code/'.format(port)
        #self.callback_url = 'http://socialanalytics.msrcosmos.com'

        print("CLIENT ID: %s" % self.id)
        print("CLIENT SECRET: %s" % self.secret)
        print("Callback URL: %s" % self.callback_url)

        if auth_token == None:

            self.authentication = LinkedInAuthentication(
                self.id,
                self.secret,
                self.callback_url,

                permissions=['r_basicprofile', 'r_emailaddress', 'rw_company_admin', 'w_share']
            )

            if auth_code == None:
                print("Please open this address in your browser in order to obtain the authorization_code\n\n")
                print(self.authentication.authorization_url)

                print(
                    "\n\nIn case of error, please double check that the callback URL has been correctly added in the developer console: https://www.linkedin.com/developer/apps/")
                sys.exit()

            else:
                self.authentication.authorization_code = auth_code
                result = self.authentication.get_access_token()

                print("\n\nAccess Token:", result.access_token)
                print("Expires in (seconds):", result.expires_in)
                sys.exit()

        else:
            print
            self.application = LinkedInApplication(token=auth_token)


lkin_api = LinkedInWrapper(CLIENT_ID, CLIENT_SECRET, PORT, auth_token=AUTH_TOKEN, auth_code=code)

#########################################################################################
#########################################################################################
#########################################################################################

print("\n\n")
print("############## Requesting Information about your profile ##############")
print("\n")

print("Getting your profile information...")
print(lkin_api.application.get_profile())

print("\nGetting specific information on your profile...")
print(lkin_api.application.get_profile(
    selectors=['id', 'first-name', 'last-name', 'location', 'distance', 'num-connections', 'skills', 'educations']))

print("\nSearching for companies with keywords: 'apple microsoft' and getting specific information about them...")
print(lkin_api.application.search_company(selectors=[{'companies': ['name', 'universal-name', 'website-url']}],
                                          params={'keywords': 'apple microsoft'}))

print("\nMake the user to follow a company...")
print(lkin_api.application.follow_company(1035))

print("\nMake the user to unfollow a company...")
print(lkin_api.application.unfollow_company(1035))

print("\nPost a random post on the user's profile")
print(lkin_api.application.submit_share('Posting from the API using JSON', 'A title for your share', None,
                                        'https://www.linkedin.com', 'https://d.pr/3OWS'))

#########################################################################################
#########################################################################################
#########################################################################################

print("\n")
print("############## Requesting Information about your companies ##############")
print("Warning: you can not request any information on a company if you don't have admin rights on it")
print("\n")

company_list = lkin_api.application.get_companies_user_is_admin()
print("User is admin of: ", company_list)

if company_list["_total"] >= 0:
    example_company_id = company_list["values"][0]["id"]

    print("\nRequesting the company: %d" % example_company_id)
    print(lkin_api.application.get_companies(company_ids=[example_company_id, example_company_id, example_company_id]))
else:
    print("Unfortunately you are not admin of any company on LinkedIn")

print("\n")
print("############## Requesting Information about your connections ##############")
print("\n")

'''
# Deprecated Routes:

lkin_api.application.get_connections()
lkin_api.application.search_profile(selectors=[{'people': ['first-name', 'last-name']}], params={'keywords': 'apple microsoft'})
lkin_api.application.search_job(selectors=[{'jobs': ['id', 'customer-job-code', 'posting-date']}], params={'title': 'python', 'count': 2})
lkin_api.application.get_group(41001)

title = 'Scala for the Impatient'
summary = 'A new book has been published'
submitted_url = 'https://horstmann.com/scala/'
submitted_image_url = 'https://horstmann.com/scala/images/cover.png'
description = 'It is a great book for the keen beginners. Check it out!'
lkin_api.application.submit_group_post(41001, title, summary, submitted_url, submitted_image_url, description)

from linkedin.linkedin import NETWORK_UPDATES
update_types = (NETWORK_UPDATES.CONNECTION, NETWORK_UPDATES.PICTURE)
lkin_api.application.get_network_updates(update_types)

from linkedin.models import LinkedInRecipient, LinkedInInvitation
recipient = LinkedInRecipient(None, 'john.doe@python.org', 'John', 'Doe')
invitation = LinkedInInvitation('Hello John', "What's up? Can I add you as a friend?", (recipient,), 'friend')
application.send_invitation(invitation)
'''
