# Cdev Architecture



## High Level Deployment
1. The Frontend execution object finds the user defined Cdev_Project.py file in the called directory. This file is then imported as a module. When imported, the file must instantiate a Cdev_Project file obj and initialize `Cdev components`. Once confirmed instantiation, the `render` function is called. The `render` function will sequentially go through the components and render them. 

2. The rendering of all the `cdev components` in the `cdev_project` object will return a `rendered_project` object.

3. Initialize the backend by running the `cdev_backend.py` module (if provided) to make any updates to the backend needed by the user. The main step in initializing the backend is registering mappers. When a mapper registers with the backend it claims certain top level resource namespaces. These namespaces are used to determine which mapper will handle provisioning desired changes in the backend state. 

4. The backend receives the new desired project state from the frontend. It then creates a set of differences based on the hashes of the resources. This generate 3 types of objects:
- Creates -> desire to create a new resource
- Updates -> desire to update an already existing resource 
- Deletes -> desire to delete a resource

Note that these actions are from the point of view of just the backend state, and it has no knowledge of the underlying cloud resources. For example, an update to a deployed function can involve deleting the old version in the cloud and re-provisioning a new function. The Mappers handle determining how these diffs are actually implemented on the actual cloud provider. 

5. The diffs are handed to the different mappers based on the namespace registry and the resource's id. The mapper is completely responsible for interacting with a cloud provider to provision the needed resources. Note that the mapper should have an understanding of what it can/can't deploy and should throw errors if it is handed a resource it doesn't know how to deploy or a resource with ill-formed parameters. The mapper pulls in data from the cloud mapping state to determine what it needs to do. All communication from a provider to the cloud mapping happens through a provided API. 

6. The mapper makes calls to the Cloud provider API's to actually create the resources. It then updates the cloud mapping as resources are created/update/deleted. When a mapper has finished with all its changes, it calls the API to interact with the deployed remote state to update the deployed state. 


## Primitives


### Resources
This might be the most fundamental primitive because it is used by the frontend, backend, and mappers. Because the world of the Cloud providers and SaaS developer tools is exploding, I think it is really important to create a system that is flexible enough to add support for any kind of "serverless" resource. To accomplish this, I have kept the definition of a resource as light as I can. 