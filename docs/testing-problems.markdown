---
layout: default
title: Testing Problems
nav_order: 10
has_children: false
---

# Testing Problems Caused by Generative AI Nondeterminism 

Let's first review why [Determinism]({{site.glossaryurl}}/#determinism){:target="_glossary"} is an important concept in software development, then discuss how the use of [Generative AI Models]({{site.glossaryurl}}/#generative-ai-model){:target="_glossary"} makes this difficult. If you have a strong background in conventional software testing, you might skip the first section and go to [How Generative AI Changes This Picture](#how-generative-ai-changes-this-picture).

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Traditional software is mostly [Deterministic]({{site.glossaryurl}}/#determinism){:target="_glossary"}. This makes it much easier to reason about its behavior and to write repeatable, reliable tests. This is a central, enabling assumption made in software development.
> 1. [Generative AI Model]({{site.glossaryurl}}/#generative-ai-model){:target="_glossary"} outputs are [Stochastic]({{site.glossaryurl}}/#stochastic){:target="_glossary"}, governed by a [Random Probability Distribution]({{site.glossaryurl}}/#probability-and-statistics){:target="_glossary"}, which means that some values are more likely than others in a given context, but you can't predict exactly what you will get in any single observation.
> 1. Testing AI-enabled applications requires understanding and using the same tools based on statistical techniques that are used to assess model performance, such as [Benchmarks]({{site.glossaryurl}}/#benchmark){:target="_glossary"}.
> 1. Many generative models support a _temperature_ setting that lets you reduce the amount of randomness down to &ldquo;none&rdquo;, when desired. This feature can be useful in tests, but some randomness is almost always desired in the running production system.

## Why Determinism is an Important Tool for Software Development

We have learned from decades of experience that creating and maintaining reliable software requires deterministic [Behavior]({{site.glossaryurl}}/#behavior){:target="_glossary"}, whenever possible, and principled handling of unavoidable nondeterminism. Simply stated, the more [Predictable]({{site.glossaryurl}}/#predictable){:target="_glossary"} and [Repeatable]({{site.glossaryurl}}/#repeatable){:target="_glossary"} the behavior, the easier it is to _reason_ about its [State]({{site.glossaryurl}}/#state){:target="_glossary"} and [Behavior]({{site.glossaryurl}}/#behavior){:target="_glossary"}, including aspects of design, testing, and interactions with other software.

To frame the following discussion, We will use the term [Unit]({{site.glossaryurl}}/#unit){:target="_glossary"} for the lowest-granularity encapsulation of some sort of work done by code execution. (This term was popularized by the [Test-Driven Development]({{site.glossaryurl}}/#test-driven-development){:target="_glossary"} community.) We will use [Component]({{site.glossaryurl}}/#component){:target="_glossary"} for larger-granularity collections of units. Depending on the context, a unit will usually be a [Function]({{site.glossaryurl}}/#function){:target="_glossary"} or a [Class]({{site.glossaryurl}}/#class){:target="_glossary"}. We will normally use component for a whole distributed service we test or use. 

Furthermore, suppose a unit in question is [Immutable]({{site.glossaryurl}}/#immutable){:target="_glossary"}, meaning its [State]({{site.glossaryurl}}/#state){:target="_glossary"} never changes. Also, suppose it never performs [Side Effects]({{site.glossaryurl}}/#side-effect){:target="_glossary"}, a term meaning it doesn't modify any state outside of itself, like writing to file (which modifies the state of the file), updating a database record (a similar state change), or reading user input (which will be different every time). Such a unit will _always_ be deterministic, which means that if we invoke it with the same input repeatedly, we _must always_ receive the same value back. For example, the Mathematics equation `sin(π) == -1` will always be true, and a software implementation of it will always be true, as well (ignoring potential floating point round-off errors...). For such a unit, you can write an automated test that checks this result and it will never, ever fail, _unless_ some new bug, a [Regression]({{site.glossaryurl}}/#regression){:target="_glossary"}, causes its behavior to change. 

There are necessary exceptions to this deterministic behavior for real-world systems. Some units will have [Mutable]({{site.glossaryurl}}/#mutable){:target="_glossary"} state, like files, databases, and many in-memory data structures. Finally, any distributed systems, including multi-threaded applications, cannot guarantee how events will be ordered nor which events will occur. 

Fortunately, _all_ these more complex behaviors are well understood. For example, the range of possible values and orders of occurrence are usually bounded, allowing both exhaustive tests to be written and allowing effective handling when testing dependencies that use them and when everything runs in production deployments. We have effective techniques for handling these scenarios, some of which we will review in [Architecture and Design for Testing]({{site.baseurl}}/arch-design/).

To summarize, application developers expect the following:

* Most software behaves deterministically, _with known exceptions_, allowing reasoning about behaviors and writing tests to verify expectations.
* The ability to use repeatable, automated tests to validate new behaviors work as designed and to ensure that no regressions occur as the application code base evolves.
* The ability to work with high productivity, because robust, comprehensive test suites provide _confidence_ in the current safety and reliability of the application, and since they also catch regressions when they occur during the evolution of the software, the developer can work relatively quickly.

## How Generative AI Changes This Picture

Generative AI models are inherently [Stochastic]({{site.glossaryurl}}/#stochastic){:target="_glossary"} and hence nondeterministic. As an extreme example, sending the same query to a model, "Write a haiku about the beauty of Spring" or "Create an image of a dog in a space suit walking on Mars", is _expected_ to return a different result _every time_. How do you reason about and write reliable tests for such &ldquo;expected&rdquo; behavior? Introducing AI-generated content into an application makes it difficult, if not impossible, to write deterministic tests that are repeatable and automatable. 

More precisely, the simple view of an [LLM]({{site.glossaryurl}}/#large-language-model){:target="_glossary"} is that it generates the next [Token]({{site.glossaryurl}}/#token){:target="_glossary"}, one at a time, based on the tokens it has generated so far, guided by any additional context information that was supplied in the prompt. It picks the next token randomly from all possible tokens based on the probability that each one would be a &ldquo;suitable&rdquo; choice to appear next. Those tokens with the highest [Probabilities]({{site.glossaryurl}}/#probability-and-statistics){:target="_glossary"} are chosen more often, but occasionally less-probable tokens are chosen. [Multimodal Models]({{site.glossaryurl}}/#multimodal-models){:target="_glossary"} that generate images, audio, and video work similarly.

Therefore, model outputs are an example of a [Stochastic]({{site.glossaryurl}}/#stochastic){:target="_glossary"} process, where each _observation_, a [Token]({{site.glossaryurl}}/#token){:target="_glossary"} in this case, can't be predicted exactly, but if you collect enough observations, the frequencies of the observed values will fit a _random probability distribution_ (see [Probability and Statistics]({{site.glossaryurl}}/#probability-and-statistics){:target="_glossary"}) that represents the model's behavior. 

Actually, some models support an adjustable parameter, called the _temperature_, that controls how much randomness is allowed in token selection. In these models, you can turn this parameter down to _zero_, which forces the model to always pick the _most probable_ token in every situation. This makes the output effectively deterministic for any given prompt! However, we normally want some variability. Nevertheless, a zero temperature can be useful in some tests.

{: .attention}
> _Temperature_ is a useful metaphor for randomness; think of how the surface of a pot of water behaves as you heat it up, going from cold and flat (and &ldquo;predictable&rdquo;) to hot and very bubbly, where the height at any point on the surface can vary a lot around the average level.

Two other simple random probability distribution examples are useful to consider. Consider the behavior of flipping a _fair_ (unweighted) coin. For each flip, you have no way of knowing whether you will observe a head or a tail, each of which has a 50% probability of occurring. However, if you flip the coin 100 times, you will have observed approximately 50 heads and 50 tails. For 1000 flips, the split is even more likely to be 500 heads and 500 tails. A less simple example distribution is the values observed when rolling two, six-sided dice. Without going into details, it is much more probable to get two values that add up to 5, 6, or 7 on a roll, for example, than to get a total of 2 or 12.

Furthermore, the nondeterminism introduced by generative AI isn't _peripheral_ to the application logic, like an implementation detail that is independent of the user experience. Rather, the nondeterminism is a core enabler of fundamentally new capabilities that were previously impossible. 

The problems are compounded when we have applications built on [Agents]({{site.glossaryurl}}/#agent){:target="_glossary"}, each of which will have some stochastic behavior of its own, if it encapsulates a generative model.

So, we can't avoid this nondeterminism. We have to learn how to write tests that are still repeatable and automatable, that are deterministic where feasible, but otherwise effectively evaluate the stochastic behavior that occurs. These tests are necessary to give us _confidence_ our application works as intended. This is the challenge this guide explores.

## How Do AI Experts Test Models?

AI experts also need to understand how well generative models (and the [AI Systems]({{site.glossaryurl}}/#ai-systems){:target="_glossary"} that use them) perform against various criteria, like skills in Mathematics, and suppression of hate speech and hallucinations. 

Sometimes you can model a stochastic process with Mathematics to understand it, like tossing a coin or a pair of dice. Often, though, the behavior is too complex to model mathematically or the mathematical formulas are unknown. In these cases, you have to collect as many observations as you can, then look at the percentages for all the observed values. 

Generative AI falls into the later category and the model is so complex, people don't normally try to capture it &ldquo;experimentally&rdquo;. Instead, they just focus on observed, _aggregate_ behavior, i.e., rather than focus on token-by-token probabilities, focus on whole responses of text, images, etc.

This is what [Benchmarks]({{site.glossaryurl}}/#benchmarks){:target="_glossary"} focus on. A common way to implement a benchmark is to curate a set of question and answer (Q&A) pairs (a kind of [Labeled Data]({{site.glossaryurl}}/#labeled-data){:target="_glossary"}) that cover as much of the _space_ of possible questions and expected answers as possible in the domain of interest. To use a benchmark, a model is sent each question and the answer is evaluated for correctness. Deciding whether or not an answer is &ldquo;correct&rdquo; is another challenge, which we'll return to in several places in [Testing Strategies and Techniques]({{site.baseurl}}/testing-strategies).

It is usually not necessary for you to run these benchmarks yourself. The results of applying the more popular benchmarks against the more popular models are published in leaderboards, allowing you to browse models based on how well they do against the benchmarks you care most about.

So, when you see that a particular model scores 85% on a benchmark, it means the model's replies to the questions was judged to be correct 85% of the time. Now, **is 85% good enough??** The answer depends on the application requirements. You may have to chose the best-performing model for a given benchmark, while considering performance of the model against other benchmarks to be less critical.

This approach to validating behaviors is far different than the unambiguous 100% &ldquo;pass/fail&rdquo; answers software developers are accustomed to seeing.

Some models can output a _confidence_ score, expressing how much trust they have in the answer they provided. Is there a correlation between those confidence scores and the answers that were judged good or bad? That information can tell you if the confidence scores are very trustworthy.

More advanced [Statistical Analysis]({{site.glossaryurl}}/#probabilities-and-statistics){:target="_glossary"} techniques can be used to probe the results of a stochastic process more deeply. 

You are probably already familiar with statistical concepts like the _mean_ and _standard deviation_. For example, what is the _mean_ (average) score across all models against a particular benchmark? A low mean gives you a sense that the benchmark is hard for a lot of the models, while a high mean value means that models are now very good in this area, _on average_. 

The standard deviation of model scores tells you how much variability there is across the models. For example, this value is fairly large if newer and larger models tend to significantly outperform older and smaller models. In contrast, if the standard is low, then it means that all models are closer in performance. Combined with a low means, it suggests all models struggle about equally with the benchmark, while a high mean with a low standard deviation suggests that the benchmark is easy for most models to perform well on.

### This Is Not a New Problem

Recently, [one of us]({{site.referencesurl}}/#dean-wampler) posted a link on [Mastodon](https://discuss.systems/@deanwampler/113850433324825993){:target="mastodon"} to the slides for a talk, [Generative AI: Should We Say Goodbye to Deterministic Testing?](https://deanwampler.github.io/polyglotprogramming/papers/#Generative-AI-Should-We-Say-Goodbye-to-Deterministic-Testing){:target="slides"}. In a private conversation afterwards, [Adrian Cockcroft]({{site.referencesurl}}/#adrian-cockcroft) said that Netflix encountered similar problems around 2008 with their content recommendation systems: &ldquo;The content inventory (movies or products) changes constantly, and the recommendations are personalized so that everyone sees a different result. We had to build some novel practices and tools for our QA engineers.&rdquo; 

The specific tools and practices he mentioned are discussed in [Test Doubles at Netflix]({{site.baseurl}}/arch-design/component-design/#test-doubles-at-netflix) and [The Use of Statistics at Netflix]({{site.baseurl}}/testing-strategies/statistical-tests/#the-use-of-statistics-at-netflix).

--- 

Review the [highlights](#highlights) summarized above. Next, before we discuss [Testing Strategies]({{site.baseurl}}/testing-strategies), let us first discuss [Architecture and Design]({{site.baseurl}}/arch-design), informed by our testing concerns.
