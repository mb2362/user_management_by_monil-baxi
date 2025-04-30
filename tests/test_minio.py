from unittest.mock import patch, MagicMock
from minio import Minio
import os
from urllib3 import HTTPConnectionPool  # Add this import

@patch("minio.Minio")  # Patch the Minio class itself
@patch.object(HTTPConnectionPool, 'urlopen', return_value=None)  # Mock urllib3's urlopen method
def test_minio_bucket_exists(mock_urlopen, mock_minio_class):
    # Create a mock instance of the Minio client
    mock_client = MagicMock()

    # Mock the bucket_exists method to always return True
    mock_client.bucket_exists.return_value = True

    # Mock the urlopen method to return a mock response
    mock_response = MagicMock()
    
    # Set up the mock response with the correct attributes
    mock_response.status = 200  # Simulate a successful response
    mock_response.headers.get.return_value = "application/xml"  # Correct content type
    mock_response.data.decode.return_value = "<Response><Status>OK</Status></Response>"  # Simulate XML body
    
    # Return the mock response when urlopen is called
    mock_urlopen.return_value = mock_response

    # Assign the mock instance to the Minio class constructor
    mock_minio_class.return_value = mock_client

    # Instantiate the Minio client (it will use the mocked version)
    client = Minio(
        "localhost:9000",  # This is still set to localhost but the request will be mocked
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        secure=False
    )

    bucket_name = os.getenv("MINIO_BUCKET_NAME", "user-profile-pictures")

    # Fix the get_redirect_location method to return None (not a MagicMock)
    mock_response.get_redirect_location.return_value = None
    
    # Call the method to check if the bucket exists (this will use the mock)
    found = client.bucket_exists(bucket_name)
    
    # Add assertion here if needed
    assert found is True  # Expected to be True based on the mock
