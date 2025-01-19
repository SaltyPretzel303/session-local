package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/kelseyhightower/envconfig"
)

type Config struct {
	DomainName string `envconfig:"DOMAIN_NAME", json:"DomainName"`

	AuthConfig struct {
		Path           string `envconfig:"AUTH_PATH", json:"AuthPath"`
		TokensAppName  string `envconfig:"TOKENS_APP_NAME, json:"TokensAppName`
		TokensApiAddr  string `envconfig:"TOKENS_API_ADDR", json:"TokensApiAddr"`
		SiteBasePath   string `envconfig:"SITE_BASE_PATH", json:"SiteBasePath"`
		TokensCoreAddr string `envconfig:"TOKENS_CORE_ADDR" json:"TokensCoreAddr"`
		TokensCorePort string `envconfig:"TOKENS_CORE_PORT" json:"TokensCorePort"`
	}
}

func ReadFile(path string, config *Config) error {
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

func ReadEnv(config *Config) error {

	err := envconfig.Process("", config)

	if err != nil {
		return fmt.Errorf("failed to read config from env: %v", err)
	}

	return nil
}
