# Fish completion for ploTTY
complete -c plotty -f
complete -c plotty -n __fish_use_subcommand -a job -d 'Manage plotting jobs'
complete -c plotty -n __fish_use_subcommand -a plot -d 'Plot jobs interactively'
complete -c plotty -n __fish_use_subcommand -a batch -d 'Batch process multiple jobs'
complete -c plotty -n __fish_use_subcommand -a stats -d 'View statistics and analytics'
complete -c plotty -n __fish_use_subcommand -a backup -d 'Backup and restore data'
complete -c plotty -n __fish_use_subcommand -a recovery -d 'Crash recovery operations'
complete -c plotty -n __fish_use_subcommand -a guard -d 'System validation and checks'
complete -c plotty -n __fish_use_subcommand -a config -d 'Configuration management'
complete -c plotty -n __fish_use_subcommand -a logging -d 'Log management'
complete -c plotty -n __fish_use_subcommand -a status -d 'System status information'
complete -c plotty -n __fish_use_subcommand -a --help -d 'Show help'
complete -c plotty -n __fish_use_subcommand -a --version -d 'Show version'
