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

warning() {
    echo "*** WARNING: $@" 1>&2
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

expected_lines() {
    expected_label="$1"
    data_file="$2"
    let nlines=$(grep --count --invert-match "\"label\": \"$expected_label\"" "$data_file")
    [[ $nlines = 0 ]] && return 0
    warning "$nlines lines in $data_file do not have expected label $expected_label!"
    warning "The labels may be correct for the actual question generated, so please check the following:"
    grep --invert-match "\"label\": \"$expected_label\"" "$data_file" | while read line
    do
        warning "  $line"
    done
    return 1
}

do_trial() {
    template="$1"
    expected_label="$2"
    data_file="$3"
    rm -f "$data_file"
    if [[ -z $NOOP ]]
    then
        llm --template "$template" > "$data_file"
        let stat=$status
        echo "$(grep --count "\"question\":" $data_file) Q&A pairs generated"
        # Currently, we don't return a "bad" status from expected_lines...
        expected_lines "$expected_label" "$data_file"
    else
        $NOOP "llm --template $template > $data_file"
        let stat=0
    fi
    return $stat
}

trial() {
    template=$(template_name "$1")
    data_file="$data_dir/${template}-data.yaml"
    expected_label="$2"
    cat <<EOF
Using:
  Template: $template
  Expected label: $expected_label
  Data output file: $data_file
EOF
    if [[ -z $output ]]
    then
        do_trial "$template" "$expected_label" "$data_file" "$@" || \
            error --no-help "\"$template\" run had errors and data file $data_file"
    else
        do_trial "$template" "$expected_label" "$data_file" "$@" >> "$output" || \
            error --no-help "\"$template\" run had errors. See $output and data file $data_file"
    fi
}

[[ -n $output ]] && rm -f "$output"
$NOOP mkdir -p $data_dir
trial "prescription-refills" "refill"
trial "non-prescription-refills" "other"
trial "emergency" "emergency"

echo "Synthetic data files written to directory: $data_dir"

