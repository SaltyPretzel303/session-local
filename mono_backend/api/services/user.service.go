package services

import "saltypretzel/session-backend/db"

type UserService struct {
	Db db.UserRepository
}

func (us *UserService) GetUserByUsername(username string) (*db.User, error) {
	user, err := us.Db.GetByUsername(username)
	if err != nil {
		return nil, err
	}
	return user, nil
}

func (us *UserService) GetUserByToken(token string) (*db.User, error) {
	user, err := us.Db.GetByToken(token)
	if err != nil {
		return nil, err
	}
	return user, nil
}

func (us *UserService) IsAuthenticated(username string) (bool, error) {
	return false, nil
}

func (us *UserService) GetFollowing(username string) ([]db.Channel, error) {
	return []db.Channel{}, nil
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
