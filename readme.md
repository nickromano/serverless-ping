# Serverless Ping

[![serverless](http://public.serverless.com/badges/v3.svg)](http://www.serverless.com)
[![Build Status](https://travis-ci.org/nickromano/serverless-ping.svg?branch=master)](https://travis-ci.org/nickromano/serverless-ping)
[![Coverage Status](https://coveralls.io/repos/github/nickromano/serverless-ping/badge.svg?branch=master&v2)](https://coveralls.io/github/nickromano/serverless-ping?branch=master)

Once a minute this lambda function will check to see if your endpoint is up.  If so it will send the response time to Cloudwatch.  A Cloudwatch alarm will then email you when the endpoint is down (`ALARM`) or if the lambda function stops working (`INSUFFICENT RESULTS`).

`Cloudwatch Event (1 minute)` > `AWS Lambda` > `Cloudwatch Data` > `Cloudwatch Alarm` > `SNS Topic` > `SNS Email Subscription`

Estimated Costs: **$0.05/month** *(not including free tier)* [source](https://s3.amazonaws.com/lambda-tools/pricing-calculator.html)

## Setup

Install the serverless commandline tools

```
npm install -g serverless
```

Deploy this service to AWS (swap out parameters for your needs)

```
serverless deploy \
	--ping-name=google \
	--ping-host=https://google.com \
	--ping-alarm-email=alertme@gmail.com
```

That's it! 🎉

### Cleanup

To remove all resources created run

```
serverless remove \
	--ping-name=google \
	--ping-host=https://google.com \
	--ping-alarm-email=alertme@gmail.com
```

### Additional Options

Alarm namespace - By default the cloudwatch data will be put under the `Serverless/Ping` namespace.  You can override it using `--ping-alarm-namespace`.

```
--ping-alarm-namespace=MyNamespace/Ping
```

Exception Monitoring - Any exceptions thrown in the lambda function will be logged to CloudWatch Logs.  If you would like them also sent to sentry add the DSN as another paramter to the `serverless deploy` command above.

```
--ping-sentry-dsn=https://*********:*******@sentry.io/*****
```

## Contributing

Installing dependencies.  Vendored dependencies are included in the git repo to make it easier for users to deploy this.

```
pip3 install -t vendored/ -r requirements.txt --upgrade
```
