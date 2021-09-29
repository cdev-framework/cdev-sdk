# Todo

This is a running list of tasks that need to be done on the project.



### Large
- Add automated testing (investigate placebo for capturing aws calls) and exception handling
- Add transaction system for making deployments so that is the program is cancelled in the middle of a deployment that state is not in a messed up place. This also applies to multistage deployments that have an error in one of the steps.
- 


### Medium
- Improve and document the functionality of the `run` command and the underlying system 
- Add more options for the stream functionality for the data sync tool


### Small
- Add implementations of the sync functionality for different resources



### Bugs
- If the lambda function annotation is split into two lines the parser incorrectly adds the second line cause the function to most likely be in an unusable state.