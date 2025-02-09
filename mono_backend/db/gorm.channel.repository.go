package db

import (
	"fmt"
	"saltypretzel/session-backend/model"

	"gorm.io/gorm"
)

type UserRepo interface {
	GetByUsername(username string) (*User, error)
}

type GormChannelRepository struct {
	gormDb   *gorm.DB
	userRepo UserRepo
}

func NewChannelRepo(db *gorm.DB, userRepo UserRepo) (*GormChannelRepository, error) {
	err := db.AutoMigrate(&Channel{})

	if err != nil {
		return nil, err
	}

	return &GormChannelRepository{gormDb: db, userRepo: userRepo}, nil
}

func (r *GormChannelRepository) GetFollowing(username string, qRange *model.QueryRange) ([]Channel, error) {
	user, err := r.userRepo.GetByUsername(username)
	if err != nil {
		return nil, err
	}

	userId := user.ID

	queryRecord := FollowRecord{UserId: userId}

	followingRecs := []FollowRecord{}
	qRes := r.gormDb.
		Scopes(AsPage(qRange)).
		Where(&queryRecord).
		Find(&followingRecs)

	if qRes.Error != nil {
		return nil, qRes.Error
	}

	channels := make([]Channel, len(followingRecs))

	for ind, rec := range followingRecs {
		channel := Channel{}
		err = r.gormDb.First(&channel, rec.ChannelId).Error
		if err != nil {
			return nil, err
		}

		channels[ind] = channel
	}

	return channels, nil
}

func (r *GormChannelRepository) GetById(id uint) (*Channel, error) {
	channel := Channel{}
	err := r.gormDb.First(&channel, id).Error

	if err != nil {
		return nil, err
	}

	return &channel, nil
}

func (r *GormChannelRepository) GetByName(name string) (*Channel, error) {
	queryChan := Channel{Name: name}

	channel := Channel{}
	qRes := r.gormDb.Where(queryChan).First(&channel)

	if qRes.Error != nil {
		return nil, qRes.Error
	}

	return &channel, nil
}

func (r *GormChannelRepository) IsFollowing(username string, channelName string) (bool, error) {
	user, err := r.userRepo.GetByUsername(username)
	if err != nil {
		return false, err
	}

	channel, err := r.GetByName(channelName)
	if err != nil {
		return false, err
	}

	fRecQuery := FollowRecord{UserId: user.ID, ChannelId: channel.ID}
	exists := false

	qRes := r.gormDb.
		Model(&FollowRecord{}).
		Select("count(*) > 0").
		Where(&fRecQuery).
		Find(&exists)

	if qRes.Error != nil {
		return false, qRes.Error
	}

	return exists, nil
}

func (r *GormChannelRepository) Follow(username string, channelName string) error {
	isFolowing, err := r.IsFollowing(username, channelName)
	if err != nil {
		return err
	}

	if isFolowing {
		return fmt.Errorf("already following this channel")
	}

	user, err := r.userRepo.GetByUsername(username)
	if err != nil {
		return err
	}

	channel, err := r.GetByName(channelName)
	if err != nil {
		return err
	}

	followRecord := FollowRecord{
		UserId:    user.ID,
		ChannelId: channel.ID,
	}

	qRes := r.gormDb.Create(&followRecord)
	if qRes.Error != nil {
		return qRes.Error
	}

	return nil
}

func (r *GormChannelRepository) Unfollow(username string, channelName string) error {
	user, err := r.userRepo.GetByUsername(username)
	if err != nil {
		return err
	}

	channel, err := r.GetByName(channelName)
	if err != nil {
		return err
	}

	removeQuery := FollowRecord{UserId: user.ID, ChannelId: channel.ID}

	return r.gormDb.Where(&removeQuery).Delete(&FollowRecord{}).Error
}
