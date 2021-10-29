# Technical Todos

This is a running list of tasks that need to be done on the project.



### Large
- Add automated testing (investigate placebo for capturing aws calls) and exception handling
- Add transaction system for making deployments so that is the program is cancelled in the middle of a deployment that state is not in a messed up place. This also applies to multistage deployments that have an error in one of the steps.
- Add remote backends to allow more than local json state. (Maybe S3 and dynamodb)


### Medium
- Improve and document the functionality of the `run` command and the underlying system 
- Add more options for the stream functionality for the data sync tool
- Work on README 
- Create the first tutorial on the website
- Package dependencies with Lambda Functions 


### Small
- Add implementations of the sync functionality for different resources
- Add support for Global Secondary Indexes for dynamodb
- Add support for simple Websockets on API Gateway
- Fix `cdev output` command because it can render some values as emoji that are not emojis (ex. arn of secret has :secret: in it)


### Bugs
- If the lambda function annotation is split into two lines the parser incorrectly adds the second line cause the function to most likely be in an unusable state.
- Look init project init because intermediate folder might not be created. Add better check for file system state.
- Add project and a salt to creating the env hash so that projects don't have resource collisions on aws. 


### Nice to haves
- Make a runtime library for aws aurora that is compatible with the [python db interface](https://www.python.org/dev/peps/pep-0249/) (Large task)
