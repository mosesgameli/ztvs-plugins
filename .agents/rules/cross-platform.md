# Cross-Platform Compatibility Rules

These rules are MANDATORY for all plugin and host development to ensure ZTVS remains truly cross-platform.

## Core Rules

1.  **OS Detection**: Always use `runtime.GOOS` to detect the underlying operating system and adjust platform-specific logic (e.g., file paths, command execution).
2.  **Path Handling**: 
    - Use `path/filepath` for all path manipulations to ensure correct separators (`/` vs `\`).
    - Avoid hardcoding Unix-style paths (e.g., `/etc/`) without a Windows fallback (e.g., `%ProgramData%` or `%AppData%`).
3.  **Environment Variables**:
    - Use `os.Getenv("ProgramData")` or `os.Getenv("AppData")` for system-wide configuration locations on Windows.
    - Provide sensible defaults for all platforms.
4.  **Testing**:
    - Implement unit tests that specifically verify path selection and OS-specific logic.
    - Ensure CI/CD workflows run tests on `ubuntu-latest`, `macos-latest`, and `windows-latest`.

## Implementation Example (Go)

```go
func getConfigPath(goos string) string {
    if goos == "windows" {
        return os.Getenv("ProgramData") + `\app\config.yaml`
    }
    return "/etc/app/config.yaml"
}
```
