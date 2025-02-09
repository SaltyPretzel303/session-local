package db

import (
	"fmt"
	"saltypretzel/session-backend/config"
	"saltypretzel/session-backend/model"
	"testing"
)

func dbConfig() config.Db {
	return config.Db{
		Address:  "database.session.com",
		Port:     5432,
		User:     "session_user",
		Password: "session_password",
		Database: "session",
	}
}

func getDb(t *testing.T) *GormUserRepository {
	gormDb, err := GetPgresDb(dbConfig())

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

	db := getDb(t)

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

	db := getDb(t)

	for i := 0; i < 10; i++ {
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
	db := getDb(t)

	for i := 0; i < 10; i++ {
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
	db := getDb(t)

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
