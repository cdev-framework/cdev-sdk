# Cdev - Serverless Development Framework

Cdev provides a development environment and framework that allows python developers to easily create and deploy Serverless Applications on Amazon Web Services. By providing features like automated dependency management, isolated deployment environments, and function artifact optimizations, Cdev allows developers to focus on the development of their project then deploy an optimized version of their project onto Aws with a single command.

[![](https://cdevframework.io/images/github_banner.png)](https://cdevframework.io)


[Website](https://cdevframework.io/) • [Docs](https://cdevframework.io/docs/)


## Getting Started
- [An Aws account and credentials](https://aws.amazon.com/)
- [Requires Python>=3.6 and pip](https://cdevframework.io/docs/gettingstarted/python/)
- it is **highly** encourage to use a python virtual environment

Starting from an empty directory. Set up your python virtual environment and install the Cdev cli.
```
$ python -m venv .venv

$ . ./.venv/bin/activate

$ pip install cdev

$ cdev
```

### Create a new project
When creating a new project, you will be prompted about your Aws credentials and to link to a `S3 Bucket` for your deployment artifacts to be stored in.
```
$ cdev init demo-project --template quick-start
**Aws Credentials and S3 Bucket Selection Wizard**
```

### View the resources that will be deployed
```
$ cdev plan
```

### Deploy the resources
```
$ cdev deploy
```

### Invoke the deployed function directly from the cli
```
$ cdev run function.execute hello_world_comp.hello_world_function
```

### View the logs of the function
You might have to wait a few seconds for the logs to process in the cloud
```
$ cdev run function.logs hello_world_comp.hello_world_function
```

### Invoke the function from the deployed HTTP endpoint
Invoke the deployed function via the created HTTP Api
```
$ cdev output hello_world_comp.api.demoapi.endpoint
<url>
```

```
$ curl <url>/hello_world
```

You can also visit `<url>/hello_world` in your favorite web browser!


### Delete the Resources in the Environment
```
$ cdev destroy
```

For a more in depth information and examples about the capabilities of Cdev, check out our [documentation](https://cdevframework.io/docs/).


## Features
- [Serverless Function Parsing](https://cdevframework.io/docs/firstprinciples/serverless_optimizations/#serverless-function-parsing)
- [Automated and Optimized Dependency Management](https://cdevframework.io/docs/firstprinciples/serverless_optimizations/#automated-dependency-management)
- [Light-weight isolated environments](https://cdevframework.io/docs/firstprinciples/project_management/#environments)


## Supported Resources
- Serverless Function
- HTTP Endpoint
- S3 Bucket
- Dynamodb
- Aurora DB (Mysql and Postgres)
- Sqs
- Sns
- Hosted Static Website (Aws Cloudfront)

For guides on how to deploy any of these resources, check out our [documentation](https://cdevframework.io/docs/resources)

## Alpha Notes and Limitations
The project is still in an `alpha` state, so there are still rough edges and limitations. The following are the current high level limitations of the framework.

- Recovery from Failed Deployments
    - Certain resources require multiple API calls to generate the proper configurations in the Cloud, and if one of the API calls fails, it can cause the Cloud resource to be in a state that needs to be manually updated before continuing the deployment.

- Parallel Deployments
    - Non-dependant resources can be deployed in parallel to reduce the total deployment time when there are many changes in a single deployment.

- Remote Backend
    - The current state of cloud resources are stored in json files. This is extremely limiting as it prevents multiple people from working on the same state at the same time.

- Limited Resources and Options on Resources
    - We are starting by focusing on a set of resource that we feel provide value while not being too complex. We have plans to add more resource and customization as time goes on.

- Codebase improvements
    - Improvements in unit test coverage, logging, and error handling/messaging.

All of the current limitations can be navigated to use Cdev effectively for projects and solutions are being worked on to over come the documented limitations. Any issues that arise while using Cdev can be raised to daniel@cdevframework.com and will be addressed.
