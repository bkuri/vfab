# Fish completion for ploTTY
complete -c plotty -f

# Main commands
complete -c plotty -n __fish_use_subcommand -a interactive -d 'Start an interactive plot'
complete -c plotty -n __fish_use_subcommand -a optimize -d 'Optimize jobs for plotting'
complete -c plotty -n __fish_use_subcommand -a plan -d 'Plan a job for plotting'
complete -c plotty -n __fish_use_subcommand -a queue -d 'Queue a job for plotting'
complete -c plotty -n __fish_use_subcommand -a resume -d 'Resume interrupted plotting jobs'
complete -c plotty -n __fish_use_subcommand -a restart -d 'Restart job from beginning'
complete -c plotty -n __fish_use_subcommand -a setup -d 'Run setup wizard'
complete -c plotty -n __fish_use_subcommand -a start -d 'Start plotting a job'
complete -c plotty -n __fish_use_subcommand -a plot -d 'Plot a job'
complete -c plotty -n __fish_use_subcommand -a add -d 'Add new files'
complete -c plotty -n __fish_use_subcommand -a check -d 'System and device checking'
complete -c plotty -n __fish_use_subcommand -a info -d 'Status and monitoring commands'
complete -c plotty -n __fish_use_subcommand -a list -d 'List and manage resources'
complete -c plotty -n __fish_use_subcommand -a remove -d 'Remove resources'
complete -c plotty -n __fish_use_subcommand -a stats -d 'Statistics and analytics'
complete -c plotty -n __fish_use_subcommand -a system -d 'System management commands'
complete -c plotty -n __fish_use_subcommand -a --help -d 'Show help'
complete -c plotty -n __fish_use_subcommand -a --version -d 'Show version'

# add subcommands
complete -c plotty -n '__fish_seen_subcommand_from add' -a job -d 'Add a new job'
complete -c plotty -n '__fish_seen_subcommand_from add' -a jobs -d 'Add multiple jobs using pattern'
complete -c plotty -n '__fish_seen_subcommand_from add' -a pen -d 'Add a new pen configuration'
complete -c plotty -n '__fish_seen_subcommand_from add' -a paper -d 'Add a new paper configuration'

# check subcommands
complete -c plotty -n '__fish_seen_subcommand_from check' -a camera -d 'Test camera connectivity'
complete -c plotty -n '__fish_seen_subcommand_from check' -a config -d 'Check configuration'
complete -c plotty -n '__fish_seen_subcommand_from check' -a job -d 'Check job status and guards'
complete -c plotty -n '__fish_seen_subcommand_from check' -a ready -d 'Check overall system readiness'
complete -c plotty -n '__fish_seen_subcommand_from check' -a self -d 'Run comprehensive self-tests'
complete -c plotty -n '__fish_seen_subcommand_from check' -a servo -d 'Test servo motor operation'
complete -c plotty -n '__fish_seen_subcommand_from check' -a timing -d 'Test device timing'

# info subcommands
complete -c plotty -n '__fish_seen_subcommand_from info' -a system -d 'Show overall system status'
complete -c plotty -n '__fish_seen_subcommand_from info' -a tldr -d 'Quick overview of system and queue'
complete -c plotty -n '__fish_seen_subcommand_from info' -a job -d 'Show detailed information about a specific job'
complete -c plotty -n '__fish_seen_subcommand_from info' -a reset -d 'Reset the current session'
complete -c plotty -n '__fish_seen_subcommand_from info' -a session -d 'Show current session information'
complete -c plotty -n '__fish_seen_subcommand_from info' -a queue -d 'Show job queue status'

# list subcommands
complete -c plotty -n '__fish_seen_subcommand_from list' -a pens -d 'List available pen configurations'
complete -c plotty -n '__fish_seen_subcommand_from list' -a papers -d 'List available paper configurations'
complete -c plotty -n '__fish_seen_subcommand_from list' -a presets -d 'List available plot presets'
complete -c plotty -n '__fish_seen_subcommand_from list' -a jobs -d 'List all jobs in workspace'
complete -c plotty -n '__fish_seen_subcommand_from list' -a guards -d 'List available guards'

# remove subcommands
complete -c plotty -n '__fish_seen_subcommand_from remove' -a pen -d 'Remove a pen configuration'
complete -c plotty -n '__fish_seen_subcommand_from remove' -a paper -d 'Remove a paper configuration'
complete -c plotty -n '__fish_seen_subcommand_from remove' -a job -d 'Remove a job'
complete -c plotty -n '__fish_seen_subcommand_from remove' -a jobs -d 'Remove multiple jobs with filtering'

# stats subcommands
complete -c plotty -n '__fish_seen_subcommand_from stats' -a summary -d 'Show overall statistics summary'
complete -c plotty -n '__fish_seen_subcommand_from stats' -a jobs -d 'Show job-related statistics'
complete -c plotty -n '__fish_seen_subcommand_from stats' -a performance -d 'Show performance metrics and trends'

# system subcommands
complete -c plotty -n '__fish_seen_subcommand_from system' -a export -d 'Export and backup operations'
complete -c plotty -n '__fish_seen_subcommand_from system' -a import -d 'Import and restore operations'
complete -c plotty -n '__fish_seen_subcommand_from system' -a logs -d 'Log management commands'
complete -c plotty -n '__fish_seen_subcommand_from system' -a stats -d 'Statistics and analytics'

# Common options for plot commands
complete -c plotty -n '__fish_seen_subcommand_from start; or __fish_seen_subcommand_from plot' -l preset -s p -d 'Plot preset (fast, safe, preview, detail, draft)' -x
complete -c plotty -n '__fish_seen_subcommand_from start; or __fish_seen_subcommand_from plot' -l port -d 'Device port' -x
complete -c plotty -n '__fish_seen_subcommand_from start; or __fish_seen_subcommand_from plot' -l model -d 'Device model' -x
complete -c plotty -n '__fish_seen_subcommand_from start; or __fish_seen_subcommand_from plot' -l apply -d 'Start plotting'
complete -c plotty -n '__fish_seen_subcommand_from start; or __fish_seen_subcommand_from plot' -l dry-run -d 'Preview plotting without moving pen'

# optimize options
complete -c plotty -n '__fish_seen_subcommand_from optimize' -l preset -s p -d 'Optimization preset (fast, default, hq)' -x
complete -c plotty -n '__fish_seen_subcommand_from optimize' -l digest -s d -d 'Digest level for AxiDraw acceleration (0-2)' -x
complete -c plotty -n '__fish_seen_subcommand_from optimize' -l apply -d 'Actually perform optimization'

# plan options
complete -c plotty -n '__fish_seen_subcommand_from plan' -l pen -s p -d 'Default pen specification' -x
complete -c plotty -n '__fish_seen_subcommand_from plan' -l interactive -s i -d 'Interactive layer planning'

# interactive options
complete -c plotty -n '__fish_seen_subcommand_from interactive' -l port -d 'Device port' -x
complete -c plotty -n '__fish_seen_subcommand_from interactive' -l model -d 'Device model' -x
complete -c plotty -n '__fish_seen_subcommand_from interactive' -l units -d 'Coordinate units (inches, millimeters, centimeters)' -x

# resume options
complete -c plotty -n '__fish_seen_subcommand_from resume' -l apply -d 'Apply resume changes'

# restart options
complete -c plotty -n '__fish_seen_subcommand_from restart' -l apply -d 'Apply restart changes'
complete -c plotty -n '__fish_seen_subcommand_from restart' -l now -d 'Move job to front of queue'
complete -c plotty -n '__fish_seen_subcommand_from restart' -l json -d 'Output in JSON format'

# Global export options for info and stats commands
complete -c plotty -n '__fish_seen_subcommand_from info; or __fish_seen_subcommand_from stats' -l json -d 'Export as JSON'
complete -c plotty -n '__fish_seen_subcommand_from info; or __fish_seen_subcommand_from stats' -l csv -d 'Export as CSV'
