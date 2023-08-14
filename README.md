# AWS Daily Blog Post Generator

## Description

The AWS Blog Generator is an automated solution that leverages the power of OpenAI's GPT-3 model to create insightful and relevant blog posts about AWS services and features. Designed to simplify content creation, this solution integrates AWS Lambda with OpenAI's API, allowing for on-demand generation of blog content.

Upon invocation, the Lambda function sends a predefined prompt to OpenAI's GPT-3 engine. This prompt instructs the model to craft a blog post tailored for beginners, focusing on a specific AWS service or feature. The generated content is structured with an introduction, a high-level overview, practical examples, insights, best practices, and a conclusion. The tone is set to be engaging, casual, yet instructive, ensuring readers find value in every piece.

Once the content is generated, the solution saves the blog post to an Amazon S3 bucket, providing a centralized storage solution and easy retrieval for future use.

This AWS Blog Generator is not just a testament to the capabilities of AI in content creation but also showcases the seamless integration possibilities between cloud services and AI platforms. Whether you're an AWS enthusiast, a content creator, or someone looking to automate parts of their content strategy, this solution offers a glimpse into the future of automated content generation.

These instructions are written to use the AWS CLI exclusively, so you either need this installed on your local machine, or if you want to use the exact same commands as me, use [AWS CloudShell.](https://aws.amazon.com/cloudshell/)

## Items in this repository

These items are stored within this repository, you will have to download it to your local machine and unzip them, and run this lab in the same directory (I designed this specifically to use AWS CloudShell but any CLI environment will work.)

1. OpenAi API Key saved in a text file called openaicreds.txt (you will have to retrieve your own one and store it in this file)

2. Openai layer in lambda, the ARN within a text file called layerarn.txt (you can choose to either keep this or use your own Lambda Layer - this runtime is specified for Python3.7)

3. The code file written in Python (functioncode.py)

4. Lambda trust policy (trust-policy.json)


#### 1. Create S3 bucket and edit your Python code (you will need a globally unique bucket name)

  ```bash
  BUCKET_NAME=my-blog-bucket
  ```

  ```bash
  aws s3 mb s3://$BUCKET_NAME
  ```

#### 2. Edit the functioncode.py, replacing the placeholder with your new bucket name using the sed command

  ```bash
  sed -i "s/bucket-name/$(echo $BUCKET_NAME)/g" functioncode.py
  ```

#### 2.5 Check that this has worked - you should see your bucket name in the code file on line 9

  ```bash
  cat functioncode.py
  ```

#### 3. Zip it up for use with our Lambda Function later

  ```bash
  zip function.zip functioncode.py
  ```

#### 4. Also, replace the bucket name within your IAM permissions policy using the sed command

  ```bash
  sed -i "s/bucket-name/$(echo $BUCKET_NAME)/g" access-policy.json
  ```

#### 4.5 Check that this has worked - you should see your bucket name reflected in the resource field in the policy

  ```bash
  cat access-policy.json
  ```

#### 5. Create the IAM role

  ```bash
  ROLE_ARN=$(aws iam create-role --role-name LambdaRole --assume-role-policy-document file://trust-policy.json --query 'Role.Arn' --output text)
  ```

#### 6. Create the IAM policy

  ```bash
  aws iam put-role-policy --role-name LambdaRole --policy-name LambdaPolicy --policy-document file://access-policy.json
  ```

#### 7. Create function using layer ARN and your openai key

  ```bash
  OPENAI_KEY=$(cat open_ai_creds.txt)
  ```

  ```bash
  LAYER_ARN=$(cat layerarn.txt)
  ```

  ```bash
  LAMBDA_ARN=$(aws lambda create-function --function-name BlogFunction --zip-file fileb://function.zip --role $ROLE_ARN --layers $LAYER_ARN --runtime python3.7 --handler functioncode.lambda_handler --environment "Variables={OPENAI_API_KEY=$OPENAI_KEY}" --timeout 180 --query 'FunctionArn' --output text)
  ```

#### 8. Test the function and read our first blog post!

  ```bash
  aws lambda invoke --function-name BlogFunction --payload '{}' response.json && cat response.json
  ```

  ```bash
  aws s3api list-objects --bucket $BUCKET_NAME
  ```

  ```bash
  OBJECT_NAME=$(aws s3api list-objects --bucket $BUCKET_NAME --query 'Contents[0].Key' --output text)
  ```

  ```bash
  aws s3api get-object --bucket $BUCKET_NAME --key $OBJECT_NAME blog.txt
  ```

#### 9. Add daily trigger using Amazon EventBridge (Optional)

  ```bash
  RULE_ARN=$(aws events put-rule --name daily-9am --schedule-expression "cron(0 8 * * ? *)" --query 'RuleArn' --output text)
  ```

  ```bash
  aws lambda add-permission --function-name BlogFunction --statement-id "EventbridgeInvokeRule" --action 'lambda:InvokeFunction' --principal events.amazonaws.com --source-arn $RULE_ARN
  ```

  ```bash
  aws events put-targets --rule daily-9am --targets Id=1,Arn=$LAMBDA_ARN
  ```

#### Feel free to reach out at lavellej286@gmail.com if you have any questions, and feel free to submit pull requests. 
