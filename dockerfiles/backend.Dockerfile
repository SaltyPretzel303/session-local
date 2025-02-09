FROM golang:1.23.5-bookworm

WORKDIR /app

RUN mkdir /go_deps

ADD ./mono_backend/go.mod ./go.mod
ADD ./mono_backend/go.sum ./go.sum
RUN go mod download

# # Non-necessary files and dirs are excluded by the dockerignore.
ADD ./mono_backend/ ./

# ADD ./mono_backend/api ./api
# ADD	./mono_backend/db ./db
# ADD	./mono_backend/model ./model
# ADD	mono_backend/config.go \
# 	mono_backend/config.json \
# 	# mono_backend/go.mod \
# 	mono_backend/main.go ./

RUN go build .

ENTRYPOINT ["./session-backend"]
