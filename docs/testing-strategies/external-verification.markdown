---
layout: default
title: External Tool Verification
nav_order: 330
parent: Testing Strategies and Techniques
has_children: false
---

# External Tool Verification

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

In [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/), we explored using LLMs to validate the quality of synthetic benchmark data, and generative responses during both tests and production runs responses. Fortunately, there are many scenarios where we can leverage non-AI tools during production runs to generate more precise answers, as well as use them to evaluate synthesized data for tests and generated responses during test runs. This chapter builds on the discussion we started in [Bring in the Experts]({{site.baseurl}}/arch-design/component-design/#bring-in-the-experts-ie-other-services), about leveraging non-AI tools, in the [Component Design]({{site.baseurl}}/arch-design/component-design/) chapter.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Many non-AI tools are much better than generative AI tools at doing particular tasks, especially where precise, accurate, and deterministic answers are feasible and necessary.
> 2. These tools be used as part of an [Agentic]({{site.glossaryurl}}/#agent){:target="_glossary"} architecture to maximize the performance of AI applications. They can also be used to support validation of test data and the responses during test runs.

When interest in generative AI exploded after the unveiling of ChatGPT, it become quickly apparently that LLMs are better at some tasks than others, and other kinds of tools that predate generative AI are superior choices to perform many tasks. This led to application design patterns like [Retrieval-Augmented Generation]({{site.glossaryurl}}/#retrieval-augmented-generation){:target="_glossary"} (RAG) and [Agents]({{site.glossaryurl}}/#agent){:target="_glossary"}. 

In RAG, knowledge relevant to a prompt is retrieved and sent with the prompt as part of the [Context]({{site.glossaryurl}}/#context){:target="_glossary"} during inference invocations. This helps the model generate more accurate responses. Uses include sourcing information about news events that occurred after a model was trained, so the model can generate relevant responses, and retrieval of proprietary information with details needed for effective responses, for example a ChatBot that assists an aviation repair technician can query relevant repair manuals, service bulletins, and logs of past repair sessions.

Agentic systems extend this data-retrieval model to more general tool invocations, such as web searches, with the additional enhancement that LLMs perform an &ldquo;orchestration&rdquo; role of determining from the prompt what kinds of information to gather from tools, which tools to invoke to get the information, invoking those tools, and formulating a response based on the tool replies. The process might also include automatic invocation of actions on behalf of the user.

We are interested in using such tools in a testing context, to validate synthetic data and to evaluate model or application outputs during tests.

## Using External Tools

First, let's consider the &ldquo;mechanics&rdquo; of using external tools.

### How to Invoke Tools

To use any tool, one option is to hard-code invoking it and doing some ad hoc processing of the response. For example, in a code generation application, the generated code can be passed to a parser for analysis. If the analysis succeeds, the code is used as is, but if the analysis fails (i.e., the code has syntax errors), then the user is presented with the error output and asked if she wants to fix the errors herself or have the LLM try fixing the code or generating new code.

The [Agent]({{site.glossaryurl}}/#agent){:target="_glossary"} design pattern emerged to lean on LLMs to eliminate these manual steps of writing code to integrate tools, deciding when to invoke them, doing the invocation, and processing the results. Hence, agents handle this integration automatically with greater flexibility and more dynamic flexibility, depending on the application use cases and prompts received. 

### A Variation of LLM as a Judge?

In the context of checking the quality of test data or inference responses during tests, if an LLM is used to interpret the analysis done by the tools, then this implementation of external tool verification can be considered a variation of [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/). Instead of relying on the LLM's ability to judge by itself, the LLM is used to interpret the analysis of other tools, in order to determine a judgement.

### Another Way of Generating Test Data?

If we are using external tools to validate test data, should we use them to generate the data in the first place? We would replace calls to an LLM to synthesize data with calls to an agent system instead.

For our ChatBot, if the patient reports experiencing some symptoms, we could query a database of known symptoms and possible causes. We will investigate this idea, too.

## Example Tools

Let's explore some example tools.

### Code Generation

Generated code can be checked for quality and validity and, in some cases, automatically modified into a more desirable form. For example:

* Use a parser or compiler to verify the syntax is valid.
  * For languages like Python with optional type hints, run the type checker, too.
* Execute the code (in a safe, sand boxed environment!) to verify it is logically correct. If tests already exist for the generated code (see [Test-Driven Development]({{site.glossaryurl}}/#test-driven-development){:target="_glossary"}), verify the generated code allows the tests to pass.
* Scan for conformance to project code formatting conventions.
* Check for excessive complexity, e.g., using [cyclomatic complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity){:target="_wikipedia"}.
* Scan for security vulnerabilities. For example, check that the code only uses allowed third-party libraries and allowed versions of them, e.g., those libraries approved by the organization and versions that have no known vulnerabilities.

### Data Stores

This is the RAG pattern, but possibly generalized. As discussed in the [RAG glossary entry]({{site.glossaryurl}}/#retrieval-augmented-generation){:target="_glossary"} reference data &ldquo;chunks&rdquo; are encoded into _vectors_ with a similarity metric. At inference time, prompts are similarly encoded to find and return _nearest neighbor_ reference chunks, so the extra context data returned is more likely to be the most relevant for the prompt.

Generalizing this approach in a typical [Agent]({{site.glossaryurl}}/#agent){:target="_glossary"} implementation, any data store of domain-relevant or other data can be queried and interpreted by an LLM for the desired use. In this case, we might use such data to judge the accuracy or utility of synthesized data or responses from inference during test or production runs.

### Planning

Planning is a common technique used in industrial applications. Examples include designing and optimizing assembly lines, determining near-optimal routing, e.g., for package delivery and moving goods around storage facilities or factories, and other purposes.

AI-generated plans can be checked against digital simulations of these scenarios. Why not just use the digital simulation in the first place? This is preferable, but in many cases the model might produce candidate results faster, while the simulation might provide fast verification, thereby providing overall time and resource savings.

### Reasoning, Logic, and Other Mathematics

Various tools exist to perform reasoning or perform and verify logical proofs and other mathematical deductions, etc.

### Science

Models are sometimes used to generate new ideas for certain research problems, which can then be validated experimentally or through software simulations.

For example, protein structure models can generate new, candidate molecules for various purposes. The results can be compared to experimental data and software simulation models (models used in the general sense of the word). Candidate molecules can be synthesized to verify the have the desired properties.

Like for planning, sometimes a model can generate candidate ideas faster than running a simulation, but the simulation can be used to quickly check the validity and utility of the ideas generated.

### Web Search

Tools that perform a conventional web search about a topic provide the same utility as they do when used by people. However, tool-based web searches have the same drawbacks, too. Care is required to validate the veracity of the results or at least the trustworthiness of the sources found. 

## Using External Agents to Generate and Validate Healthcare ChatBot Synthetic Data

{: .todo}
> **TODO:** 
> 
> We intend to provide a complete example of external tool use for creating and validating data sets for the ChatBot application. See issues [#30]({{site.gh_edit_repository}}/issues/30){:target="_blank"} and [#24]({{site.gh_edit_repository}}/issues/24){:target="_blank"}. Here we sketch a possible approach.

If you try some of the [generated example queries]({{site.gh_edit_repository}}/tree/main/src/data/examples/){:target="examples"}, you will see that often the replies generated are quite good, suitable for sharing with a patient. Unfortunately, not all of them are satisfactory and there is potentially-high risk if a poor response is given to a patient. 

The AI Alliance project [Deep Research Agent for Applications](https://the-ai-alliance.github.io/deep-research-agent-for-applications/){:target="draa"} (DRAA) provides three example applications, one of which is a medical tool that accepts a user query about a medical condition or pharmaceutical, then queries reputable sources for up-to-date information. 

One way to enhance the quality of synthetic Q&A pairs would be to use an LLM to generate Q&A pairs, as we have been doing, then verify the quality of the answers by reformatting them as queries to the DRAA medical application, which would be asked to judge the Q&A pairs. This is similar to LLM as a Judge, but since DRAA is engineered to use reputable resources for expert opinion, not just rely on a model's judgement, it should be a more reliable judge than an LLM alone.

Keep in mind that agent systems, like the DRAA application, usually have significantly higher overhead compared to &ldquo;plain&rdquo; LLM inference. This will likely rule out their use during _live_ sessions with real users, whereas other external tools may operate fast enough to be used in such contexts.

Also, this approach isn't useful for all possible Q&A pairs. The companion ChatBot application has Q&A pairs for more use cases than we discuss in this guide. An example is queries related to appointments, such as asking to reschedule an appointment, asking if a visit is necessary for some purpose, etc. Other example queries relate to paying bills. Obviously, it wouldn't make sense to validate these Q&A pairs with a research-oriented tool like DRAA. Fortunately, these scenarios are sufficiently generic and &ldquo;mainstream&rdquo; that a regular LLM as a Judge approach is sufficient.

## Experiments to Try

{: .todo}
> **TODO:** 
> 
> We will expand this section once the working example is provided.

## What's Next?

Review the [highlights](#highlights) summarized above, then proceed to [Statistical Evaluation]({{site.baseurl}}/testing-strategies/statistical-evaluation/).

---
