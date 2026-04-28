# README for AI Test's Data Directory

The JSONL files in this directory, one per _use case_, fall into two categories:

* _Simple_: Q&A pairs used with `ChatBotSimple` and sometimes `ChatBotAgent`.
* _Agent_: More complex JSON files used with the _agent skills_ implemented in `ChatBotAgent`.

When there are two JSONL files for a use case, for example, `appointments-simple.jsonl` and `appointments-agent.jsonl`, they used with `ChatBotSimple` and `ChatBotAgent`, respectively. If there is only one file, like `others.jsonl`, it is used to for testing both implementations.

## Format for the &ldquo;Simple&rdquo; JSONL Files 

The _simple_ files are adapted from the outputs of the data synthesis and validation tools discussed in the guide. However, quite a few changes have been made reflecting experience working with these data sets, adding additional uses, etc. Hence, this README discusses some important details.

The format used is illustrated with this example from `appointments.jsonl` (nicely formatted...):

```json
{
  "query":   "I need to reschedule my next appointment.",
  "labels":  ["appointment"],
  "actions": ["reschedule"],
  "rating":  5
}
```

We call these _Q&A_ (question and answer) pairs in the guide, but they actually contain a query (question) and expected metadata values corresponding to metadata fields the prompt asks the ChatBot to return. This metadata is used in the tests and in the ChatBot to returned predefined (and hence controlled) responses to the user, rather than returning the generated text, which may contain incorrect information. In other words, we rely on the LLMS to determine the nature of the patient query and some useful information in it (like mentioned prescriptions). In the current form of the ChatBot, we don't rely on the LLM's generated text:

| Expected Metadata Field | Corresponding Response Field | Discussion |
| :---------------------- | :--------------------------- | :--------- |
| `labels`  | `label`   | The response's `label` is expected to be found in the `labels` list. Usually there is just one element in `labels`, but sometimes more than one label is listed when the query is potentially ambiguous. |
| `actions` | `actions` | The response `actions` list should be a subset of the allowed `actions`. |
| `rating`  | _N/A_     | How the _LLM as a Judge_ validation process rated this synthetic example. |

In addition, there are optional fields that may appear in the examples:

| Expected Metadata Field | Corresponding Response Field | Discussion |
| :---------------------- | :--------------------------- | :--------- |
| `reason`        | _N/A_           | Why the judge rated the example the way it did. |
| `prescriptions` | `prescriptions` | List of one or more prescriptions mentioned in the query. |
| `body_parts`    | `body_parts`    | List of one or more body parts mentioned in the query. |
| `vaccines`      | `vaccines`      | List of one or more vaccines mentioned in the query. |

The last three fields only appear in an example JSONL if they are non-empty.

During testing, if the `rating` is below a threshold, the ChatBot result is logged as _low confidence_ and not checked for expected results. The ChatBot is also asked to provide its _confidence_ of the result, which is used similarly during the test.

The `label` returned by the ChatBot should correspond to the use case file name! However, in practice, some queries are ambiguous enough that more than one label would be a reasonable interpretation, which is why `labels` is a list. The first list element is always the name of the use case. So, for example, there are many examples in `prescriptions.jsonl` with the label list `["prescription", "appointment"]`, like this one:

```json
{
  "query":         "Do I need a follow-up appointment for my prescription for ozempic?",
  "labels":        ["prescription","appointment"],
  "actions":       ["inquiry"],
  "prescriptions": ["ozempic"],
  "rating": 5
}
```

You can see from the query that it is reasonable to interpret the query as an appointment or prescription query. It is really both, but at this time we ask the ChatBot to return only one `label`.

## Format for the &ldquo;Agent&rdquo; JSONL Files

TODO

