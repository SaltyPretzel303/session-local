package controllers

import "fmt"

func GET(c IController, path string) string {
	return fmt.Sprintf("GET %v%v", c.GetBasePath(), path)
}

func POST(c IController, path string) string {
	return fmt.Sprintf("POST %v%v", c.GetBasePath(), path)
}

func DELETE(c IController, path string) string {
	return fmt.Sprintf("DELETE %v%v", c.GetBasePath(), path)
}
