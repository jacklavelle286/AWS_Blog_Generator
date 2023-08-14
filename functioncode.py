import openai
import boto3
import os
import uuid

openai.apikey = os.getenv('OPENAI_API_KEY')
s3 = boto3.client('s3')

BUCKET_NAME = 'bucket-name'

def generate_content(prompt):

  response = openai.Completion.create(
    engine="text-davinci-003", 
    prompt=prompt,
    max_tokens=2000,
  )

  content = response.choices[0].text
  return content


def write_to_s3(content):

  object_key = f"blog_post_{uuid.uuid4()}.txt"  

  s3.put_object(  
    Bucket=BUCKET_NAME,
    Key=object_key, 
    Body=content
  )

  print(f"Blog post written to s3://{BUCKET_NAME}/{object_key}")


def lambda_handler(event, context):

  prompt = """
Compose a blog post of around 1800 words, designed for beginners, delving deep into a specific AWS service or feature. The article should follow the following structure and guidelines:

Introduction: Give readers a concise overview of the AWS service being discussed, emphasizing its significance and relevance to them.

High-level Overview: Shed light on how this AWS service functions, but maintain simplicity suitable for beginners.

Practical Examples: Showcase some frequent applications of this service, and provide a clear, step-by-step walkthrough on how newcomers can kick off their journey with this feature.

Insights and Best Practices: Offer valuable insights derived from hands-on experiences. Recommend best practices to optimize their utilization of the service.

Conclusion: Round up the discourse by recapping the primary advantages and takeaways of the service.

Style and Tone:

The piece should have an engaging flow, with seamless transitions from one section to the next.

The tone should be casual yet instructive, fostering an environment conducive to learning.

Emphasis on Practicality: Rather than just enumerating the features, elucidate on how readers can harness this service effectively for their specific requirements. Use the provided sample article as a benchmark for the desired structure, organization, and formatting.

Quality Assurance: The content produced should be of the utmost quality, without any abrupt interruptions, especially in mid-sentence. don't add anything like this- Proofread your work for spelling and grammatical errors before submission.

Citations and External References: Include links to external references wherever required. Make sure that all hyperlinks work.
and write the title at the top of the doc also. Make the post extremely thorough. """
  
  content = generate_content(prompt)
  
  write_to_s3(content)

  return {
    'statusCode': 200,
    'body': 'Post generated and saved to S3' 
  }
