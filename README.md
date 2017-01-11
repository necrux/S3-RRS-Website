# S3-RRS-Website
A solution for hosting a self-healing, static website using AWS' S3 storage with reduced redundancy.

This script will check a given SQS queue for RRS and deleted object events. If any are detected, it will re-upload the missing files from a given path.

If failures are detected, a message with the original message and error is sent to a specificed SNS ARN.

The script relies on usre provided input in the 'config' file, as well as AWS credentials located in ~/.aws/credentials.
