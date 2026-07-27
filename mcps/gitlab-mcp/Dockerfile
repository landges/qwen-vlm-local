FROM node:22-alpine

ENV NODE_ENV=production \
    GITLAB_DISABLE_VERSION_CHECK=true

RUN npm install --global --omit=dev @zereight/mcp-gitlab@2.1.42 \
    && npm cache clean --force

USER node

EXPOSE 3002

ENTRYPOINT ["zereight-mcp-gitlab"]
