SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
find .. -type d -name migrations -prune-exec rm -rf {} \; # rm -rf