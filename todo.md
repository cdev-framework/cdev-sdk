# Technical Todos

This is a running list of tasks that need to be done on the project before the alpha is complete.


### Large
- Add remote backends to allow more than local json state. (Maybe S3 and dynamodb)
- Transition the backend to use the Cloud Control API 
- Auto generation tool for resources on the Cloud Control API
- Refactor the system to add `modifiers` and `validators` api and flow into commands


### Medium
- Add support for some user authentication. Most likely use AWS Cognito
- Add support for simple Websockets on API Gateway
- Create the first tutorial on the website
- Complete the reference system
- Add all commands to CLI
- Make custom types for relative paths to improve DX of working with paths.


### Small
- Fix storing and deleting roles associated with lambdas
- Add demo project that demonstrates how to use 3rd party integrations
- Add Event support for Lambda events from all support resources
- Add implementations of the sync functionality for different resources
- Add support for Global Secondary Indexes for dynamodb
- Add more options for the stream functionality for the data sync tool
- Fix `cdev output` command because it can render some values as emoji that are not emojis (ex. arn of secret has :secret: in it)


### Bugs
- If the lambda function annotation is split into two lines the parser incorrectly adds the second line cause the function to most likely be in an unusable state.
- Check on the `run` command

