package tests

import (
	"fmt"
	"testing"
)

type IPrinter interface {
	toPrint() string
}

type Printer struct {
	value string
}

func (p *Printer) toPrint() string {
	return p.value
}

type InnerData struct {
	value string
}

type Data struct {
	InnerData
	name string
}

func TestComposition(t *testing.T) {

	d := &Data{
		name:      "someName",
		InnerData: InnerData{value: "Somevalue"},
	}

	fmt.Println(d.value)
}
