package db

import (
	"fmt"
	"saltypretzel/session-backend/model"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type PostgresUserRepository struct {
	db *gorm.DB
}

func NewPostgre() (*PostgresUserRepository, error) {
	dns := "host=localhost user=postgres password=postgres dbname=postgres port=5432 sslmode=disable"
	db, err := gorm.Open(postgres.Open(dns), &gorm.Config{})

	if err != nil {
		return nil, err
	}

	return &PostgresUserRepository{db: db}, nil
}

func (f *PostgresUserRepository) CreateUser(user model.User) error {
	fmt.Println("Yo")
	return nil
}

func (r *PostgresUserRepository) GetByUsername(username string) (*User, error) {
	panic("unimplemented")
}

func (p *PostgresUserRepository) GetByToken(token string) (*User, error) {
	return nil, nil
}

func (r *PostgresUserRepository) IsAuthenticated(username string) (bool, error) {
	panic("unimplemented")
}

func (r *PostgresUserRepository) GetFollowing(username string) ([]Channel, error) {
	panic("unimplemented")
}

func (r *PostgresUserRepository) IsFollowing(username string, whom string) (bool, error) {
	panic("unimplemented")
}

func (r *PostgresUserRepository) RemoveUser(username string) error {
	panic("unimplemented")
}

func (r *PostgresUserRepository) AuthorizeView(username string, channel string) (bool, error) {
	panic("unimplemented")
}

func (r *PostgresUserRepository) AuthorizeChat(username string, channel string) (bool, error) {
	panic("unimplemented")
}

func (r *PostgresUserRepository) Follow(username string, whom string) error {
	panic("unimplemented")
}

func (r *PostgresUserRepository) Unfollow(username string, whom string) error {
	panic("unimplemented")
}
