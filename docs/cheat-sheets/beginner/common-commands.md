# Common Commands Cheat Sheet

**Essential commands reference** - The 20 commands you'll use 90% of the time.

---

## 📋 Job Management

### Add Jobs
```bash
# Basic add
plotty add design.svg

# With custom name
plotty add design.svg --name "My Art"

# With paper size
plotty add design.svg --paper a4 --name "A4 Art"

# Multiple files
plotty add *.svg --name "Batch Job"
```

### List Jobs
```bash
# All jobs
plotty list jobs

# Current queue
plotty list queue

# Job details
plotty info job my_job

# Completed jobs
plotty list jobs --state completed
```

### Remove Jobs
```bash
# Specific job
plotty remove job my_job

# Completed jobs
plotty queue cleanup --state completed

# Old jobs (older than 7 days)
plotty queue cleanup --older-than 7d
```

---

## ⚡ Planning & Plotting

### Plan Jobs
```bash
# Quick planning (fast preset)
plotty plan my_job

# Interactive planning
plotty plan my_job --interactive

# High quality planning
plotty plan my_job --preset hq

# Plan all jobs
plotty plan-all --preset fast
```

### Plot Jobs
```bash
# Plot single job
plotty plot my_job

# Plot all planned jobs
plotty plot-all

# With preview
plotty plot my_job --preview

# With recording
plotty plot my_job --record
```

---

## 🔍 Information & Status

### System Status
```bash
# Quick status
plotty status

# Full system check
plotty check ready

# Device status
plotty check device

# Database status
plotty check database
```

### Job Information
```bash
# Job details
plotty info job my_job

# Time estimation
plotty estimate my_job

# Detailed estimation
plotty estimate my_job --detailed

# Job report
plotty info job my_job --show-report
```

---

## 📊 Statistics & Analytics

### Quick Stats
```bash
# Summary statistics
plotty stats summary

# Today's stats
plotty stats summary --today

# Last 30 days
plotty stats summary --last 30
```

### Detailed Analytics
```bash
# Job statistics
plotty stats jobs --last 30

# Performance metrics
plotty stats performance

# Pen usage
plotty stats pens --last 30
```

---

## 🖊️ Pen & Paper Management

### Pen Management
```bash
# List pens
plotty list pens

# Add pen
plotty add pen --name "Fine Black" --width 0.3 --color "#000000"

# Update pen
plotty update pen 1 --speed-cap 60

# Pen usage
plotty list pens --show-usage
```

### Paper Management
```bash
# List paper types
plotty list paper

# Add paper size
plotty add paper --name "Custom" --width 200 --height 150

# Paper usage
plotty list paper --show-usage
```

---

## 🛠️ Configuration

### Device Configuration
```bash
# View config
plotty config show

# Set device port
plotty config device --port /dev/ttyUSB0

# Set pen positions
plotty config device --pen-up 60 --pen-down 40

# Test device
plotty check device --test-move
```

### General Configuration
```bash
# Interactive setup
plotty setup

# Setup wizard
plotty setup device

# Validate config
plotty config validate
```

---

## 🔄 Recovery & Troubleshooting

### Recovery Commands
```bash
# List recovery options
plotty recovery list

# Resume interrupted job
plotty resume my_job

# Restart job
plotty restart my_job

# Abort stuck job
plotty abort my_job
```

### Diagnostic Commands
```bash
# System information
plotty info system

# Health check
plotty check ready --detailed

# Log files
plotty logs --tail 50

# Test patterns
plotty test pattern --basic
```

---

## 🎯 Quick Reference Patterns

### Daily Workflow
```bash
# Morning setup
plotty check ready
plotty list queue

# Add and plot new design
plotty add new.svg --name "Today's Art"
plotty plan new_art --interactive
plotty plot new_art

# End of day cleanup
plotty queue cleanup --state completed
plotty stats summary --today
```

### Batch Processing
```bash
# Add multiple files
for file in *.svg; do
    plotty add "$file" --name "Batch: $(basename "$file" .svg)"
done

# Plan all
plotty plan-all --preset fast

# Plot all
plotty plot-all
```

### Troubleshooting Sequence
```bash
# When something goes wrong
plotty check ready
plotty status
plotty recovery list
plotty info system
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
plotty abort

# Emergency device reset
plotty check device --reset

# Full system restart
plotty restart
```

**When you're stuck:**
```bash
# Get help for any command
plotty <command> --help

# Full system status
plotty info system

# Check what's running
plotty status --verbose
```

---

## 💡 Pro Tips

**Save time with aliases:**
```bash
# Add to your .bashrc/.zshrc
alias pp='plotty plot'
alias pa='plotty add'
alias pl='plotty list'
alias ps='plotty status'
```

**Useful combinations:**
```bash
# Add and plan in one step
plotty add design.svg --name "Art" && plotty plan Art

# Quick status check
plotty status && plotty list queue

# Clean and report
plotty queue cleanup --completed && plotty stats summary --today
```

---

**🎯 Goal:** Memorize the top 10 commands in the first section. The rest will come naturally as you need them.

**📚 Next:** [Troubleshooting Basics](troubleshooting-basics.md) when things go wrong.