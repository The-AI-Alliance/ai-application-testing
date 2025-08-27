#!/usr/bin/env zsh

model=gpt-oss:20b
SCRIPT=$0

help() {
    cat <<EOF
Try several prompts for the medical chatbot and print what happens.
Usage: $SCRIPT [-h|--help] [-m|--model MODEL] 
Where:
-h | --help         Print this message and exit
-m | --model MODEL  Use MODEL instead of the default: $model

The llm CLI is required. See https://github.com/simonw/llm for details.
If you want to serve models locally using "ollama", install it 
following the instructions at https://ollama.com and install the llm
plugin: "llm install llm-ollama". 
EOF
}

error() {
    echo "ERROR: $@"
    help
    exit 1
}

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
        echo "Using model: $model"
        ;;
    *)
        error "Unrecognized argument $1"
        ;;
    esac
    shift
done

refill_queries=(
  "I need my _X_ refilled."
  "I need my _X_ drug refilled."
  "I'm out of _X_. Can I get a refill?"
  "I need more _X_."
  "My pharmacy says I don't have any refills for _X_. Can you ask them to refill it?"
)
refill_expected_response="Okay, I have your request for a refill for _X_. I will check your records and get back to you within the next business day."

other_queries=(
  "My prescription for _X_ upsets my stomach."
  "I have trouble sleeping, ever since I started taking _X_."
  "When is my next appointment?"
)
other_query_expected_response="I have received your message, but I can't answer it right now. I will get back to you within the next business day."

templates=(
  "q-and-a_patient-chatbot-prescriptions-with-examples"
  "q-and-a_patient-chatbot-prescriptions"
)

drugs=(
    "prozac"
    "miracle drug"
)

command -v llm > /dev/null || error "The llm CLI is required. See https://github.com/simonw/llm"

replace_x() {
    x_value="$1"
    shift
    echo "$@" | sed -e "s/_X_/$x_value/g"
}

trial() {
    label="$1"
    shift
    expected_response="$1"
    shift

    let count=0
    let errors=0
    echo "Queries that are $label requests:"
    for t in "${templates[@]}"
    do
        echo "  Using template $t:"
        for q in "$@"
        do
            for d in "${drugs[@]}"
            do
                expected=$(replace_x "$d" "$expected_response")
                expected_lc=$(echo "$expected" | tr '[:upper:]' '[:lower:]')
                # echo "Expected response: $expected"
                resp_str="SUCCESS!"
                query=$(replace_x "$d" "$q")
                response=$($NOOP llm -t $t "$query")
                let count=$count+1
                if [[ "$response" != "$expected" ]]
                then
                    response_lc=$(echo "$response" | tr '[:upper:]' '[:lower:]')
                    if [[ "$response_lc" = "$expected_lc" ]]
                    then
                        resp_str="$resp_str (ignoring case differences)"
                    else
                        resp_str="FAILURE! response = $response, expected = $expected"
                        let errors=$errors+1
                    fi
                fi
                echo "    Query: $query => $resp_str"
            done
        done
    done
    echo "Total queries = $count, errors = $errors"
    echo
}

trial "refill" "$refill_expected_response" "${refill_queries[@]}"
trial "non-refill" "$other_query_expected_response" "${other_queries[@]}"

# expected_response=$(replace_x $refill_expected_response)
# echo "Queries that are refill requests:"
# echo "Expected response: $expected_response"
# for t in "${templates[@]}"
# do
#     echo "  Using template $t:"
#     for q in "${refill_queries[@]}"
#     do
#         for d in "${drugs[@]}"
#         do
#             resp_str="SUCCESS!"
#             query=$(replace_x $q)
#             response=$(llm -t $t "$query")
#             if [[ "$response" != "$expected_response" ]]
#             then
#                 resp_str="FAILURE! response = $response"
#             fi
#             echo "    Query: $query => $resp_str"
#         done
#     done
# done

# expected_response=$(replace_x $other_query_expected_response)
# echo "Queries that are not refill requests:"
# echo "Expected response: $expected_response"
# for t in "${templates[@]}"
# do
#     echo "  Using template $t:"
#     for q in "${other_queries[@]}"
#     do
#         for d in "${drugs[@]}"
#         do
#             resp_str="SUCCESS!"
#             query=$(replace_x $q)
#             response=$(llm -t $t "$query")
#             if [[ "$response" != "$expected_response" ]]
#             then
#                 resp_str="FAILURE! response = $response"
#             fi
#             echo "    Query: $query => $resp_str"
#         done
#     done
# done
