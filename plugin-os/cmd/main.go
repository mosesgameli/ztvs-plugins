package main

import (
	"github.com/mosesgameli/ztvs-sdk-go/sdk"
	"github.com/mosesgameli/ztvs/plugins/plugin-os/pkg/checks"
)

func main() {
	sdk.Run(sdk.Metadata{
		Name:       "plugin-os",
		Version:    "1.0.0",
		APIVersion: 1,
	}, []sdk.Check{
		&checks.SSHCheck{},
	})
}
