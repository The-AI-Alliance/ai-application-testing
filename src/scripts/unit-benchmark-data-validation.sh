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
Evaluate the quality of generated Q&A pairs for the healthcare ChatBot.
Usage: $SCRIPT [-h|--help] [-m|--model MODEL] [-o|--output OUT] [-d|--data DIR] 
Where:
-h | --help         Print this message and exit
-m | --model MODEL  Use MODEL instead of the default: $default_model
-o | --output OUT   Where standard output is written. Defaults to stdout.
                    Error messages are written to stderr.
-d | --data DIR     Directory where synthetic data files are found and the validation
                    results will be written. Default: $default_data_dir.
                    A subdirectory based on the model name is actually used, 
                    by default: $default_model_dir_name
                    All the synthetic data files are read and each answer is 
                    evaluated against the corresponding question.

Summary statistics are written to stdout (or the value passed for --output).
The llm CLI is required. Run "make help-llm" in the project's src directory.
The jq CLI is required. Run "make help-jq" in the project's src directory.
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
Reading synthetic data files from $data_dir 
and writing analysis to the same directory.

EOF

command -v llm > /dev/null || error "The llm CLI is required. Run 'make help-llm' and see https://github.com/simonw/llm"
command -v jq  > /dev/null || error "The jq CLI is required. Run 'make help-jq' and see https://jqlang.org"

do_validate() {
    data_file="$1"
    shift
    validation_file="$1"
    shift
    rm -f "$validation_file"
    template="synthetic-q-and-a_patient-chatbot-data-validation"
    if [[ -z $NOOP ]]
    then
        jq -c '{question: .question, label: .answer.label}' "$data_file" | while read line
        do
            #echo "llm --template $template $line >> $validation_file"
            llm --template "$template" "$line" >> "$validation_file"
        done
    else
        $NOOP "llm --template $template $line"
    fi
    return 0
}

validate() {
    data_file="$1"
    shift
    validation_file=${data_file:r}-validation.yaml  # :r removes the extension...
    echo "Reading data file: $data_file, writing validation file $validation_file"
    if [[ -z $output ]]
    then
        do_validate $name_len "$data_file" "$validation_file" || \
            error --no-help "\"$data_file\" validation had errors and $validation_file"
    else
        do_validate $name_len "$data_file" "$validation_file" >> "$output" || \
            error --no-help "\"$data_file\" validation had errors. See $output and $validation_file"
    fi
}

[[ -n $output ]] && rm -f "$output"
data_files=()
for data_file in $data_dir/*.yaml
do
    [[ "$data_file" =~ "-validation.yaml" ]] && continue  # skip old validation files!
    data_files+=( "$data_file" )
    validate "$data_file"
done

# Print summary statistics:

print_stats_for_file() {
    let name_len=$1
    shift
    data_file="$1"
    shift
    validation_file=${data_file:r}-validation.yaml  # :r removes the extension...

    declare -A ratings
    for i in {1..5}
    do
        ratings[$i]=0
    done
    let count=0
    # toss errors for empty lines, written to stderr.
    jq -c '.rating' "$validation_file" 2> /dev/null | while read rating
    do
        let count=$count+1
        let rat=$ratings[$rating]+1 
        ratings[$rating]=$rat
    done

    dfile="${data_file:t}:"  # drop the directory prefix, leaving the file name "tail".
    printf "%-${name_len}s  |  %3d  |  %3d  |  %3d  |  %3d  |  %3d  |  %3d  |" \
        $dfile $ratings[1] $ratings[2] $ratings[3] $ratings[4] $ratings[5] $count
    echo

    for k v in ${(kv)ratings}
    do
        let i=$k
        [[ $i -ge 1 ]] && [[ $i -le 5 ]] && continue
        warning "There are ratings outside 1-5: $k => $v"
    done
}

print_all_stats() {
    let name_len=85  # a hack...

    printf "%-${name_len}s  |  %3d  |  %3d  |  %3d  |  %3d  |  %3d  | Total |" "Files:" 1  2  3  4  5 
    echo
    printf "%-${name_len}s  |-------|-------|-------|-------|-------|-------|" "------" 
    echo

    for data_file in "$@"
    do
        print_stats_for_file $name_len "$data_file"
    done

    printf "%-${name_len}s  |-------|-------|-------|-------|-------|-------|" "------" 
    echo
}

if [[ -z $output ]]
then
    print_all_stats "${data_files[@]}"
else
    print_all_stats "${data_files[@]}" >> "$output"
fi

