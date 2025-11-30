FROM node:20

WORKDIR /app

COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

COPY . .

# Ensure node_modules/.bin is in PATH
ENV PATH=/app/node_modules/.bin:$PATH

EXPOSE 5173
ENV CHOKIDAR_USEPOLLING=true

# Force rebuild optional binaries
RUN npm rebuild

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
