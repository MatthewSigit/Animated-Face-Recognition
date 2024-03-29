from operator import not_
import os
import uuid
import ntpath
from PIL import Image 
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

# Credentials for connection string
# KEEP THIS PRIVATE!!! 
# account_name = ''
# account_key = ''
# container_name = ''
# connection_string = ''

# Create a blob service client
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Create a container client
container_client = blob_service_client.get_container_client(container_name)

blobs_list = container_client.list_blobs()
for blob in blobs_list:
    print("blob name: " + blob.name)
    sas_token = generate_blob_sas(account_name=account_name,
                                container_name= container_name,
                                blob_name=blob.name,
                                account_key=account_key,
                                permission=BlobSasPermissions(read=True),
                                expiry=datetime.utcnow() + timedelta(hours=1))
    sas_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob.name}?{sas_token}"

# Change local directory to the folder where the files are located
os.chdir(os.path.dirname(__file__))

def download_file(path):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=path)
    with open(file=path, mode="wb") as sample_blob:
        download_stream = blob_client.download_blob()
        sample_blob.write(download_stream.readall())

def upload_file(path, image=True):
     with open(path, "rb") as data:
        if (image):
            if (not path.endswith(".jpg")):
                print("Converting to jpg")
                not_jpg = Image.open(path)
                rbg_im = not_jpg.convert('RGB')
                rbg_im.save("tmp" + ".jpg")
                data = open("tmp.jpg", "rb")
            path = uuid.uuid4().hex + ".jpg"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=path)
        blob_client.upload_blob(data, overwrite=True)
        return path

def delete_file(path):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=path)
    blob_client.delete_blob()

# Uploading Files
# upload_file("test.txt", False)
# upload_file("dogg.png")
# upload_file("monke.jpg")

# Downloading Files
# download_file("187881f509814a3a8e7c7cb01855786b.jpg")
# download_file("91141eca2c2541b19243ee2b43e99632.jpg")