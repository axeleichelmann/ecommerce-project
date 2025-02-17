# start from node.js base image
FROM node:18-alpine

# Create working directory & copy frontend contents into it
WORKDIR /app

# Copy app contents
COPY ./ /app/

# install npm packages
RUN npm install
RUN npm install axios

CMD ["npm", "run", "dev", "--", "--host"]