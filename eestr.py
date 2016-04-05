#!/usr/bin/python
import boto3
from datetime import datetime

def is_my_instance(instance):
	'''Function to filter instances'''
	
	startswith = "HBG.CDR"

	if instance.tags:
		for tag in instance.tags:
			if tag["Key"] == "Name" and tag["Value"].startswith(startswith):
				return True

def check_volume_tags(instance, volume):
	'''Check if instance tags are present in volume tags'''
	
	if not instance.tags:
		return True
	if instance.tags and not volume.tags:
		return False

	vol_tags = volume.tags

	for tag in instance.tags:
		if tag not in vol_tags:
			#print "Tag " + str(tag) + " NOT in " + str(vol_tags)
			return False

def check_snap_tags(volume, snapshot):
	'''Check if the given snapshot has the proper tags'''

	if not volume.tags:
		return True
	if volume.tags and not snapshot.tags:
		return False

	snap_tags = snapshot.tags

	for tag in volume.tags:
		if tag not in snap_tags:
			return False

def apply_tags(instance, volume):
	'''If instance and volume tags dont match, propagate them'''

	vol_tags = volume.tags
	for tag in instance.tags:

		# Si no hay vol_tags, creo una lista vacia
		if not vol_tags:
			vol_tags = []

		# Si el tag no esta en la lista de tags...
		if tag not in vol_tags and not tag['Key'].startswith("aws:"):
			
			print "Aplico el tag " + str(tag) + " al volumen " + volume.id 

			vol_tags.append(tag)
			volume.create_tags(DryRun=False, Tags=vol_tags)


def get_proper_instances(ec2):
	'''Get instances in our project'''
	
	inst = []

	for instance in ec2.instances.all():
		if is_my_instance(instance):
			inst.append(instance)

	return inst

def apply_tags_to_volumes(instances):
	'''This tag applies tag to untagged volumes. Also return the list of volumes for the given instances'''


	vols = []

	for instance in instances:
		#print instance.id
		for volume in instance.volumes.all():
			#print volume.id
			
			vols.append(volume)
			if not check_volume_tags(instance, volume):
				apply_tags(instance, volume)
	return vols

def apply_tags_to_snaps(volumes, ec2):
	'''Apply tags to snaps which corresponds to a given list of volumes'''

	print "snaps"

	for volume in volumes:
		if volume.snapshot_id:
			if check_snap_tags(volume, ec2.Snapshot(volume.snapshot_id)):
				print "snapshot " + snapshot_id + " bien tagged"
			else:
				print "snapshot " + snapshot_id + " mal tagged"


def eestr(ec2):
	'''Get instances on my own. Get Volumes and apply tags. Get Snaps and apply tags'''

	instances = get_proper_instances(ec2)

	volumes = apply_tags_to_volumes(instances)

	apply_tags_to_snaps(volumes, ec2)


def lambda_handler(event, context):

	print('Starting function at {}'.format(str(datetime.now())))
	
	# start connectivity
	s = boto3.Session()
	ec2 = s.resource('ec2')

	try:
		if eestr(ec2):
			print "Success!"

	except Exception as e:
		print e
		print('Check failed!')
		raise
	finally:
		print('Check complete at {}'.format(str(datetime.now())))
		return "OK"