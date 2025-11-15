# Common Commands Cheat Sheet

**Essential commands reference** - The 20 commands you'll use 90% of the time.

---

## 📋 Job Management

### Add Jobs
```bash
# Basic add
vfab add design.svg

# With custom name
vfab add design.svg --name "My Art"

# With paper size
vfab add design.svg --paper a4 --name "A4 Art"

# Multiple files
vfab add *.svg --name "Batch Job"
```

### List Jobs
```bash
# All jobs
vfab list jobs

# Current queue
vfab list queue

# Job details
vfab info job my_job

# Completed jobs
vfab list jobs --state completed
```

### Remove Jobs
```bash
# Specific job
vfab remove job my_job

# Completed jobs
vfab queue cleanup --state completed

# Old jobs (older than 7 days)
vfab queue cleanup --older-than 7d
```

---

## ⚡ Planning & Plotting

### Plan Jobs
```bash
# Quick planning (fast preset)
vfab plan my_job

# Interactive planning
vfab plan my_job --interactive

# High quality planning
vfab plan my_job --preset hq

# Plan all jobs
vfab plan-all --preset fast
```

### Plot Jobs
```bash
# Plot single job
vfab plot my_job

# Plot all planned jobs
vfab plot-all

# With preview
vfab plot my_job --preview

# With recording
vfab plot my_job --record
```

---

## 🔍 Information & Status

### System Status
```bash
# Quick status
vfab status

# Full system check
vfab check ready

# Device status
vfab check device

# Database status
vfab check database
```

### Job Information
```bash
# Job details
vfab info job my_job

# Time estimation
vfab estimate my_job

# Detailed estimation
vfab estimate my_job --detailed

# Job report
vfab info job my_job --show-report
```

---

## 📊 Statistics & Analytics

### Quick Stats
```bash
# Summary statistics
vfab stats summary

# Today's stats
vfab stats summary --today

# Last 30 days
vfab stats summary --last 30
```

### Detailed Analytics
```bash
# Job statistics
vfab stats jobs --last 30

# Performance metrics
vfab stats performance

# Pen usage
vfab stats pens --last 30
```

---

## 🖊️ Pen & Paper Management

### Pen Management
```bash
# List pens
vfab list pens

# Add pen
vfab add pen --name "Fine Black" --width 0.3 --color "#000000"

# Update pen
vfab update pen 1 --speed-cap 60

# Pen usage
vfab list pens --show-usage
```

### Paper Management
```bash
# List paper types
vfab list paper

# Add paper size
vfab add paper --name "Custom" --width 200 --height 150

# Paper usage
vfab list paper --show-usage
```

---

## 🛠️ Configuration

### Device Configuration
```bash
# View config
vfab config show

# Set device port
vfab config device --port /dev/ttyUSB0

# Set pen positions
vfab config device --pen-up 60 --pen-down 40

# Test device
vfab check device --test-move
```

### General Configuration
```bash
# Interactive setup
vfab setup

# Setup wizard
vfab setup device

# Validate config
vfab config validate
```

---

## 🔄 Recovery & Troubleshooting

### Recovery Commands
```bash
# List recovery options
vfab recovery list

# Resume interrupted job
vfab resume my_job

# Restart job
vfab restart my_job

# Abort stuck job
vfab abort my_job
```

### Diagnostic Commands
```bash
# System information
vfab info system

# Health check
vfab check ready --detailed

# Log files
vfab logs --tail 50

# Test patterns
vfab test pattern --basic
```

---

## 🎯 Quick Reference Patterns

### Daily Workflow
```bash
# Morning setup
vfab check ready
vfab list queue

# Add and plot new design
vfab add new.svg --name "Today's Art"
vfab plan new_art --interactive
vfab plot new_art

# End of day cleanup
vfab queue cleanup --state completed
vfab stats summary --today
```

### Batch Processing
```bash
# Add multiple files
for file in *.svg; do
    vfab add "$file" --name "Batch: $(basename "$file" .svg)"
done

# Plan all
vfab plan-all --preset fast

# Plot all
vfab plot-all
```

### Troubleshooting Sequence
```bash
# When something goes wrong
vfab check ready
vfab status
vfab recovery list
vfab info system
```

---

## 📋 Command Options Quick Reference

### Common Flags
| Flag | Meaning | Example |
|------|---------|---------|
| `--name` | Custom job name | `--name "My Art"` |
| `--paper` | Paper size | `--paper a4` |
| `--preset` | Optimization level | `--preset hq` |
| `--interactive` | Interactive mode | `--interactive` |
| `--dry-run` | Preview only | `--dry-run` |
| `--help` | Show help | `--help` |

### Paper Sizes
| Size | Command |
|------|---------|
| A4 | `--paper a4` |
| A3 | `--paper a3` |
| US Letter | `--paper letter` |
| Custom | `--paper 200x150` |

### Optimization Presets
| Preset | Speed | Quality | Use Case |
|--------|-------|---------|----------|
| `fast` | ⚡ Fast | ✅ Good | Simple designs, tests |
| `default` | 🚶 Medium | ✨ Better | Most designs |
| `hq` | 🐌 Slow | 💎 Best | Complex art, final prints |
| `none` | ⚡ Instant | ❌ None | Pre-optimized files |

---

## 🚨 Emergency Commands

**When plotter goes crazy:**
```bash
# IMMEDIATELY STOP
vfab abort

# Emergency device reset
vfab check device --reset

# Full system restart
vfab restart
```

**When you're stuck:**
```bash
# Get help for any command
vfab <command> --help

# Full system status
vfab info system

# Check what's running
vfab status --verbose
```

---

## 💡 Pro Tips

**Save time with aliases:**
```bash
# Add to your .bashrc/.zshrc
alias pp='vfab plot'
alias pa='vfab add'
alias pl='vfab list'
alias ps='vfab status'
```

**Useful combinations:**
```bash
# Add and plan in one step
vfab add design.svg --name "Art" && vfab plan Art

# Quick status check
vfab status && vfab list queue

# Clean and report
vfab queue cleanup --completed && vfab stats summary --today
```

---

**🎯 Goal:** Memorize the top 10 commands in the first section. The rest will come naturally as you need them.

**📚 Next:** [Troubleshooting Basics](troubleshooting-basics.md) when things go wrong.