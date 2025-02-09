package db

import (
	"fmt"
	"saltypretzel/session-backend/config"
	"saltypretzel/session-backend/model"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

func AsPage(qRange *model.QueryRange) func(db *gorm.DB) *gorm.DB {
	return func(db *gorm.DB) *gorm.DB {
		if qRange == nil {
			return db
		}

		return db.Offset(qRange.From).Limit(qRange.Count)
	}
}

func GetPgresDb(cfg config.Db) (*gorm.DB, error) {
	dns := fmt.Sprintf("host=%v port=%v user=%v password=%v dbname=%v sslmode=disable",
		cfg.Address, cfg.Port, cfg.User, cfg.Password, cfg.Database)

	db, err := gorm.Open(postgres.Open(dns),
		&gorm.Config{Logger: logger.Default.LogMode(logger.Silent)})

	if err != nil {
		return nil, err
	}

	return db, nil
}
