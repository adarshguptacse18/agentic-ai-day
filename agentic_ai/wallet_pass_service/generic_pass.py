import json
import os
import uuid

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials
from google.auth import jwt, crypt

# [END imports]

ISSUER_ID = "3388000000022958565"  # RECEIVED FROM GOOGLE WALLET API DASHBOARD
CLASS_SUFFIX = "generic"  # -> class ID of a generic pass sclass in Google Walled API Dashboard


class GenericPass:
    """Demo class for creating and managing Generic passes in Google Wallet.

    Attributes:
        key_file_path: Path to service account key file from Google Cloud
            Console. Environment variable: GOOGLE_APPLICATION_CREDENTIALS.
        base_url: Base URL for Google Wallet API requests.
    """

    def __init__(self):
        # get the current directory path and then join it with steady-habitat-467108-n7-6e6567eec883.json
        self.key_file_path = os.path.join(os.path.dirname(__file__), "steady-habitat-467108-n7-6e6567eec883.json")
        # Set up authenticated client
        self.auth()

    # [END setup]

    # [START auth]
    def auth(self):
        """Create authenticated HTTP client using a service account file."""
        self.credentials = Credentials.from_service_account_file(
            self.key_file_path, scopes=["https://www.googleapis.com/auth/wallet_object.issuer"]
        )

        self.client = build("walletobjects", "v1", credentials=self.credentials)

    # [END auth]

    # [START jwtNew]
    def create_jwt_new_objects(self, object_suffix: str, title: str, header: str, text_modules: list) -> str:
        """Generate a signed JWT that creates a new pass class and object.

        When the user opens the "Add to Google Wallet" URL and saves the pass to
        their wallet, the pass class and object defined in the JWT are
        created. This allows you to create multiple pass classes and objects in
        one API call when the user saves the pass to their wallet.

        Args:
            object_suffix (str): Developer-defined unique ID for the pass object.


        Returns:
            str: JWT token

        """

        # See link below for more information on required properties
        # https://developers.google.com/wallet/generic/rest/v1/genericclass
        new_class = {"id": f"{ISSUER_ID}.{CLASS_SUFFIX}"}

        # See link below for more information on required properties
        # https://developers.google.com/wallet/generic/rest/v1/genericobject
        new_object = {
            "id": f"{ISSUER_ID}.{object_suffix}",
            "classId": f"{ISSUER_ID}.{CLASS_SUFFIX}",
            "state": "ACTIVE",
            "textModulesData": text_modules,
            "cardTitle": {"defaultValue": {"language": "en-US", "value": title}},
            "header": {"defaultValue": {"language": "en-US", "value": header}},
            "hexBackgroundColor": "#4285f4",
        }

        # Create the JWT claims
        claims = {
            "iss": self.credentials.service_account_email,
            "aud": "google",
            "origins": ["www.example.com"],
            "typ": "savetowallet",
            "payload": {
                # The listed classes and objects will be created
                "genericClasses": [new_class],
                "genericObjects": [new_object],
            },
        }

        # The service account credentials are used to sign the JWT
        signer = crypt.RSASigner.from_service_account_file(self.key_file_path)
        token = jwt.encode(signer, claims).decode("utf-8")

        return token

    # [END jwtNew]
