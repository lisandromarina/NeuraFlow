FROM node:20

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

ENV CHOKIDAR_USEPOLLING=true
# Start Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]