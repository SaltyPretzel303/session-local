FROM golang:1.23.5-bookworm

RUN go install github.com/air-verse/air@latest

WORKDIR /app

ENTRYPOINT ["air", "."]
