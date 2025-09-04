#!/usr/bin/env zsh

default_model=gpt-oss:20b
SCRIPT=$0
default_data_dir=data

model_dir_name() {
    echo "$1" | sed -e 's/:/_/g'
}

default_model_dir_name=$(model_dir_name $default_model)

help() {
    cat <<EOF
Generate Q&A pairs for the healthcare ChatBot.
Usage: $SCRIPT [-h|--help] [-m|--model MODEL] [-o|--output OUT] [-d|--data DIR] 
Where:
-h | --help         Print this message and exit
-m | --model MODEL  Use MODEL instead of the default: $default_model
-o | --output OUT   Where standard output is written. Defaults to stdout.
                    Error messages are written to stderr.
-d | --data DIR     Directory where data files are written. Default: $default_data_dir.
                    The files will actually be written into a subdirectory 
                    based on the model name, by default: $default_model_dir_name

The llm CLI is required. Run "make help-llm" in the project's src directory.
EOF
}

error() {
    do_help=true
    [[ $1 = "--no-help" ]] && shift && do_help=false
    echo "*** ERROR: $@" 1>&2
    $do_help && help 1>&2
    exit 1
}

model="$default_model"
output=
data_dir1="$default_data_dir"
while [[ $# -gt 0 ]]
do
    case $1 in
    -h|--help)
        help
        exit 0
        ;;
    -m|--model)
        shift
        model=$1
        ;;
    -o|--output)
        shift
        output="$1"
        ;;
    -d|--data)
        shift
        data_dir1="$1"
        ;;
    *)
        error "Unrecognized argument $1"
        ;;
    esac
    shift
done

data_dir="$data_dir1/$(model_dir_name $model)"
cat << EOF
$SCRIPT:
Using model: $model
Writing output to $([[ -z $output ]] && echo "stdout" || echo $output)
Writing synthetic data files to $data_dir

EOF

template_name() {
    which_one=$1
    echo "synthetic-q-and-a_patient-chatbot-$which_one"
}

command -v llm > /dev/null || error "The llm CLI is required. Run 'make help-llm' and see https://github.com/simonw/llm"

do_trial() {
    template="$1"
    data_file="$2"
    rm -f "$data_file"
    if [[ -z $NOOP ]]
    then
        llm --template "$template" > "$data_file"
    else
        $NOOP "llm --template $template > $data_file"
    fi
    return $status
}

trial() {
    template=$(template_name "$1")
    data_file="$data_dir/${template}-data.yaml"
    echo "Using template \"$template\" and data output file \"$data_file\""
    if [[ -z $output ]]
    then
        do_trial "$template" "$data_file" "$@" || \
            error --no-help "\"$template\" run had errors and data file $data_file"
    else
        do_trial "$template" "$data_file" "$@" > "$output" || \
            error --no-help "\"$template\" run had errors. See $output and data file $data_file"
    fi
}

[[ -n $output ]] && rm -f "$output"
$NOOP mkdir -p $data_dir
trial "prescription-refills"
trial "non-prescription-refills"

echo "Synthetic data files written to directory: $data_dir"

