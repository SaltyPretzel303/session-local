package db

import "saltypretzel/session-backend/model"

type UserRepository interface {
	CreateUser(user model.User) error

	GetByUsername(username string) (*User, error)
	GetByToken(token string) (*User, error)
	IsAuthenticated(username string) (bool, error)
	GetFollowing(username string) ([]Channel, error)
	IsFollowing(username string, channel string) (bool, error)
	RemoveUser(username string) error
	AuthorizeView(username string, channel string) (bool, error)
	AuthorizeChat(username string, channel string) (bool, error)
	Follow(username string, whom string) error
	Unfollow(username string, whom string) error
}
