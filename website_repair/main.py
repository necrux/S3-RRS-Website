import datetime
import boto3
import json
import mimetypes

def date_initialization(days_expiry):
  # Function to convert 'Expires' from days to ISO8601 format.
  now = datetime.datetime.now()
  expires = now + datetime.timedelta(days=days_expiry)
  expires = expires.isoformat()
  return (expires)

def sns_send(variables, message, error):
  # Function to send error messages to SNS.
  client = boto3.client('sns')
  Message="Error encountered with the following sync: \n\n%s \n\nError: \n\n%s" % (message.body, error)
  client.publish(
    TopicArn=variables['sns_arn'],
    Subject=variables['sns_subject'],
    Message=Message
  )

def content_type(filename):
  # Function to determine the MIME type for selected file.
  mime_type = mimetypes.guess_type(filename)[0]
  return (mime_type)

def sqs_processing(variables):
  # Function to read and process the selected SQS queue.
  s3 = boto3.resource('s3')
  sqs = boto3.resource('sqs')
  queue = sqs.get_queue_by_name(QueueName=variables['my_queue'])
  
  while (int(queue.attributes['ApproximateNumberOfMessages']) > 0):
    for message in queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=5):
      jmessage = json.loads(message.body)
      try: 
        key = jmessage['Records'][0]['s3']['object']['key']
        mime_type = content_type(variables['path']+key)
        if mime_type is None:
          # Let the queue know that the message is processed
          message.delete()
          sns_send(variables, message, "File type is None.")
          break
        metadata = variables['metadata']
        metadata['ContentType'] = mime_type
        s3.Object(variables['my_bucket'], key).upload_file(variables['path']+key, ExtraArgs=variables['metadata'])
        # Let the queue know that the message is processed
        message.delete()
      except (IOError, OSError) as error:
        # Let the queue know that the message is processed
        message.delete()
        sns_send(variables, message, error)
