package tests

import (
	"fmt"
	"testing"
)

type nextFunc func(value string)

func log_1(next nextFunc) nextFunc {
	return func(val string) {
		nextVal := fmt.Sprintf("%v + log_1", val)
		next(nextVal)
	}
}

func log_2(next func(value string)) func(string) {
	return func(val string) {
		nextVal := fmt.Sprintf("%v + log_2", val)
		next(nextVal)
	}
}

func TestMiddleware(t *testing.T) {
	log_1(log_2(func(val string) {
		fmt.Printf("final value : %v \n", val)
	}))("Initial value")
}
