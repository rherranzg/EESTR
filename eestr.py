#!/usr/bin/python
import boto3
from datetime import datetime

ec2 = boto3.client('ec2')

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

	for tag in instance.tags:
		if tag not in volume.tags:
			#print "Tag " + str(tag) + " NOT in " + str(volume.tags)
			return False

def check_snap_tags(volume, snapshot):
	'''Check if the given snapshot has the proper tags'''
	try:

		print ">>> Checkeo vol tags y snap tags"
		print volume.tags
		print snapshot.tags

		if not volume.tags:
			#print ">>> check_snap_tags: volumen sin tags"
			return True
		if volume.tags and not snapshot.tags:
			#print ">>> check_snap_tags: snap sin tags"
			return False

		for tag in snapshot.tags:
			if tag not in snapshot.tags:
				#print ">>> check_snap_tags: tag not in volume"
				return False

	except Exception as e:
		print e

def apply_tags(instance, volume):
	'''If instance and volume tags dont match, propagate them'''

	vol_tags = volume.tags
	for tag in instance.tags:

		# Si no hay vol_tags, creo una lista vacia
		if not vol_tags:
			vol_tags = []

		# Si el tag no esta en la lista de tags...
		if tag not in vol_tags and not tag['Key'].startswith("aws:"):
			
			print "Applying tag " + str(tag) + " to volume " + volume.id 

			vol_tags.append(tag)
			volume.create_tags(DryRun=False, Tags=vol_tags)


def get_proper_instances(ec2_session):
	'''Get instances in our project'''
	
	inst = []

	for instance in ec2_session.instances.all():
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

def apply_tags_to_snaps(volumes):
	'''Apply tags to snaps which corresponds to a given list of volumes'''

	print "> Snaps"

	ec2_resource = boto3.resource('ec2')

	for volume in volumes:
		if volume.snapshot_id:
			
			try:


				snap = ec2_resource.Snapshot(volume.snapshot_id)
				
				#print ">> Snap {}".format(volume.snapshot_id)
				#print ">> {}".format(volume.tags)

				check_snap_tags(volume, snap):

			except Exception as e:
				
				print ">>> Snap {} doesnt exist".format(volume.snapshot_id)

def eestr(ec2_session):
	'''Get instances on my own. Get Volumes and apply tags. Get Snaps and apply tags'''

	instances = get_proper_instances(ec2_session)

	volumes = apply_tags_to_volumes(instances)

	#apply_tags_to_snaps(volumes)


def lambda_handler(event, context):

	print('Starting function at {}'.format(str(datetime.now())))

	# start connectivity
	s = boto3.Session()
	ec2_session = s.resource('ec2')

	try:
		if eestr(ec2_session):
			print "Success!"

	except Exception as e:
		print e
		print('Check failed!')
		raise
	finally:
		print('Check complete at {}'.format(str(datetime.now())))
		return "OK"

if __name__ == "__main__":
	lambda_handler(None, None)