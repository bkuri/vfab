# Command Line Reference Cheat Sheet

**All commands at a glance** - Quick lookup for any vfab command.

---

## 🧭 Quick Navigation
- **New to vfab?** [Daily Quick Start](../beginner/daily-quickstart.md)
- **Need command examples?** [Common Commands](../beginner/common-commands.md)
- **Configuration options?** [Configuration Reference](configuration.md)
- **Optimization presets?** [Optimization Presets](optimization-presets.md)

---

## 📋 Core Commands

### Job Management
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab add <file>` | Add new job | `vfab add design.svg` |
| `vfab list jobs` | List all jobs | `vfab list jobs --state completed` |
| `vfab info job <name>` | Job details | `vfab info job my_art` |
| `vfab remove job <name>` | Remove job | `vfab remove job old_job` |

### Planning & Plotting
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab plan <job>` | Plan job | `vfab plan my_art --interactive` |
| `vfab plan-all` | Plan all jobs | `vfab plan-all --preset fast` |
| `vfab plot <job>` | Plot job | `vfab plot my_art --record` |
| `vfab plot-all` | Plot all jobs | `vfab plot-all --monitor` |

### Status & Information
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab status` | Current status | `vfab status --verbose` |
| `vfab check ready` | System check | `vfab check ready --detailed` |
| `vfab list queue` | Current queue | `vfab list queue --watch` |
| `vfab estimate <job>` | Time estimate | `vfab estimate my_art --detailed` |
| `vfab daemon` | Start daemon | `vfab daemon --host 0.0.0.0 --port 8766` |
| `vfab monitor` | Real-time monitor | `vfab monitor --channels jobs,system --follow` |

---

## 🖊️ Resource Management

### Pen Management
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab list pens` | List all pens | `vfab list pens --show-usage` |
| `vfab add pen` | Add new pen | `vfab add pen --name "Fine Black" --width 0.3` |
| `vfab update pen <id>` | Update pen | `vfab update pen 1 --speed-cap 60` |
| `vfab remove pen <id>` | Remove pen | `vfab remove pen 5` |

### Paper Management
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab list paper` | List paper types | `vfab list paper --show-stock` |
| `vfab add paper` | Add paper size | `vfab add paper --name "A4" --width 210 --height 297` |
| `vfab update paper <name>` | Update paper | `vfab update paper "A4" --stock-count 50` |
| `vfab remove paper <name>` | Remove paper | `vfab remove paper "Old Size"` |

---

## ⚙️ Configuration

### Device Configuration
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab config show` | Show config | `vfab config show --device` |
| `vfab config device` | Device settings | `vfab config device --port /dev/ttyUSB0` |
| `vfab setup` | Interactive setup | `vfab setup --device-only` |
| `vfab check device` | Test device | `vfab check device --test-move` |

### General Configuration
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab config validate` | Validate config | `vfab config validate --strict` |
| `vfab config reset` | Reset config | `vfab config reset --device-only` |
| `vfab info system` | System info | `vfab info system --detailed` |

---

## 📊 Statistics & Analytics

### Basic Statistics
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab stats summary` | Summary stats | `vfab stats summary --last 30` |
| `vfab stats jobs` | Job statistics | `vfab stats jobs --by-client` |
| `vfab stats performance` | Performance | `vfab stats performance --pen-usage` |
| `vfab stats pens` | Pen usage | `vfab stats pens --last 90` |

### Advanced Analytics
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab analyze queue` | Queue analysis | `vfab analyze queue --efficiency` |
| `vfab analyze pens` | Pen analysis | `vfab analyze pens --wear-patterns` |
| `vfab analyze production` | Production analysis | `vfab analyze production --cost-analysis` |

---

## 🔄 Recovery & Troubleshooting

### Recovery Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab recovery list` | List recovery options | `vfab recovery list --all` |
| `vfab resume <job>` | Resume job | `vfab resume interrupted_job` |
| `vfab restart <job>` | Restart job | `vfab restart failed_job` |
| `vfab abort <job>` | Abort job | `vfab abort stuck_job` |

### Diagnostic Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab check database` | Database check | `vfab check database --verify` |
| `vfab check camera` | Camera check | `vfab check camera --test-url` |
| `vfab logs` | View logs | `vfab logs --tail 100` |
| `vfab test pattern` | Test pattern | `vfab test pattern --basic` |

---

## 🧹 Maintenance & Cleanup

### Queue Management
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab queue cleanup` | Clean queue | `vfab queue cleanup --completed --older-than 7d` |
| `vfab queue optimize` | Optimize queue | `vfab queue optimize --global-pen-order` |
| `vfab queue backup` | Backup queue | `vfab queue backup --file queue_backup.json` |

### System Maintenance
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab restart` | Restart vfab | `vfab restart --queue-only` |
| `vfab backup data` | Backup data | `vfab backup data --full` |
| `vfab cleanup workspace` | Clean workspace | `vfab cleanup workspace --older-than 30d` |

---

## 🎯 Common Flags & Options

### Job Management Flags
| Flag | Purpose | Example |
|------|---------|---------|
| `--name <string>` | Custom job name | `--name "My Art"` |
| `--paper <size>` | Paper size | `--paper a4` |
| `--priority <level>` | Job priority | `--priority high` |
| `--tags <list>` | Job tags | `--tags "client,logo,v2"` |

### Planning Flags
| Flag | Purpose | Example |
|------|---------|---------|
| `--preset <type>` | Optimization preset | `--preset hq` |
| `--interactive` | Interactive mode | `--interactive` |
| `--dry-run` | Preview only | `--dry-run` |
| `--optimize-pens` | Optimize pen changes | `--optimize-pens` |

### Plotting Flags
| Flag | Purpose | Example |
|------|---------|---------|
| `--record` | Record plotting | `--record` |
| `--preview` | Preview mode | `--preview` |
| `--monitor` | Monitor progress | `--monitor` |
| `--speed <percent>` | Plotting speed | `--speed 50` |

### Information Flags
| Flag | Purpose | Example |
|------|---------|---------|
| `--detailed` | Detailed output | `--detailed` |
| `--json` | JSON output | `--json` |
| `--watch` | Watch mode | `--watch` |
| `--verbose` | Verbose output | `--verbose` |

---

## 📏 Paper Sizes

### Standard Paper Sizes
| Size | Command | Dimensions (mm) |
|------|---------|-----------------|
| A4 | `--paper a4` | 210 × 297 |
| A3 | `--paper a3` | 297 × 420 |
| A5 | `--paper a5` | 148 × 210 |
| Letter | `--paper letter` | 216 × 279 |
| Legal | `--paper legal` | 216 × 356 |

### Custom Paper Sizes
| Format | Example | Result |
|--------|---------|---------|
| Width×Height | `--paper 200x150` | 200mm × 150mm |
| Named custom | `--paper "Custom Large"` | Uses predefined custom size |

---

## ⚡ Optimization Presets

### Available Presets
| Preset | Speed | Quality | Best For |
|--------|-------|---------|-----------|
| `fast` | ⚡ Fast | ✅ Good | Simple designs, tests, drafts |
| `default` | 🚶 Medium | ✨ Better | Most designs, general use |
| `hq` | 🐌 Slow | 💎 Best | Complex art, final prints |
| `none` | ⚡ Instant | ❌ None | Pre-optimized files |

### Preset Selection Guide
```bash
# Simple designs - use fast
vfab plan simple_design --preset fast

# Complex art - use hq
vfab plan complex_art --preset hq

# Already optimized - use none
vfab plan optimized_design --preset none

# Let vfab decide
vfab plan design --auto-preset --target-time 10m
```

---

## 🎨 Multi-Pen Options

### Multi-Pen Flags
| Flag | Purpose | Example |
|------|---------|---------|
| `--pen-mapping <list>` | Manual pen mapping | `--pen-mapping "1,2,3"` |
| `--optimize-pens` | Optimize pen changes | `--optimize-pens` |
| `--force-multi-pen` | Force multi-pen mode | `--force-multi-pen` |
| `--pen-order <list>` | Global pen order | `--pen-order "2,1,3,4"` |

### Multi-Pen Workflow
```bash
# Interactive pen mapping
vfab plan multi_pen_art --interactive

# Custom pen mapping
vfab plan art --pen-mapping "3,1,4,2"

# Global pen optimization
vfab plan-all --optimize-pens --global-pen-order
```

---

## 📹 Camera & Recording

### Camera Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `vfab check camera` | Test camera | `vfab check camera --test-stream` |
| `vfab config camera` | Camera settings | `vfab config camera --url http://...` |
| `vfab record <name>` | Manual recording | `vfab record test --seconds 30` |

### Recording Flags
| Flag | Purpose | Example |
|------|---------|---------|
| `--record` | Record during plot | `--record` |
| `--camera-url <url>` | Custom camera URL | `--camera-url http://...` |
| `--no-camera` | Disable camera | `--no-camera` |

---

## 🔧 Advanced Options

### Performance Flags
| Flag | Purpose | Example |
|------|---------|---------|
| `--max-time <duration>` | Time limit | `--max-time 30m` |
| `--memory-limit <size>` | Memory limit | `--memory-limit 2G` |
| `--parallel <count>` | Parallel jobs | `--parallel 2` |

### Quality Flags
| Flag | Purpose | Example |
|------|---------|---------|
| `--quality-threshold <num>` | Quality threshold | `--quality-threshold 95` |
| `--enforce-quality` | Enforce quality gates | `--enforce-quality` |
| `--auto-replot-failed` | Auto-replot failures | `--auto-replot-failed` |

---

## 🆘 Emergency Commands

### Critical Commands
| Command | Purpose | When to Use |
|---------|---------|-------------|
| `vfab abort` | Immediate stop | Plotter going crazy |
| `vfab emergency-stop` | Hardware stop | Software not responding |
| `vfab reset device` | Reset device | Device unresponsive |
| `vfab restart` | Full restart | System hung |

### Recovery Sequence
```bash
# 1. Immediate stop
vfab abort

# 2. Check status
vfab status

# 3. List recovery options
vfab recovery list

# 4. Apply recovery
vfab resume <job>  # or restart, or remove
```

---

## 💡 Pro Tips & Shortcuts

### Command Shortcuts
```bash
# Common aliases to add to .bashrc/.zshrc
alias pp='vfab plot'
alias pa='vfab add'
alias pl='vfab list'
alias ps='vfab status'
alias pr='vfab resume'
alias pk='vfab plan'
```

### Useful Combinations
```bash
# Add and plan in one step
vfab add design.svg --name "Art" && vfab plan Art

# Quick status check
vfab status && vfab list queue

# Clean and report
vfab queue cleanup --completed && vfab stats summary --today

# Batch operations
for file in *.svg; do vfab add "$file"; done && vfab plan-all
```

### Time-Saving Patterns
```bash
# Template for new projects
project_setup() {
    mkdir -p "$1"/{designs,output,docs}
    cd "$1"
    echo "Project $1 ready for vfab work"
}

# Quick batch add
batch_add() {
    for file in "$1"/*.svg; do
        vfab add "$file" --name "Batch: $(basename "$file" .svg)"
    done
}
```

---

## 📚 Getting Help

### Help Commands
| Command | Purpose |
|---------|---------|
| `vfab --help` | Main help |
| `vfab <command> --help` | Command-specific help |
| `vfab info system` | System information |
| `vfab version` | Version information |

### Common Help Topics
```bash
# Get help for specific areas
vfab add --help          # Job addition
vfab plan --help         # Planning options
vfab plot --help         # Plotting options
vfab config --help       # Configuration
vfab stats --help        # Statistics
```

---

**🎯 Goal:** Keep this reference handy. You'll use these commands daily.

**📚 Related:** [Optimization Presets](optimization-presets.md) for preset selection guide.