# Mind Archive web interface — development image.
#
# This runs the Vite dev server, which is what you want locally: hot reload and
# fast feedback. A production image would build static assets and serve them
# behind nginx. That belongs to Milestone 7 and is noted in docs/BACKLOG.md.

FROM node:22-alpine

WORKDIR /app

# Copy the manifests first so that editing source code does not invalidate the
# cached dependency layer.
COPY package.json package-lock.json* ./

# npm ci needs a lockfile; fall back to npm install on a fresh clone that does
# not have one committed yet.
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .

# node:alpine already provides an unprivileged 'node' user.
RUN chown -R node:node /app
USER node

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
