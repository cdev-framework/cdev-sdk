# File System Manager

This module does the heavy lifting for the `DefaultComponent` provided with cdev_core by default. The purpose of this component is to allow end users to define their desired infrastructure using high level languages like Python, but this comes at the cost of the architecture being highly coupled to the users filesystem set up. This module attempts to prevent coupling when possible, but there are some situations like handler packaging where it is impossible to completely decouple.




## Dependencies and Packaging

This is one the most important issues that cause friction when transitioning to serverless development because the constraints taken into account when creating language dependency systems are not the same constraints that exist for serverless platforms. The solution to this problem is highly dependant on the languages internal dependency system and whatever package manager is popular for that language. For Python, the main package manager is `pip`. To understand the solutions implemented in Cdev, it is important to have a solid understanding python modules and the standards that drive tools like `pip`. Below are some resources that you should familiar with when working on dependency and packaging. 
- [Python Modules](https://docs.python.org/3/tutorial/modules.html)



## Dependencies and Packaging Current Problems

Since all the popular languages were not built with the constraints of serverless in mind, they all have points of friction that need to be addressed. For Python, a good place to start finding points of friction is to looks at 'traditional' development workflows and point out some of the places that problems arise. 

### Requirements.txt 
Developers that have worked with python projects know to look for this file as the source of truth for the external dependencies that a project will need. This file contains a list of the external projects (and hopefully a specific version identifier) needed for the application to work, and these packages can be retrieved and made available to the application using a simple `pip install -r requirements`. When deploying the application, some workflows will package the downloaded files from the developers machine with the application, but others will simply include the `requirements.txt` files and have the deployment platform retrieve the dependencies. 

A simple mirroring of these workflows on a serverless deployment platform breakdowns because of two constraints of serverless development: **cold starts** and **total package size**. 

Aws' mechanism for defining external dependencies is Lambda Layers, which are essentially archives that will be loaded into the execution environment before your function is executed. On its own, Lambda Layers are a fairly static offering that requires developers to manually create the archives, but the current serverless development tools provide functionality to create these layers from `requirements.txt` files using a single command. Although you can create this archive as easy as previous development paradigms, there is still friction as a project grows in size.

Providing each function with a single layer that contains the entire projects set of dependencies can break down as the projects includes more dependencies. For example, the entire Aws Lambda execution environment has a [limit of 250 MB](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) including used layers. This means that if a projects dependencies exceed this limit, then no function would be able to use the project's layer regardless of if any individual function actually uses all the dependencies.

Although lots of projects will never reach this limit, it is a constraint that will weigh down larger scale projects because once this problem arises the developer must create manual processes to break up their dependencies. Cdev's solution will strive to make the process scale seamlessly up to the point of reaching hard limits, such as an individual function truly using more than 250MB, while maintaining a familiar developer experience. 

## Dependencies and Packaging Implementation Details
Cdev's solution to dependencies and packaging strives to provide a great developer experience by allowing projects to using familiar dependency structure while scaling seamlessly to the absolute limits of the deployment platform. One of the fundamental differentiators that underpins our solution is that the input to the process is the `parsed function` output from that `serverless parser`, which provides information about the exact external dependencies used by each specific handler. This allows us to understand at a granular level what dependencies are used by each handler without forcing a project to be structured with a single handler per file. 

**Note that the information is derived from the `serverless parser` which relies on the symbol tree representation of a handler. If you require dynamically loading modules at runtime bypassing an `import` statement, then we will not be able to extract all the needed information about the dependencies used.** 


The starting point for the process is the input of a handler and the top level modules that the handler directly uses. A handler like the one below  would result in the following modules being need: (imagine the actual function does some data transformation with pandas and then renders a report with it)
```
import pandas
import jinja2


def myhandler(event, context):
    print(pandas)
    print(jinja2)

```

top-level modules from parser:
- jinja2
- pandas


For each top level module, we need to find all the dependency of that top level module. Some types of modules can be excluded because they are from the standard library (os, sys, etc) or are provided by default in the serverless execution environment (boto3, etc). The modules that need to be parsed for dependencies can be broken into two categories: managed or user defined. 

- **Managed modules** are ones that come from projects that are installed using a package manager like `pip`. The dependencies of these modules are discovered using the metadata from the project. 
- **User defined modules** are ones that are created within the project. The dependencies of these modules are discovered by parsing the symbol tree of each file in the module. 

### Managed Modules


### Relative Imports 
Although serverless development platforms are designed to reduce the amount of cognitive overhead for developers, they can actually surface new problems that developers did not have to previously think about. One such problem, is that developers must now understand and account for how their project is structured. When working on a growing project, it is important to separate reusable code, and one of the best mechanism for isolating code in python is to create local modules. In 'traditional' development environments, the entire project is often bundled together, which preserves the folder structure for the relative modules. To create a familiar environment where developers can create relative modules, we must understand how the serverless platforms are executing our code. 


#### Aws Lambda Code Execution
When creating an Aws Lambda function, one of the most important fields that must be set is the 'handler', which specifies to the platform which function to execute. The 'handler' field is not set as a file path, but instead, as a python module definition. This means that if we have a folder structure such as:
```
src
|- handlers
|--- __init__.py
|--- api.py
|----- function1
|- myutils
|--- helper.py
|- __init__.py
```
The `handler` value would be `src.api.function1`

Since the handler value includes the parent package `src`, we will be able to reference the `myutils` package with a relative import from our handler.
```
from .. import myutils
```

When crating the final archive that contains our handler, it is important to package the `myutils` package correctly with regards to its position in the file system. 

On top of preserving the file system relationship between the local packages, we must ensure that any module defined in the local dependencies are packaged correctly too. This is a recursive process of tracing down the dependency tree of each local module that is included. 





### Managed Modules Packaging

Once we have computed the set of needed projects from pip, we have to make some decisions about how to create the layers that will contain the packages. Starting on one side of the spectrum, we could have a single layer per project and attach that to all functions, but we discussed the downsides of this in `current problems` section. The other side of the spectrum would be to create an individual layer archive for each function, but this quickly becomes a problem when you have many functions or heavy external dependencies (for example numpy) because you would have to upload a unique layer for each function, which is really slow if the dependencies are heavy and wasteful if the same dependency is uploaded multiple times. 

So what is the appropriate middle ground? Cdev packaging is based around each external dependency being deployed in its own layer. This allows the developer to only upload each dependency once and then quickly attach it to other functions without paying the raw upload cost. Unfortunately, this also has issues that must be overcome. 

[Aws has a hard limit](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) that each function can only have **five** layers attached to it. If a function has more than six external dependencies, we would not be able to simply reuse the layers that contain a simple dependency each. Also, we want to allow a user to define other layers that can contain data or binaries, so that limit of five can be less. Our solution is to come up with an algorithm that will determine the most appropriate external dependencies to come combine into a unique `composite layer` while reusing the most appropriate already available single dependency layers. 


#### External Dependency Index

Since this `composite layer` will most likely be unique to this function, we want to pick the `composite layer` that will result in the smallest upload time. (Note we will keep track of what composite layers have already been used in the project and default to an already made one to avoid uploading an artifact). The initial thought would be to simply choose the largest packages to deploy with existing single dependency layers that way our composite layer contains the remaining smaller packages, but this unfortunately does not actually provide the most optimal solution. 

To see how this initial strategy does not provide an optimal solution imagine a situation where we are only allowed to use two layers for the dependencies, but we have to package three external dependencies. This means that we are going to have one single dependency layer and one composite layer. Imagine the dependencies look like this:
- Project A (60 MB total) (10 MB individually) -> depends on Project Z (50 MB)
- Project B (55 MB total) (5 MB individually) -> depends on Project Z (50 MB)
- Project C (30 MB) (10 MB individually) -> depends on Project X (20 MB)

Since Project A and Project B share the same dependency that makes up most of both of their total size, it makes sense that Project A and Project B make up the composite layer. See the below table for computed values:


**Composite Layer Size** 
|   | A     | B     | C |
| - | -     | -     | - |
| A | -     | -     | - |
| B | 65 MB | -     | - |
| C | 40 MB | 35 MB | - |

Although this computing this table provides the insight into which packages the make a composite layer, it is both exponential in time and memory:

for n > d
n = number of external projects
d = number of layers available
q = Max((n - d) + 1, 4)


Memory = O(n^q)
Time = O(n^q)

Since this table is unique to a specific set of external packages, it makes sense to only only compute this for levels `q<4` initially and provide the option for the user to build the larger set of the index if desired, and if not default to the simpler algorithm of picking the largest package. 







