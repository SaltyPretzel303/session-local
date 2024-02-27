FROM session/frontend_base

WORKDIR /app/react_app
ENTRYPOINT ["npm", "start"]