package db

import (
	"saltypretzel/session-backend/model"

	"gorm.io/gorm"
)

type User struct {
	gorm.Model

	Email    string
	Username string
	// Password string // hashed

	TokensId string
}

func (u *User) AsModel() *model.User {
	return &model.User{
		Username: u.Username,
		Email:    u.Email,
	}
}

type Channel struct {
	gorm.Model
	UserID uint
}

type FollowRecord struct {
	gorm.Model

	UserId    uint
	ChannelId uint
}
