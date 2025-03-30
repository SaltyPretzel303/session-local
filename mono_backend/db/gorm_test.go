package db

import (
	"context"
	"fmt"
	"saltypretzel/session-backend/config"
	"saltypretzel/session-backend/model"
	"strconv"
	"testing"

	"github.com/docker/go-connections/nat"
	_ "github.com/jackc/pgx/v5"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

func dbConfig() config.Db {
	return config.Db{
		Port:     5432,
		User:     "test_session_user",
		Password: "test_session_password",
		Database: "test_session",
	}
}

func setupDb(ctx context.Context, t *testing.T) config.Db {
	cfg := dbConfig()

	var envs = map[string]string{
		"POSTGRES_USER":     cfg.User,
		"POSTGRES_PASSWORD": cfg.Password,
		"POSTGRES_DB":       cfg.Database,
	}

	// pgresUrl := func(host string, port nat.Port) string {
	// 	return fmt.Sprintf("postgres://%s:%s@localhost:%v/%v?sslmode=disable",
	// 		cfg.User, cfg.Password, cfg.Port, cfg.Database)
	// }

	port := nat.Port(strconv.Itoa(cfg.Port))

	req := testcontainers.GenericContainerRequest{
		ContainerRequest: testcontainers.ContainerRequest{
			Image:        "postgres:latest",
			ExposedPorts: []string{port.Port()},
			Cmd:          []string{"postgres", "-c", "fsync=off"},
			Env:          envs,
			// WaitingFor:   wait.ForSQL(port, "pgx", pgresUrl),
			WaitingFor: wait.ForListeningPort(nat.Port("5432/tcp")),
		},
		Started: true,
	}

	container, err := testcontainers.GenericContainer(ctx, req)
	if err != nil {
		t.Fatal("failed to create db testcontainer: ", err)
	}

	host_port, err := container.MappedPort(ctx, port)
	if err != nil {
		t.Fatal("failed to get mapped db testcontainer port: ", err)
	}

	cfg.Address = "localhost"
	p, _ := strconv.Atoi(host_port.Port())
	cfg.Port = p

	return cfg
}

func getDb(t *testing.T, cfg config.Db) *GormUserRepository {
	gormDb, err := NewPgresDb(cfg)

	if err != nil {
		t.Fatal("failed to create db, err: ", err)
	}

	userRepo, err := NewUserRepo(gormDb)
	if err != nil {
		t.Fatal("failed to create user repository: ", err)
	}

	return userRepo
}

func TestCreateUser(t *testing.T) {

	ctx := context.Background()
	c_cfg := setupDb(ctx, t)

	db := getDb(t, c_cfg)

	for i := 0; i < 10; i++ {
		username := fmt.Sprintf("user_%v", i)
		email := fmt.Sprintf("user_%v@mail.com", i)
		token := fmt.Sprintf("users_%v_token", i)

		user := model.User{
			Username: username,
			Email:    email,
		}

		_, err := db.CreateUser(user, token)
		if err != nil {
			t.Fatalf("failed to save user: %v, err: %v", username, err)
		}
	}

}

func TestGetUserByUsername(t *testing.T) {

	ctx := context.Background()
	c_cfg := setupDb(ctx, t)

	db := getDb(t, c_cfg)

	for i := range 10 {
		username := fmt.Sprintf("user_%v", i)

		user, err := db.GetByUsername(username)
		if err != nil {
			t.Fatalf("failed to query user with username: %v, err: %v", username, err)
		}

		email := fmt.Sprintf("user_%v@mail.com", i)
		token := fmt.Sprintf("users_%v_token", i)

		if user.Username != username {
			t.Fatalf("queried user's username not matching: %v != %v", user.Username, username)
		}

		if user.Email != email {
			t.Fatalf("queried user's email not matching: %v != %v", user.Email, email)
		}

		if user.TokensId != token {
			t.Fatalf("queried user's token not matching: %v != %v", user.TokensId, token)
		}
	}
}

func TestGetUserByToken(t *testing.T) {
	ctx := context.Background()
	c_cfg := setupDb(ctx, t)

	db := getDb(t, c_cfg)

	for i := range 10 {
		token := fmt.Sprintf("users_%v_token", i)

		user, err := db.GetByToken(token)
		if err != nil {
			t.Fatalf("failed to query user with token: %v, err: %v", token, err)
		}

		username := fmt.Sprintf("user_%v", i)
		email := fmt.Sprintf("user_%v@mail.com", i)

		if user.Username != username {
			t.Fatalf("1ueried user's username not matching: %v != %v", user.Username, username)
		}

		if user.Email != email {
			t.Fatalf("queried user's email not matching: %v != %v", user.Email, email)
		}

		if user.TokensId != token {
			t.Fatalf("queried user's token not matching: %v != %v", user.TokensId, token)
		}
	}

}

func TestRemoveUserByUsername(t *testing.T) {
	ctx := context.Background()
	c_cfg := setupDb(ctx, t)

	db := getDb(t, c_cfg)

	for i := 0; i < 10; i++ {
		username := fmt.Sprintf("user_%v", i)
		err := db.RemoveUser(username)

		if err != nil {
			t.Errorf("failed to remove user: %v, err: %v", username, err)
		}

		user, err := db.GetByUsername(username)
		if err != nil && err.Error() != "record not found" {
			t.Errorf("query user after delete failed, err: %v", err)
		}

		if user != nil {
			t.Error("user queried after delete")
		}

	}

}
