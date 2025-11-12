# Command Line Reference Cheat Sheet

**All commands at a glance** - Quick lookup for any ploTTY command.

---

## 🧭 Quick Navigation
- **New to ploTTY?** [Daily Quick Start](../beginner/daily-quickstart.md)
- **Need command examples?** [Common Commands](../beginner/common-commands.md)
- **Configuration options?** [Configuration Reference](configuration.md)
- **Optimization presets?** [Optimization Presets](optimization-presets.md)

---

## 📋 Core Commands

### Job Management
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty add <file>` | Add new job | `plotty add design.svg` |
| `plotty list jobs` | List all jobs | `plotty list jobs --state completed` |
| `plotty info job <name>` | Job details | `plotty info job my_art` |
| `plotty remove job <name>` | Remove job | `plotty remove job old_job` |

### Planning & Plotting
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty plan <job>` | Plan job | `plotty plan my_art --interactive` |
| `plotty plan-all` | Plan all jobs | `plotty plan-all --preset fast` |
| `plotty plot <job>` | Plot job | `plotty plot my_art --record` |
| `plotty plot-all` | Plot all jobs | `plotty plot-all --monitor` |

### Status & Information
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty status` | Current status | `plotty status --verbose` |
| `plotty check ready` | System check | `plotty check ready --detailed` |
| `plotty list queue` | Current queue | `plotty list queue --watch` |
| `plotty estimate <job>` | Time estimate | `plotty estimate my_art --detailed` |

---

## 🖊️ Resource Management

### Pen Management
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty list pens` | List all pens | `plotty list pens --show-usage` |
| `plotty add pen` | Add new pen | `plotty add pen --name "Fine Black" --width 0.3` |
| `plotty update pen <id>` | Update pen | `plotty update pen 1 --speed-cap 60` |
| `plotty remove pen <id>` | Remove pen | `plotty remove pen 5` |

### Paper Management
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty list paper` | List paper types | `plotty list paper --show-stock` |
| `plotty add paper` | Add paper size | `plotty add paper --name "A4" --width 210 --height 297` |
| `plotty update paper <name>` | Update paper | `plotty update paper "A4" --stock-count 50` |
| `plotty remove paper <name>` | Remove paper | `plotty remove paper "Old Size"` |

---

## ⚙️ Configuration

### Device Configuration
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty config show` | Show config | `plotty config show --device` |
| `plotty config device` | Device settings | `plotty config device --port /dev/ttyUSB0` |
| `plotty setup` | Interactive setup | `plotty setup --device-only` |
| `plotty check device` | Test device | `plotty check device --test-move` |

### General Configuration
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty config validate` | Validate config | `plotty config validate --strict` |
| `plotty config reset` | Reset config | `plotty config reset --device-only` |
| `plotty info system` | System info | `plotty info system --detailed` |

---

## 📊 Statistics & Analytics

### Basic Statistics
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty stats summary` | Summary stats | `plotty stats summary --last 30` |
| `plotty stats jobs` | Job statistics | `plotty stats jobs --by-client` |
| `plotty stats performance` | Performance | `plotty stats performance --pen-usage` |
| `plotty stats pens` | Pen usage | `plotty stats pens --last 90` |

### Advanced Analytics
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty analyze queue` | Queue analysis | `plotty analyze queue --efficiency` |
| `plotty analyze pens` | Pen analysis | `plotty analyze pens --wear-patterns` |
| `plotty analyze production` | Production analysis | `plotty analyze production --cost-analysis` |

---

## 🔄 Recovery & Troubleshooting

### Recovery Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty recovery list` | List recovery options | `plotty recovery list --all` |
| `plotty resume <job>` | Resume job | `plotty resume interrupted_job` |
| `plotty restart <job>` | Restart job | `plotty restart failed_job` |
| `plotty abort <job>` | Abort job | `plotty abort stuck_job` |

### Diagnostic Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty check database` | Database check | `plotty check database --verify` |
| `plotty check camera` | Camera check | `plotty check camera --test-url` |
| `plotty logs` | View logs | `plotty logs --tail 100` |
| `plotty test pattern` | Test pattern | `plotty test pattern --basic` |

---

## 🧹 Maintenance & Cleanup

### Queue Management
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty queue cleanup` | Clean queue | `plotty queue cleanup --completed --older-than 7d` |
| `plotty queue optimize` | Optimize queue | `plotty queue optimize --global-pen-order` |
| `plotty queue backup` | Backup queue | `plotty queue backup --file queue_backup.json` |

### System Maintenance
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty restart` | Restart ploTTY | `plotty restart --queue-only` |
| `plotty backup data` | Backup data | `plotty backup data --full` |
| `plotty cleanup workspace` | Clean workspace | `plotty cleanup workspace --older-than 30d` |

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
plotty plan simple_design --preset fast

# Complex art - use hq
plotty plan complex_art --preset hq

# Already optimized - use none
plotty plan optimized_design --preset none

# Let ploTTY decide
plotty plan design --auto-preset --target-time 10m
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
plotty plan multi_pen_art --interactive

# Custom pen mapping
plotty plan art --pen-mapping "3,1,4,2"

# Global pen optimization
plotty plan-all --optimize-pens --global-pen-order
```

---

## 📹 Camera & Recording

### Camera Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `plotty check camera` | Test camera | `plotty check camera --test-stream` |
| `plotty config camera` | Camera settings | `plotty config camera --url http://...` |
| `plotty record <name>` | Manual recording | `plotty record test --seconds 30` |

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
| `plotty abort` | Immediate stop | Plotter going crazy |
| `plotty emergency-stop` | Hardware stop | Software not responding |
| `plotty reset device` | Reset device | Device unresponsive |
| `plotty restart` | Full restart | System hung |

### Recovery Sequence
```bash
# 1. Immediate stop
plotty abort

# 2. Check status
plotty status

# 3. List recovery options
plotty recovery list

# 4. Apply recovery
plotty resume <job>  # or restart, or remove
```

---

## 💡 Pro Tips & Shortcuts

### Command Shortcuts
```bash
# Common aliases to add to .bashrc/.zshrc
alias pp='plotty plot'
alias pa='plotty add'
alias pl='plotty list'
alias ps='plotty status'
alias pr='plotty resume'
alias pk='plotty plan'
```

### Useful Combinations
```bash
# Add and plan in one step
plotty add design.svg --name "Art" && plotty plan Art

# Quick status check
plotty status && plotty list queue

# Clean and report
plotty queue cleanup --completed && plotty stats summary --today

# Batch operations
for file in *.svg; do plotty add "$file"; done && plotty plan-all
```

### Time-Saving Patterns
```bash
# Template for new projects
project_setup() {
    mkdir -p "$1"/{designs,output,docs}
    cd "$1"
    echo "Project $1 ready for ploTTY work"
}

# Quick batch add
batch_add() {
    for file in "$1"/*.svg; do
        plotty add "$file" --name "Batch: $(basename "$file" .svg)"
    done
}
```

---

## 📚 Getting Help

### Help Commands
| Command | Purpose |
|---------|---------|
| `plotty --help` | Main help |
| `plotty <command> --help` | Command-specific help |
| `plotty info system` | System information |
| `plotty version` | Version information |

### Common Help Topics
```bash
# Get help for specific areas
plotty add --help          # Job addition
plotty plan --help         # Planning options
plotty plot --help         # Plotting options
plotty config --help       # Configuration
plotty stats --help        # Statistics
```

---

**🎯 Goal:** Keep this reference handy. You'll use these commands daily.

**📚 Related:** [Optimization Presets](optimization-presets.md) for preset selection guide.