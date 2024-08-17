# Stage 1: Build React application
FROM node:20-alpine AS build

WORKDIR /app
COPY ./package.json yarn.lock ./

RUN yarn install --frozen-lockfile

COPY . .

RUN yarn build

# Stage 2: Serve React build with Nginx
FROM nginx:alpine

COPY ./nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/out /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
