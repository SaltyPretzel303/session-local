package services

import (
	"saltypretzel/session-backend/db"
	"saltypretzel/session-backend/model"
)

type IUserRepository interface {
	CreateUser(user model.User, tokensId string) (*db.User, error)
	RemoveUser(username string) error

	GetByUsername(username string) (*db.User, error)
	GetByToken(token string) (*db.User, error)
}

type IChannelRepository interface {
	GetFollowing(username string, qRange model.QueryRange) ([]db.Channel, error)
	IsFollowing(username string, channel string) (bool, error)

	Follow(username string, whom string) error
	Unfollow(username string, whom string) error
}
