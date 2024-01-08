FROM node:latest

WORKDIR /my-app/

# folder source (and contents) and where it's going to go in the container
COPY my-app/public/ /my-app/public
COPY my-app/src/ /my-app/src
COPY my-app/package.json /my-app/
# Authen. so we can upload to the bucket
COPY secrets/gen_service_account.json /my-app/gen_service_account.json

# To push to GCS bucket
# RUN npm install @google-cloud/storage
# To work with react-boostrap while also having bootstrap styles natively
RUN npm install react-bootstrap
RUN npm install bootstrap
RUN npm install axios

# React apps run on port 3000
EXPOSE 3000

# General start the react app
CMD ["npm", "start"]