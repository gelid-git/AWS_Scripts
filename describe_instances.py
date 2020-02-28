from __future__ import print_function
import boto3
import csv
from datetime import datetime

def get_ec2(ec2_client):
	global csv_rows
	response = ec2_client.describe_regions()
	for region in response['Regions']:
		curr_region = region['RegionName']
		print("Checking the " + curr_region + " region.", end="")
		client_per_region = boto3.client('ec2',region_name=curr_region)
		instance_response = client_per_region.describe_instances()
		if len(instance_response['Reservations']) > 0:	
			print(" " + str(len(instance_response['Reservations'])) + " instance(s) discovered.")
			for reservation in instance_response['Reservations']:
				for instance in reservation['Instances']:
					instance_id = instance['InstanceId']
					state = instance['State']['Name']
					image_id = instance['ImageId']
					ami_name = get_ami_name(client_per_region, image_id)
					instance_name = 'No Name Tag'
					try:
						for tag in instance['Tags']:
							if tag['Key'].lower() == 'name':
								instance_name = tag['Value']
					except:
						pass	
					
					ec2_row = [curr_region, instance_name, instance_id, state, ami_name]
					csv_rows.append(ec2_row)
		else:
			print(" No instances found.")
#### end get ec2 fun

def get_ami_name(ec2_client, amiid):
	image_name = ''
	image_response = ec2_client.describe_images(
		ImageIds=[amiid]
	)
	
	for image in image_response['Images']:
		image_name = image['Name']

	return image_name
#### end get ami name fun

curr_date = datetime.now()
timestamp = curr_date.strftime("%Y_%m_%d_%H-%M-%S")

csv_rows = []
header_row = ["Region", "InstanceName", "InstanceId", "InstanceState", "AmiName"]
csv_rows.append(header_row)

'''
#boto3.setup_default_session(profile_name='profile_name')  ###If using different accounts based on profile names.


#if you want to hard code your keys or not use aws configure/credentials file.
ec2 = boto3.client(
	'ec2',
	aws_access_key_id = 'Access_key',
	aws_secret_access_key = 'Secret_key',
	#aws_sesssion_token = 'Session_token'    ###For when using a role instead of a user account.  
)
'''

ec2_client = boto3.client('ec2')
get_ec2(ec2_client)

	
filename = 'ec2_instance_' + str(timestamp) + '.csv'

with open(filename, 'wb') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(csv_rows)
	
csv_file.close()
print("File " + filename + " created.")


