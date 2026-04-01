package checks

import (
	"os"
	"testing"
)

func TestGetConfigPath(t *testing.T) {
	c := &SSHCheck{}

	// Test Linux/Unix path
	got := c.GetConfigPath("linux")
	want := "/etc/ssh/sshd_config"
	if got != want {
		t.Errorf("GetConfigPath(linux) = %v; want %v", got, want)
	}

	// Test Windows path (without ProgramData set)
	_ = os.Setenv("ProgramData", "")
	got = c.GetConfigPath("windows")
	want = `C:\ProgramData\ssh\sshd_config`
	if got != want {
		t.Errorf("GetConfigPath(windows) with empty ProgramData = %v; want %v", got, want)
	}

	// Test Windows path (with ProgramData set)
	_ = os.Setenv("ProgramData", `D:\Data`)
	got = c.GetConfigPath("windows")
	want = `D:\Data\ssh\sshd_config`
	if got != want {
		t.Errorf("GetConfigPath(windows) with ProgramData=D:\\Data = %v; want %v", got, want)
	}
}
