package main

import (
	"bufio"
	"context"
	"os"
	"runtime"
	"strings"

	"github.com/mosesgameli/ztvs-sdk-go/sdk"
)

type SSHCheck struct{}

func (c *SSHCheck) ID() string {
	return "ssh_config"
}

func (c *SSHCheck) Name() string {
	return "SSH Configuration Check"
}

func (c *SSHCheck) Run(
	ctx context.Context,
) (*sdk.Finding, error) {
	configPath := c.getConfigPath(runtime.GOOS)

	file, err := os.Open(configPath)
	if err != nil {
		if os.IsNotExist(err) {
			return nil, nil // No file, no finding
		}
		return nil, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		fields := strings.Fields(line)
		if len(fields) >= 2 && strings.EqualFold(fields[0], "PermitRootLogin") {
			if strings.EqualFold(fields[1], "yes") {
				return &sdk.Finding{
					ID:          "F-SSH-001",
					Severity:    "high",
					Title:       "SSH Root Login Enabled",
					Description: "The SSH server is configured to allow direct root login, which is a major security risk.",
					Evidence: map[string]interface{}{
						"file":           configPath,
						"finding_string": line,
					},
					Remediation: "Modify /etc/ssh/sshd_config to set 'PermitRootLogin no' and reload the sshd service.",
				}, nil
			}
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}

	return nil, nil
}

func (c *SSHCheck) getConfigPath(goos string) string {
	if goos == "windows" {
		programData := os.Getenv("ProgramData")
		if programData == "" {
			programData = `C:\ProgramData`
		}
		return programData + `\ssh\sshd_config`
	}
	return "/etc/ssh/sshd_config"
}
