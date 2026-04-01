package main

import (
	"github.com/mosesgameli/ztvs-sdk-go/sdk"
	"github.com/mosesgameli/ztvs/plugins/plugin-axios-mitigation/pkg/checks"
)

func main() {
	meta := sdk.Metadata{
		Name:       "Axios Mitigation Plugin",
		Version:    "1.0.0",
		APIVersion: 1,
	}

	checksList := []sdk.Check{
		&checks.DependencyCheck{},
		&checks.HostIOCCheck{},
		&checks.NetworkCheck{},
	}

	sdk.Run(meta, checksList)
}
