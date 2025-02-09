package config

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/kelseyhightower/envconfig"
)

type Auth struct {
	AuthApiBase  string `envconfig:"AUTH_API_BASE" json:"AuthApiBase"`
	SiteBasePath string `envconfig:"SITE_BASE_PATH" json:"SiteBasePath"`

	AppName string `envconfig:"APP_NAME" json:"AppName"`

	TokensApiAddr  string `envconfig:"TOKENS_API_ADDR" json:"TokensApiAddr"`
	TokensCoreAddr string `envconfig:"TOKENS_CORE_ADDR" json:"TokensCoreAddr"`
}

type Db struct {
	Address  string `envconfig:"POSTGRES_ADDR"`
	Port     int    `envconfig:"POSTGRES_PORT"`
	User     string `envconfig:"POSTGRES_USER"`
	Password string `envconfig:"POSTGRES_PASSWORD"`
	Database string `envconfig:"POSTGRES_DB"`
}

type Config struct {
	DomainName string `envconfig:"DOMAIN_NAME" json:"DomainName"`
	ApiPrefix  string `envconfig:"API_PREFIX" json:"ApiPrefix"`
	Auth       `json:"AuthConfig"`
	Db         `json:"Db"`
}

func WithFile(path string, config *Config) error {
	cfile, err := os.Open(path)
	if err != nil {
		return fmt.Errorf("failed to open file on path: %v, err: %v", path, err)
	}
	defer cfile.Close()

	err = json.NewDecoder(cfile).Decode(config)
	if err != nil {
		return fmt.Errorf("failed to parse json config: %v", err)
	}

	return nil
}

func WithEnv(config *Config) error {
	err := envconfig.Process("", config)

	if err != nil {
		return fmt.Errorf("failed to read config from env: %v", err)
	}

	return nil
}
