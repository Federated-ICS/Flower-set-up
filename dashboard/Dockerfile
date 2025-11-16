FROM node:20-alpine

WORKDIR /app
COPY dashboard/package.json dashboard/vite.config.js dashboard/index.html ./
COPY dashboard/src ./src
RUN npm install
RUN npm run build

EXPOSE 4173
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]
