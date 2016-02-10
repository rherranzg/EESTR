#!/usr/bin/python
import boto3
from datetime import datetime

def get_instance_from_volume(ec2, volume):
	'''Get instance for this volume'''

	if volume.attachments:
		id = volume.attachments[0]["InstanceId"] 
		if id:
			return ec2.Instance(id)

	return None

def is_my_instance(instance):
	'''Function to filter instances'''
	startswith = "HBG.CDR"

	for tag in instance.tags:
		if tag["Key"] == "Name" and tag["Value"].startswith(startswith):
			return True

def volume_tagged(instance, volume):
	'''Check if instance tags are present in volume tags'''
	
	if not instance.tags:
		return True
	if instance.tags and not volume.tags:
		return True

	vol_tags = volume.tags

	for tag in instance.tags:
		if tag not in vol_tags:
			#print "Tag " + str(tag) + " NOT in " + str(vol_tags)
			return False

def apply_tags(instance, volume):
	vol_tags = volume.tags
	for tag in instance.tags:
		if tag not in vol_tags:
			print "Aplico el tag " + str(tag) + " al volumen " + volume.id
			volume.create_tags(DryRun=True, Tags=vol_tags)



def eestr(ec2):

	# List volumes
	for volume in ec2.volumes.all():
		
		# Get instance for this volume
		instance = get_instance_from_volume(ec2, volume)
		
		# If the volume has an instance attached...
		if instance:
			#print "El volumen " + volume.id + " esta attachado a la instancia " + instance.id
			# This check is optional
			if is_my_instance(instance) and not volume_tagged(instance, volume):
					apply_tags(instance, volume)

# start connectivity
s = boto3.Session()
ec2 = s.resource('ec2')

try:
	if eestr(ec2):
		print "Success!"

except:
	print('Check failed!')
	raise
finally:
	print('Check complete at {}'.format(str(datetime.now())))
	#return "OK"
