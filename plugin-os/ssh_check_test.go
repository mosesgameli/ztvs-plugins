package main

import (
	"os"
	"testing"
)

func TestGetConfigPath(t *testing.T) {
	c := &SSHCheck{}

	// Test Linux/Unix path
	got := c.getConfigPath("linux")
	want := "/etc/ssh/sshd_config"
	if got != want {
		t.Errorf("getConfigPath(linux) = %v; want %v", got, want)
	}

	// Test Darwin path
	got = c.getConfigPath("darwin")
	want = "/etc/ssh/sshd_config"
	if got != want {
		t.Errorf("getConfigPath(darwin) = %v; want %v", got, want)
	}

	// Test Windows path (without ProgramData set)
	_ = os.Setenv("ProgramData", "")
	got = c.getConfigPath("windows")
	want = `C:\ProgramData\ssh\sshd_config`
	if got != want {
		t.Errorf("getConfigPath(windows) with empty ProgramData = %v; want %v", got, want)
	}

	// Test Windows path (with ProgramData set)
	_ = os.Setenv("ProgramData", `D:\Data`)
	got = c.getConfigPath("windows")
	want = `D:\Data\ssh\sshd_config`
	if got != want {
		t.Errorf("getConfigPath(windows) with ProgramData=D:\\Data = %v; want %v", got, want)
	}
}
