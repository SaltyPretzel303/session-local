package db

import (
	"saltypretzel/session-backend/model"

	"gorm.io/gorm"
)

type GormUserRepository struct {
	db *gorm.DB
}

func NewUserRepo(db *gorm.DB) (*GormUserRepository, error) {
	err := db.AutoMigrate(&User{})

	if err != nil {
		return nil, err
	}

	return &GormUserRepository{db: db}, nil
}

func (r *GormUserRepository) CreateUser(user model.User, tokensId string) (*User, error) {
	dbUser := User{
		Email:    user.Email,
		Username: user.Username,
		TokensId: tokensId,
	}

	insertRes := r.db.Create(&dbUser)
	if insertRes.Error != nil {
		// fmt.Println("Failed to create new user, db error: ", insertRes.Error)
		return nil, insertRes.Error
	}

	return &dbUser, nil
}

func (r *GormUserRepository) GetByUsername(username string) (*User, error) {
	resUser := User{}
	qRes := r.db.Where(&User{Username: username}).First(&resUser)
	if qRes.Error != nil {
		return nil, qRes.Error
	}

	return &resUser, nil
}

func (r *GormUserRepository) GetByToken(token string) (*User, error) {
	resUser := User{}
	qRes := r.db.Where(&User{TokensId: token}).First(&resUser)
	if qRes.Error != nil {
		return nil, qRes.Error
	}

	return &resUser, nil
}

func (r *GormUserRepository) RemoveUser(username string) error {
	res := r.db.Where("Username = ?", username).Delete(&User{})

	return res.Error
}
