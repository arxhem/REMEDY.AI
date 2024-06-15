`az login`
`az acr list`
Create an container registery --> remedyAIBackend
`az acr login -n remedyAIBackend`

Checking the Docker image name and tag:
`docker image ls`
And now tagging it again based on ACR for ex: `remedyaibackend.azurecr.io`
`docker tag remedyai-server:latest remedyaibackend.azurecr.io/remedyai-server:v1`

Pushing the image to ACR:
`docker push remedyaibackend.azurecr.io/remedyai-server:v1`

Then setting up the webApp by adding API keys for authentication and finally testing the application at:
<a>https://remedy-ai-backend-v1.azurewebsites.net/docs</a> 