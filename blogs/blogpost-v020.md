# How Can We Test Enterprise AI Applications?

_[Dean Wampler, Ph.D.](mailto:dwampler@thealliance.ai) - IBM and The AI Alliance_

When the AI Alliance started, I became co-leader of the [Trust and Safety Work Group](https://www.aialliance.org/projects#safety), because it was clear that without the ability to trust AI, it would not be widely adopted into enterprise and consumer applications. We have made a lot of progress since then, but another, related blocking issue became apparent to me about a year ago. 

I realized that most of my fellow enterprise software developers and I don't know how to test these applications, because the probabilistic nature of generative AI is new to us. We are accustomed to more deterministic behavior when we design, implement, and test our "pre-AI" code. 

![Developer to AI Expert Spectrum](docs/assets/images/developer-to-AI-expert-spectrum.png "Developer to AI Expert Spectrum")

_**Figure 1:** The spectrum between deterministic and stochastic behavior, and the people accustomed to them!_

So, I started a project we now call [Testing Generative AI Agent Applications](https://the-ai-alliance.github.io/ai-application-testing/) to bridge this gap. It is a "living" guide designed to explore how we can adapt and adopt the evaluation technologies AI experts use for the fine-grained testing of use cases and requirements that we developers must do, in order to be _confident_ in our AI-empowered applications. It also explores the implications for how we design these applications.

Today, I'm pleased to announce version `V0.2.0` of our living guide. While there is much we still need to do, we have added content you can use today to start testing your AI-empowered applications. 

We added a working example that demonstrates how to adapt _benchmark_ techniques to create _unit benchmarks_, the analog of unit tests. Similarly, _integration benchmarks_ and _acceptance benchmarks_ are the analogs of integration tests, which explore interactions between system components, and acceptance tests, which provide the final confirmations that features are _done_.

We show how to use LLMs to synthesize focused data sets for these benchmarks, how to validate this data, and how to think about the results of tests that use this data.

Perhaps most important, we explore design concepts that allow us to reduce the randomness in parts of our applications, while still exploiting AI benefits. We also think about how to discover the AI equivalents of "features", units of functionality that we can implement incrementally and iteratively, as we prefer to do in _Agile Development_.

We show an example of a healthcare ChatBot designed to allow patients to ask questions of their healthcare provider. We show that _frequently asked questions_ (FAQs), like requests for prescription refills, enable simplified, even _deterministic_ handling. Finding the FAQs or equivalents for a domain enables more rapid progress, incrementally developing each one, without the impossible burden of trying to tackle all input-output combinations at once.

Even small large language models (LLMs) can easily interpret the many ways patients might ask for refills. When detected, we can direct the LLM to return a _deterministic_ response. Effectively, it becomes a sophisticated _classifier_. When we know the query's class, we know exactly how to handle it, deterministically and confidently. So, we keep the benefits of an LLM's ability to interpret the many variations of human questions, while enjoying the benefits of deterministic outcomes, at least for use cases like this one. These insights reduce our overall design, implementation, and testing burden. 

We still need to design and test for the many other possible user queries, and learn how to reason about and test the generative replies. We have began this journey, which we will continue in subsequent releases of this guide.

Please [let us know](https://github.com/The-AI-Alliance/ai-application-testing/discussions) what you think and consider [joining us](https://the-ai-alliance.github.io/ai-application-testing/contributing/) on this exploration!

