# start from node.js base image
FROM node:18-alpine

# Create working directory & copy frontend contents into it
WORKDIR /app

# Copy app contents
COPY ./ /app/

# install npm packages
RUN npm install
RUN npm install axios

EXPOSE 5173

CMD ["npm", "run", "dev"]