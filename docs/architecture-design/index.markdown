---
layout: default
title: Architecture and Design for Testing
nav_order: 20
has_children: true
---

# Architecture and Design for Testing

This section explores strategies and techniques that can be used to create reliable, repeatable tests for generative AI applications. 

We start with a reminder of general principles that have always applied, like _divide and conquer_ design approaches, then explore what new techniques developers can learn from their data scientist and model building peers.

Each page has a list of ideas we are exploring as _TODO_ items. See also the project [issues](https://github.com/The-AI-Alliance/ai-application-testing/issues){:target="issues"}.

{: .note }
> **NOTE:** Using a [Generative AI Model]({{site.glossaryurl}}/#generative-ai-model) can mean it is managed by the application itself, behind APIs or [Agents]({{site.glossaryurl}}/#agent), or it is used through direct calls to a separate service, like ChatGPT. When discussing models as components, we will often just use _model_ as a shorthand for all these cases.



## Notes about Software Design for Generative AI Applications

The creators of [Test-Driven Development]({{site.glossaryurl}}/#test-driven-development) (TDD) made clear that it is really a _design_ discipline as much as a _testing_ discipline. When you write tests before code, you are in the frame of mind of specifying the expected behavior of what you are about to implement, expressed as tests. The iterative nature of TDD encourages you to make minimally-sufficient and incremental changes as you go.

During this process, the software design decisions you make reflect many perspectives, intuitions, and idioms, all built on years of experience. 

### The Paradigm Shift Required in Your Thinking 

Generative models force new perspectives, intuitions, and idioms, reflecting the unique characteristics of these inherently nondeterministic systems. 

The nondeterminism comes from the inherently probabilistic nature of models. Simplistically, models generate the next most probably &ldquo;element&rdquo, with some randomness to support alternative outputs, such as the next token for language models or the next pixel for image models.

Unfortunately, truly effective testing of models requires some expertise with probabilities and statistics that software developers typically don't require. However, your intuitions are very helpful ...

TODO - more specific details.

### Scope Allowed Inputs and Outputs

Traditional software has well defined interfaces (e.g., APIs) that limit how users invoke services. It may seem paradoxical that constraints are better than no constraints, but this characteristic greatly reduces ambiguities and misunderstanding about behaviors and expectations between the user and the software. In a well-designed interface, the user knows exactly what inputs to provide and the software knows exactly what results to return for a given set of inputs. This greatly simplifies the implementation on both sides of the interface, as no effort is required to deal with ambiguities and poorly-constrained possibilities.

Generative AI Models are effectively _completely open ended_; you can input almost any text you want (often limited only by the length of the query) and you can get almost any response possible in return! From a robust software design perspective, _this is truly a bad idea_, but models have compensating virtues. When they work well, they do a good job interpreting ambiguous human speech, especially from a non-expert, and creating results that accomplish the user's goals. They are very good at generating lots of detailed content in response to relatively little input, especially image generation models.

A vision for [Agent]({{site.glossaryurl}}/#agent)-based (or _agentic_) AI is that models can determine for themselves what external services to invoke and how to invoke them, such as determining the weather forecast requested in a query. This also suggests that models have the potential of offering greater integration resiliency compared to conventional software. For example, if a breaking API change occurs in an external service, an _agentic_ system may be able to determine automatically how the behavior changed and how to compensate for it, freeing the developer of this tedium.

### Useful Techniques

Still, the open ended nature means you should consider ways of constraining allowed inputs and filtering results. 

* **Don't expose the model directly:** Hide the model behind an interface with clear constraints. In many applications, a model might be used as a _universal translator_ of sorts between systems with APIs. The user interface might provide a constrained experience, tailored to a particular use case, and the underlying prompts sent to the model might be carefully engineered (based on experimentation) to optimize the model's results.
* **Filter results heavily:** Make sure the user or downstream systems only see model results that are constrained appropriately. For chatbots, this obviously means filtering out objectionable content. For other systems, it might mean removal of _boilerplate_ text and formatting results in a concise, structured way.

The last section in [Testing Strategies]({{site.baseurl}}/testing-strategies), [From Testing to Tuning]({{site.baseurl}}/testing-strategies/from-testing-to-tuning), discusses how we might rethink testing for AI applications and put more emphasis on tuning the behaviors to align with our goals. This idea would influence architecture and design, as discussed there.

---

After exploring this section on architecture and design, proceed to [Testing Strategies and Techniques]({{site.baseurl}}/testing-strategies)
