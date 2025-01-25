FROM golang:1.23.5-bookworm

WORKDIR /app

# Non-necessary files and dirs are excluded by the dockerignore.
ADD ./mono_backend/ ./

# ADD ./mono_backend/api ./api
# ADD	./mono_backend/data ./data
# ADD	mono_backend/config.go \
# 	mono_backend/config.json \
# 	mono_backend/go.mod \
# 	mono_backend/main.go ./

RUN go mod tidy && go build . 

ENTRYPOINT ["./session-backend"]
