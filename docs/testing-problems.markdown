---
layout: default
title: Testing Problems
nav_order: 10
has_children: false
---

# Testing Problems Caused by Generative AI Nondeterminism 

Let's first review why [Determinism]({{site.glossaryurl}}/#determinism) is an important concept in software development, then discuss how the use of [Generative AI Models]({{site.glossaryurl}}/#generative-ai-model) makes this difficult.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Traditional software is mostly [Deterministic]({{site.glossaryurl}}/#determinism). This makes it much easier to reason about its behavior and to write repeatable, reliable tests. This is a central, enabling assumption made in software development.
> 1. [Generative AI Model]({{site.glossaryurl}}/#generative-ai-model) outputs are [Stochastic]({{site.glossaryurl}}/#stochastic), governed by a random probability distribution, which means that some values are more likely than others in a given context, but you can't predict exactly what you will get in any, single observation.
> 1. Testing AI-enabled applications requires understanding and using the same tools based on statistical techniques that are used to assess model performance, such as [Benchmarks]({{site.glossaryurl}}/#benchmark).
> 1. This challenge predates generative AI. It exists in any system that relies on probabilistic models of potential activity.

## Why Determinism is an Important Tool for Software Development

We have learned from decades of experience that creating and maintaining reliable software requires deterministic [Behavior]({{site.glossaryurl}}/#behavior), whenever possible, and when it can't be avoided, principled handling of the nondeterminism. Simply stated, the more [Predictable]({{site.glossaryurl}}/#predictable) and [Repeatable]({{site.glossaryurl}}/#repeatable) the behavior, the easier it is to _reason_ about its [State]({{site.glossaryurl}}/#state) and [Behavior]({{site.glossaryurl}}/#behavior), including aspects of design, testing, and interactions with other software libraries.

To frame the following discussion, We will use the term [Unit]({{site.glossaryurl}}/#unit) for the lowest-granularity encapsulation of some sort of work done by code execution. (We will use [Component]({{site.glossaryurl}}/#component) for larger-granularity collections of units.) Depending on the context, a unit will be a [Function]({{site.glossaryurl}}/#function), a [Class]({{site.glossaryurl}}/#class), or even a distributed service we invoke. 

Furthermore, suppose a unit in question is [Immutable]({{site.glossaryurl}}/#immutable), meaning its [State]({{site.glossaryurl}}/#state) never changes, and it performs no [Side Effects]({{site.glossaryurl}}/#side-effect), meaning it doesn't modify the state of other units, like writing to files, or read state from [Mutable]({{site.glossaryurl}}/#mutable) units, like ask a service for the current weather. This unit will _always_ be deterministic, which means that if we invoke it with the same input repeatedly, we _must always_ receive the same value back. For example, the Mathematics equation `sin(π) == -1` will always be true, and a software implementation of it will always be true, as well (ignoring potential floating point round-off errors...). For such a unit, you can write an automated test that checks this result and it will never, ever fail, _unless_ some new bug, a [Regression]({{site.glossaryurl}}/#regression), causes its behavior to change. 

There are necessary exceptions to this deterministic behavior for real-world systems. Some units will have mutable state, like a stack data structure. Some units will prompt a user for inputs, so the value it returns will rarely be the same value from one invocation to the next. Finally, any distributed systems, including multi-threaded applications, cannot guarantee how events will be ordered, and many cases which events will occur. 

Fortunately, these forms of nondeterminism and side effects are well understood and the range of possible occurrences is usually bounded, allowing effective handling both in tests and in production deployments. We have effective techniques for handling them, which we will review in [Architecture and Design for Testing]({{site.baseurl}}/arch-design/).

To summarize, application developers expect the following:

* Relying on determinism, _as much as possible_, to enable tests to verify expected behavior.
* Use of repeatable, automated tests to ensure that no regressions occur as the application code base evolves.
* High productivity, because robust, comprehensive test suites provide _confidence_ in the current safety and reliability of the application, and also catch regressions when they occur.

## How Generative AI Changes This Picture

Generative AI models are inherently nondeterministic. The same query to a model, for example, "Write a haiku about the beauty of Spring" or "Create an image of a dog in a space suit walking on Mars", is _expected_ to return a different result _every time_. How do you reason about and write reliable tests for such &ldquo;expected&rdquo; behavior? Introducing AI-generated content into an application makes it difficult, if not impossible, to write deterministic tests that are repeatable and automatable. 

More precisely, the simple view of an [LLM]({{site.glossaryurl}}/#large-language-model) is that it generates the next [Token]({{site.glossaryurl}}/#token), one at a time, based on the tokens it has generated so far, guided by any additional context information that was supplied in the prompt. It picks the next token randomly from all possible tokens based on the probability that each one would be a &ldquo;suitable&rdquo; choice to appear next. Those tokens with the highest [Probabilities]({{site.glossaryurl}}/#probability-and-statistics) are chosen more often, but occasionally less-probable tokens are chosen. [Multimodal Models]({{site.glossaryurl}}/#multimodal-models) that generate images, audio, and video work similarly.

Therefore, model outputs are an example of a [Stochastic]({{site.glossaryurl}}/#stochastic) process, where each _observation_, a [Token]({{site.glossaryurl}}/#token) in this case, can't be predicted exactly, but if you collect enough observations, the frequencies of the observed values will be fit a _random probability distribution_ (see [Probability and Statistics]({{site.glossaryurl}}/#probability-and-statistics)). 

Actually, some models support an adjustable parameter, called the _temperature_, that controls how much randomness is allowed in token selection. In these models, you can turn this parameter down to _zero_, which forces the model to always pick the _most probable_ token in every situation. This makes the output effectively deterministic for any given prompt! However, we normally want some variability. Nevertheless, a zero temperature can be useful in some tests!

{: .highlight}
> _Temperature_ is a useful metaphor for randomness; think of how the surface of a pot of water behaves as you heat it up, going from cold and flat (and &ldquo;predictable&rdquo;) to hot and very bubbly, where any point on the surface can vary a lot around the average level.

Two other simple random probability distribution examples are useful to consider. Consider the behavior of flipping a _fair_ (unweighted) coin. For each flip, you have no way of knowing whether you will observe a head or a tail, each of which has a 50% probability of occurring. However, if you flip the coin 100 times, you will have observed approximately 50 heads and 50 tails. For 1000 flips, the split is even more likely to be 500 heads and 500 tails. A less simple example distribution is the values observed when rolling two, six-sided dice. Without going into details, it is much easier to get two values that add up to 5, 6, or 7 on a roll, for example, than to get a total of 2 or 12.

Furthermore, the nondeterminism introduced by generative AI isn't _peripheral_ to the application logic, like an implementation detail that is independent of the user experience. Rather, the nondeterminism is a core enabler of fundamentally new capabilities that were previously impossible. 

So, we can't avoid this nondeterminism. We have to learn how to write tests that are still repeatable and automatable, that are deterministic where feasible, but otherwise effectively evaluate the stochastic behavior that occurs. These tests are necessary to give us _confidence_ our application works as intended. This is the challenge this guide explores.

## How Do AI Experts Test Models?

AI experts also need to understand how well generative models (and the [AI Systems]({{site.glossaryurl}}/#ai-systems) that use them) perform against various criteria, like suppression of hate speech and hallucinations. 

When modeling a stochastic process to understand it, you have to collect as many observations as you can, then look at the percentages for all the observed values. The widely-used leaderboards that rank models show the results of running [Benchmarks]({{site.glossaryurl}}/#benchmarks) against the models. A common way to implement a benchmark is to curate a set of question and answer (Q&A) pairs that cover as much of the _space_ of possible questions and expected answers as possible. In using these kinds of benchmarks, a model is sent each question and the answer is evaluated for correctness. (Deciding whether or not an answer is &ldquo;correct&rdquo; is another challenge, which we'll return to in several places in [Testing Strategies and Techniques]({{site.baseurl}}/testing-strategies).)

So, when you see that a particular model scored 85% on a benchmark, it means the model's replies to the questions was judged to be correct 85% of the time. Is 85% good enough?? It really depends on the application requirements, whether or not there are better-performing, alternative models, etc. This approach to validating behaviors is far different than the unambiguous 100% &ldquo;pass/fail&rdquo; answers software developers are accustomed to seeing.

More advanced [Statistical Analysis]({{site.glossaryurl}}/#probabilities-and-statistics) techniques can be used to probe the results of a stochastic process more deeply. Some models can output a _confidence_ score, expressing how much trust they have in the answer they provided. Is there a correlation between those confidence scores and the answers that were judged good or bad? That information can tell you if the confidence scores are very trustworthy.

You are probably already familiar with concepts like the _mean_ and _standard deviation_. For example, what is the _mean_ (average) score across all models against a benchmark? A low value gives you a sense of how hard the benchmark is vs. the state-of-the-art for the models evaluated. The standard deviation of model scores tells you how much variability there is across the models. Often this value is fairly large as newer and larger models tend to outperform older and smaller models, for example.

### This Is Not a New Problem

Recently, [one of us]({{site.baseurl}}/references/#dean-wampler) posted a link on [Mastodon](https://discuss.systems/@deanwampler/113850433324825993){:target="mastodon"} to the slides for a talk, [Generative AI: Should We Say Goodbye to Deterministic Testing?](https://deanwampler.github.io/polyglotprogramming/papers/#Generative-AI-Should-We-Say-Goodbye-to-Deterministic-Testing){:target="slides"}. In a private conversation afterwards, [Adrian Cockcroft]({{site.baseurl}}/references/#adrian-cockcroft) said that Netflix encountered similar problems around 2008 with their content recommendation systems: &ldquo;The content inventory (movies or products) changes constantly, and the recommendations are personalized so that everyone sees a different result. We had to build some novel practices and tools for our QA engineers.&rdquo; 

The specific tools and practices he mentioned are discussed in [Test Doubles at Netflix]({{site.baseurl}}/arch-design/component-design/#test-doubles-at-netflix) and [The Use of Statistics at Netflix]({{site.baseurl}}/testing-strategies/statistical-tests/#the-use-of-statistics-at-netflix)

--- 

Review the [highlights](#highlights) summarized above. Next, before we discuss [Testing Strategies]({{site.baseurl}}/testing-strategies), let us first discuss [Architecture and Design]({{site.baseurl}}/arch-design), informed by our testing concerns.
