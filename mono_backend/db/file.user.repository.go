package db

import (
	"fmt"
	"saltypretzel/session-backend/model"
)

type FileUserRepository struct {
}

var users = make(map[string]User)
var sessions = make(map[string]bool)
var followings = []FollowRecord{}
var channels = make(map[uint]Channel)

func NewFileUserRepository() *FileUserRepository {
	return &FileUserRepository{}
}

func (f *FileUserRepository) CreateUser(user model.User) error {
	fmt.Println("Yo")
	return nil
}

func (fr *FileUserRepository) GetByUsername(username string) (*User, error) {
	if user, ok := users[username]; ok {
		return &user, nil
	}

	return nil, fmt.Errorf("no such user: %v", username)
}

func (fr *FileUserRepository) GetByToken(token string) (*User, error) {
	for _, user := range users {
		if user.TokensId == token {
			return &user, nil
		}
	}

	return nil, fmt.Errorf("no such user, token: %v", token)
}

func (f *FileUserRepository) IsAuthenticated(username string) (bool, error) {
	if authed, ok := sessions[username]; ok && authed {
		return true, nil
	}

	return false, nil
	// TODO I guess error is not required
}

func (f *FileUserRepository) GetFollowing(username string) ([]Channel, error) {
	out := []Channel{}

	user, exists := users[username]
	if !exists {
		return nil, fmt.Errorf("no such user: %v", username)
	}

	for _, fRecord := range followings {
		if fRecord.UserId == user.ID {
			if ch, ok := channels[fRecord.ChannelId]; ok {
				out = append(out, ch)
			} else {
				fmt.Printf("Failed to find channel from fRecord, cId: %v", fRecord.ChannelId)
			}
		}
	}

	return out, nil
}

func getUserById(id uint) (*User, bool) {
	for _, u := range users {
		if u.ID == id {
			return &u, true
		}
	}

	return nil, false
}

func getChannelByName(name string) (*Channel, bool) {
	for _, c := range channels {
		if user, ok := getUserById(c.UserID); ok {
			if user.Username == name {
				return &c, true
			}
		}
	}

	return nil, false
}

func (f *FileUserRepository) IsFollowing(username string, channel string) (bool, error) {
	user, ok := users[username]
	if !ok {
		return false, fmt.Errorf("no such user: %v", username)
	}

	ch, ok := getChannelByName(channel)
	if !ok {
		return false, fmt.Errorf("no such channel: %v", channel)
	}

	for _, fRecord := range followings {
		if fRecord.UserId == user.ID && fRecord.ChannelId == ch.ID {
			return true, nil
		}
	}

	return false, nil
}

func (f *FileUserRepository) RemoveUser(username string) error {
	delete(users, username)
	delete(sessions, username)
	return nil
}

func (f *FileUserRepository) AuthorizeView(username string, channel string) (bool, error) {
	return true, nil
}

func (f *FileUserRepository) AuthorizeChat(username string, channel string) (bool, error) {
	return true, nil
}

func (f *FileUserRepository) Follow(username string, whom string) error {
	user, ok := users[username]
	if !ok {
		return fmt.Errorf("no such user: %v", username)
	}

	ch, ok := getChannelByName(whom)

	if !ok {
		return fmt.Errorf("no such channel: %v", whom)
	}

	newRec := &FollowRecord{
		UserId:    user.ID,
		ChannelId: ch.ID,
	}
	followings = append(followings, *newRec)

	return nil
}

func (f *FileUserRepository) Unfollow(username string, whom string) error {
	user, ok := users[username]
	if !ok {
		return fmt.Errorf("no such user: %v", username)
	}

	ch, ok := getChannelByName(whom)
	if !ok {
		return fmt.Errorf("no such channel: %v", whom)
	}

	for i, fRecord := range followings {
		if fRecord.UserId == user.ID && fRecord.ChannelId == ch.ID {
			followings = append(followings[:i], followings[i+1:]...)
			return nil
		}
	}

	return fmt.Errorf("no such follow record")
}
