package services

import (
	"fmt"
	"saltypretzel/session-backend/model"
)

type UserService struct {
	UserDb IUserRepository
}

func (us *UserService) CreateUser(user model.User, tokenId string) (*model.User, error) {
	dbUser, err := us.UserDb.CreateUser(user, tokenId)

	if err != nil {
		fmt.Println("user service failed to create user")
		return nil, err
	}

	return dbUser.AsModel(), nil
}

func (us *UserService) GetUserByUsername(username string) (*model.User, error) {
	user, err := us.UserDb.GetByUsername(username)
	if err != nil {
		return nil, err
	}
	return user.AsModel(), nil
}

func (us *UserService) GetUserByToken(token string) (*model.User, error) {
	user, err := us.UserDb.GetByToken(token)
	if err != nil {
		return nil, err
	}
	return user.AsModel(), nil
}

func (us *UserService) GetFollowing(username string) ([]model.Channel, error) {
	return []model.Channel{}, nil
}

func (us *UserService) IsFollowing(username string, whom string) (bool, error) {
	return false, nil
}

func (us *UserService) RemoveUser(username string) error {
	return nil
}

func (us *UserService) AuthorizeView(username string, channel string) (bool, error) {
	return false, nil
}

func (us *UserService) AuthorizeChat(username string, channel string) (bool, error) {
	return false, nil
}

func (us *UserService) Follow(username string, whom string) error {
	return nil
}

func (us *UserService) Unfollow(username string, whom string) error {
	return nil
}
