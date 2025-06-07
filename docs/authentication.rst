Authentication
==============

VeeDB supports authenticated access to the VNDB API through API tokens. Authentication is required for certain operations like accessing private user data and managing user lists.

Getting an API Token
--------------------

To get an API token:

1. **Log in** to your VNDB account at https://vndb.org
2. **Navigate** to your profile tokens page: https://vndb.org/u/tokens
3. **Create** a new token with the permissions you need
4. **Copy** the generated token and store it securely

Token Permissions
-----------------

VNDB API tokens can have different permission levels:

- **listread**: Read access to your user lists
- **listwrite**: Write access to your user lists (includes read)
- **no permissions**: Access to public data only

Choose the minimum permissions needed for your application.

Using API Tokens
----------------

Environment Variables (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Store your API token as an environment variable:

.. code-block:: bash

   # Windows PowerShell - Temporary
   $env:VNDB_API_TOKEN = "your-token-here"
   
   # Windows PowerShell - Permanent
   [Environment]::SetEnvironmentVariable("VNDB_API_TOKEN", "your-token-here", "User")

Then use it in your code:

.. code-block:: python

   import os
   from veedb import VNDB

   async def main():
       api_token = os.environ.get("VNDB_API_TOKEN")
       
       async with VNDB(api_token=api_token) as client:
           auth_info = await client.get_authinfo()
           print(f"Authenticated as: {auth_info.username}")

Direct Token Usage
~~~~~~~~~~~~~~~~~~

For testing or simple scripts, you can pass the token directly:

.. code-block:: python

   from veedb import VNDB

   async def main():
       async with VNDB(api_token="your-token-here") as client:
           # Your authenticated operations here
           pass

**Warning**: Never hardcode tokens in production code or commit them to version control.

Configuration Files
~~~~~~~~~~~~~~~~~~~

For applications, consider using configuration files:

.. code-block:: python

   import json
   from veedb import VNDB

   # config.json
   # {
   #     "vndb_token": "your-token-here",
   #     "other_settings": "..."
   # }

   async def main():
       with open("config.json") as f:
           config = json.load(f)
       
       async with VNDB(api_token=config["vndb_token"]) as client:
           # Your code here
           pass

Authentication Verification
---------------------------

Always verify authentication before performing authenticated operations:

.. code-block:: python

   from veedb import VNDB
   from veedb.exceptions import AuthenticationError

   async def verify_auth():
       try:
           async with VNDB(api_token="your-token") as client:
               auth_info = await client.get_authinfo()
               print(f"✓ Authenticated as {auth_info.username}")
               print(f"✓ User ID: {auth_info.id}")
               print(f"✓ Permissions: {auth_info.permissions}")
               return True
               
       except AuthenticationError:
           print("✗ Authentication failed - check your token")
           return False

Authenticated Operations
------------------------

User Information
~~~~~~~~~~~~~~~~

.. code-block:: python

   async def get_user_info():
       async with VNDB(api_token="your-token") as client:
           auth_info = await client.get_authinfo()
           
           # Get user details
           user_query = QueryRequest(
               filters=["id", "=", auth_info.id],
               fields="username, lengthvotes, lengthvotes_sum"
           )
           
           user_response = await client.user.query(user_query)
           user = user_response.results[0]
           
           print(f"User: {user.username}")
           print(f"Length votes: {user.lengthvotes}")

User List Management
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from veedb import UlistUpdatePayload

   async def manage_user_lists():
       async with VNDB(api_token="your-token") as client:
           # Get user's VN list
           ulist_query = QueryRequest(
               filters=["uid", "=", auth_info.id],
               fields="id, vote, notes, vn{title}"
           )
           
           ulist_response = await client.ulist.query(ulist_query)
           
           # Add a VN to list
           payload = UlistUpdatePayload(
               id="v17",  # VN ID
               vote=85,   # Rating
               notes="Great visual novel!"
           )
           
           await client.ulist.update("v17", payload)
           
           # Remove from list
           await client.ulist.delete("v17")

Release List Management
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from veedb import RlistUpdatePayload

   async def manage_release_lists():
       async with VNDB(api_token="your-token") as client:
           # Add release to list
           payload = RlistUpdatePayload(
               id="r123",
               status="finished"
           )
           
           await client.rlist.update("r123", payload)

Error Handling
--------------

Handle authentication-related errors appropriately:

.. code-block:: python

   from veedb.exceptions import (
       AuthenticationError,
       InvalidRequestError,
       RateLimitError
   )

   async def robust_auth_example():
       try:
           async with VNDB(api_token="your-token") as client:
               auth_info = await client.get_authinfo()
               
               # Perform authenticated operations
               await perform_list_operations(client)
               
       except AuthenticationError:
           print("Authentication failed:")
           print("- Check if your token is valid")
           print("- Verify token permissions")
           print("- Generate a new token if needed")
           
       except InvalidRequestError as e:
           print(f"Invalid request: {e}")
           print("- Check your filter syntax")
           print("- Verify field names")
           
       except RateLimitError:
           print("Rate limit exceeded - wait before retrying")

Token Security Best Practices
-----------------------------

1. **Environment Variables**: Always use environment variables for tokens in production
2. **Minimal Permissions**: Request only the permissions your application needs
3. **Token Rotation**: Regularly rotate your API tokens
4. **Secure Storage**: Never commit tokens to version control
5. **Error Handling**: Handle authentication errors gracefully
6. **Logging**: Avoid logging tokens in application logs

Example: Secure Token Management
--------------------------------

.. code-block:: python

   import os
   import logging
   from veedb import VNDB
   from veedb.exceptions import AuthenticationError

   # Configure logging (tokens should never appear in logs)
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   class VNDBClient:
       def __init__(self):
           self.token = os.environ.get("VNDB_API_TOKEN")
           if not self.token:
               raise ValueError("VNDB_API_TOKEN environment variable required")
       
       async def __aenter__(self):
           self.client = VNDB(api_token=self.token)
           await self.client.__aenter__()
           
           # Verify authentication
           try:
               auth_info = await self.client.get_authinfo()
               logger.info(f"Authenticated as user ID {auth_info.id}")
           except AuthenticationError:
               logger.error("Authentication failed")
               await self.client.__aexit__(None, None, None)
               raise
           
           return self.client
       
       async def __aexit__(self, exc_type, exc_val, exc_tb):
           return await self.client.__aexit__(exc_type, exc_val, exc_tb)

   # Usage
   async def main():
       try:
           async with VNDBClient() as client:
               # Your authenticated operations here
               stats = await client.get_stats()
               print(f"Connected to VNDB with {stats.vn} VNs")
               
       except ValueError as e:
           print(f"Configuration error: {e}")
       except AuthenticationError:
           print("Failed to authenticate with VNDB")

Troubleshooting
---------------

Common authentication issues and solutions:

**Token Not Working**
  - Verify the token is correctly copied
  - Check if the token has expired
  - Ensure you have the required permissions

**Permission Denied**
  - Your token may not have the required permissions
  - Generate a new token with appropriate permissions

**Rate Limiting**
  - VNDB has rate limits for authenticated requests
  - Implement proper retry logic with exponential backoff

**Environment Variable Issues**
  - Ensure the environment variable is set correctly
  - Restart your application after setting environment variables
