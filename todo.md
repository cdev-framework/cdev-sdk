# Technical Todos

This is a running list of tasks that need to be done on the project.



### Large
- Add remote backends to allow more than local json state. (Maybe S3 and dynamodb)


### Medium
- Improve and document the functionality of the `run` command and the underlying system 
- Add more options for the stream functionality for the data sync tool
- Create the first tutorial on the website


### Small
- Add implementations of the sync functionality for different resources
- Add support for Global Secondary Indexes for dynamodb
- Add support for simple Websockets on API Gateway
- Fix `cdev output` command because it can render some values as emoji that are not emojis (ex. arn of secret has :secret: in it)


### Bugs
- If the lambda function annotation is split into two lines the parser incorrectly adds the second line cause the function to most likely be in an unusable state.


