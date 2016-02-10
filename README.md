# Eestr

Eestr stands for Ec2 -> Ebs -> Snapshot Tag Replicator. 

## Purpose

EBS and Snapshots are usually not tagged when an EC2 instance are created. Eestr is a Lambda function which ensure EBSs and Snapshots are tagged with the same than its corresponding EC2 instance

## Permissions

By now, this function has been tested with Ec2FullAccess Managed Policy (don't kill me yet, plz!). More fine grained permissions will be added in a near future.
