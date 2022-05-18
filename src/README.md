# Cdev - Serverless Development Framework

The Cdev framework is designed to create a development environment that allows teams to harness the benefits of Serverless development by providing high level constructs and processes to reduce the friction of transitioning to Serverless development. By being built on a custom Infrastructure as Code framework, Cdev provides unique optimizations and flexibility that allows projects to start fast and scale naturally.

[![](https://cdevframework.io/images/github_banner.png)](https://cdevframework.io)


[Website](https://cdevframework.io/) • [Docs](https://cdevframework.io/docs/) • [Slack](https://slack.com/)


## Features
- [Serverless Function Parsing](https://cdevframework.io/docs/)
- [Optimized Dependency Management](https://cdevframework.io/docs/)
- [Custom Infrastructure as Code Framework](/src/core)
- [Designed to feel as close as possible to writing regular Python](https://cdevframework.io/docs/)
- [Extensible Plugin and Custom Functionality Capabilities](https://cdevframework.io/docs/)

## Getting Started
- [An Aws account and credentials](https://aws.amazon.com/)
    - Should have the `aws cli` and then run `aws configure` to set your credenentials.
- Requires Python>=3.6 and pip
- **Highly** encourage using a python virtual environment

Starting from an empty directory. Set up your python virtual environment and install the Cdev cli.
```
$ python -m virtualenv .venv

$ . ./.venv/bin/activate

$ pip install cdev
```

Create a new project, see the resources in the created project, and create the project
```
$ cdev

$ cdev init demo-project --template quick-start

$ cdev plan

$ cdev deploy
```

Invoke the deployed function directly from the cli
```
$ cdev run function.execute hello_world_comp.hello_world_function
```

You might have to wait a sec for the logs to process in the cloud
```
$ cdev run function.logs hello_world_comp.hello_world_function
```

Invoke the deployed function via the created HTTP Api
```
$ cdev output hello_world_comp.api.demoapi.endpoint
<url>
```

```
$ curl <url>/hello_world
```

You can also visit `<url>/hello_world` in your favorite web browser!

Delete the Resources in the Environment
```
$ cdev destroy
```

For a more in depth information about the capabilities of Cdev, check out our [documentation](https://staging.cdevframework.io/docs/).


## Supported Resources
- Serverless Functions
- HTTP Endpoints
- S3 Buckets
- Dynamodb
- Aurora DB (Mysql and Postgres)
- Sqs
- Sns
- Static Site Hosting

For guides on how to deploy any of these resources, check out our [documentation](https://cdevframework.io/docs/)

## Early Alpha Notes
The project is still in a pre-alpha state, so not all the features of the alpha are implemented. The main branch will be the most stable branch and should not have any breaking changes as work on the alpha continues. The alpha will be ready for a public launch by March 1st. Things left to do in alpha:
- More unit and integration tests
- General polish of output
- General work on documentation

For testing parts of the early alpha, it helps to start from the `resources-test` project template as that will have a bunch of preconfigured resources.
```
$ cdev init demo --template resources-test
```

## Post Alpha Road Map and Limitations
We are currently in the **very very** early stage of creating a comprehensive framework that helps teams throughout the whole cloud development process. As with any tool, it is important to understand what it is capabale and **not** capable of doing. Here are a list of outstanding things that we are working (or thinking) on.

- Remote Backend
    - The current state of cloud resources are stored in json files. This is extremely limiting as it prevents multiple people from working on the same state at the same time. We are working on creating a DB that can used as a remote backend that will allow teams to collaborate more effectively.

- Limited Resources and Options on Resources
    - We are starting by focusing on a set of resource that we feel provide value while not being too complex. We have plans to add more resource and customization as time goes on. [Our custom Infrastructure as Code framework](/src/core) provides the flexibility to deploy any resource on any cloud, but we have to put in work to generate the configurations to talk to different clouds. In the future, we hope to support a large number of Aws and non Aws resources through standardized cloud API's like the [Aws Cloud Control API](https://aws.amazon.com/cloudcontrolapi/).

- The Framework is Python Only
    - We started out with building the sdk in python first because that is the language we know best. We want the sdk to feel natural in whatever language is being used, which will require adding expertise to our team from other ecosystems. The underlying primitives that make up the framework are language agnostic, so we hope to one day support a wide range of languages.

- Can I export my project to an industry standard tool like Aws Cloudformation or Terraform?
    - We understand the benefits that come from avoiding lock-in by providing the ability to interpolate with the industry standard tools. We currently provision all resources with our custom [Infrastructure as Code Framework](/src/core) and store the state of the resources in local json files, which makes created projects not compatible with other tools. We felt that with building our own framework, we could explore new optimizations and ideas that could improve the developer experience. With some work, it is possible to make our framework work with and compatible with other Infrastructure as Code Frameworks, and we will be investigating this work as we move forward.


If you are interested in any of the challenges that we are working on or have expertise you think is missing in our project, please consider [applying for a job on our team](https://cdevframework.io/docs/).
