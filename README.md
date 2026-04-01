# ZTVS First-Party Plugins

![Build Status](https://github.com/mosesgameli/ztvs-plugins/actions/workflows/ci.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/mosesgameli/ztvs-plugins)
![License](https://img.shields.io/github/license/mosesgameli/ztvs-plugins)

This repository contains the officially supported first-party plugins for the **Zero Trust Vulnerability Scanner (ZTVS)**. These plugins provide critical host security auditing across various environments.

## 🔌 Available Plugins

### Go Plugins (Compiled)
These plugins are built using the [ZTVS Go SDK](https://github.com/mosesgameli/ztvs-sdk-go) and optimized for performance.

- **`plugin-os`**: Core operating system security checks (SSH hardening, password policies, user auditing).
- **`plugin-axios-mitigation`**: Supply-chain protection targeting known compromised dependencies (e.g., the 2026 Axios RAT).


## 🚀 Installation & Usage

### Automatic Installation (Recommended)
You do not need to install these plugins manually. The `zt` engine automatically discovers and installs them from the official registry.

To sync with the latest versions:

```bash
zt plugin update
```

### Manual Installation from Source
If you want to modify or build plugins manually, ensure you have **Go 1.26.1+** installed.

```bash
git clone https://github.com/mosesgameli/ztvs-plugins.git
cd ztvs-plugins
make build
```

This will produce binaries in the `dist/` directory. You can copy these to your local plugin path:
- **Linux/macOS:** `~/.ztvs/plugins/`
- **Windows:** `%LOCALAPPDATA%\ztvs\plugins\`

## 🛠 Developing Plugins
Interested in building your own? Check out the [ZTVS Documentation](https://github.com/mosesgameli/ztvs/tree/main/docs) for the full protocol specification.

## 📄 License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
