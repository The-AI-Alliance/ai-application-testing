---
layout: default
title: Notes on Tuning
nav_order: 425
parent: Advanced Techniques
has_children: false
---

# Notes on Tuning

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

This chapter contains notes on various [Tuning]({{site.glossaryurl}}/#tuning){:target="_glossary"} techniques, including those use by foundation model builders who have broader goals than the incremental refinement tuning that interest us in this guide. Hence, not all the techniques and ideas discussed here will be important for our purposes.

{: .warning}
> **WARNING:** 
> 
> These are raw notes. They are not very well organized, but if you are interested in the state of the art for model tuning, these notes provide a good place to start, with plenty of links to more advanced materials. Eventually, these notes will be refined and incorporated into other chapters, especially [From Testing to Tuning]({{site.baseurl}}/advanced-techniques/from-testing-to-tuning/). 

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Tuning has different meanings and goals for different people, which determines the best techniques to use, along with different data and compute requirements.
>     1. For model builders, tuning means taking a raw model and making it better at general instruction following, adherence to social norms, etc. This task requires the largest data sets and most sophisticated, leading-edge techniques.
>     1. For end users building apps, tuning means taking one of those tuned models and further tuning it for domain-specific behaviors, etc. This task requires much smaller data sets, although they will need to be more specialized for the domain-specific behaviors, and more straightforward tuning techniques, such as [Supervised Fine Tuning]({{site.glossaryurl}}/#supervised-fine-tuning){:target="_glossary"}.
> 1. Hugging Face's [a smol course](https://huggingface.co/learn/smol-course/unit0/1){:target="_blank"} is recommended for learning about tuning techniques. Their [LLM Course](https://huggingface.co/learn/llm-course/chapter1/1){:target="_blank"} is recommended for a general introduction to LLMs.

## Hugging Face Training on Model Tuning

Hugging Face's [a smol course](https://huggingface.co/learn/smol-course/unit0/1){:target="_blank"} is designed to teach all aspects of model [Tuning]({{site.glossaryurl}}/#tuning){:target="_glossary"}. It is not yet complete, but projected to be done by the end of 2025. 

{: .tip}
> **TIP:** 
> 
> This is the best place to start for practical training on tuning.

Also recommended is their more general [LLM Course](https://huggingface.co/learn/llm-course/chapter1/1){:target="_blank"}, which provides useful background information that is assumed by the smol course.

The smol course covers to the two main kinds of tuning used today:

* [Instruction Tuning](huggingface.co/learn/smol-course/unit1/1){:target="_blank"} tunes a &ldquo;raw&rdquo; base model to be better at instruction following and other general-purpose behaviors, like alignment with social norms, as well as domain-specific behaviors. It uses [Supervised Fine Tuning]({{site.glossaryurl}}/#supervised-fine-tuning){:target="_glossary"} to achieve this.
* [Preference Alignment](https://huggingface.co/learn/smol-course/unit2/1){:target="_blank"} further trains a model to provide answers people actually &ldquo;prefer&rdquo;, which makes them more useful for real-world use. It uses a relatively new technique called [Direct Preference Optimization]({{site.glossaryurl}}/#direct-preference-optimization){:target="_glossary"} (DPO), which has largely replaced variants of [Reinforcement Learning]({{site.glossaryurl}}/#reinforcement-learning){:target="_glossary"}, which are more difficult to use, although they are still in widely used.

### Instruction Tuning

It is common to have several instruction tuning &ldquo;phases&rdquo; to go from a &ldquo;raw&rdquo; model to one that meets the goals for model performance in an application context. For our purposes, we start with models that are already tuned for instruction following, social norms, etc. , then perform further tuning to add the specific domain-specific behaviors required. In fact, model developers usually publish raw and instruction-tuned models.

The heart of instruction tuning is [Supervised Fine Tuning]({{site.glossaryurl}}/#supervised-fine-tuning){:target="_glossary"}. For domain-specific tuning, which is most relevant for our needs, as discussed in [From Testing to Tuning]({{site.baseurl}}/advanced-techniques/from-testing-to-tuning), we start with a model that is already instruction tuned and use [Supervised Fine Tuning]({{site.glossaryurl}}/#supervised-fine-tuning){:target="_glossary"} to improve it, as discussed in the [third smol course section](https://huggingface.co/learn/smol-course/unit1/3){:target="_blank"}.

[What is Supervised Fine-Tuning?](https://huggingface.co/learn/smol-course/unit1/3#what-is-supervised-fine-tuning) describes SFT as &ldquo;...the process of continuing to train a [Pre-Trained]({{site.glossaryurl}}/#pre-Trained){:target="_glossary"} model on task-specific datasets with labeled examples.&rdquo; While pre-training teaches general language understanding and information, SFT teaches specific skills and behaviors, as opposed to new knowledge. For example, SFT hones how the knowledge is used toward specific applications, desired ways of responding to prompts, and use case-specific requirements.

Fortunately, SFT requires far less resources than pre-training, which we will discuss below.

However, the tutorial offers this advise:

> Before starting SFT, consider whether using an existing instruction-tuned model with well-crafted prompts would suffice for your use case. SFT involves significant computational resources and engineering effort, so it should only be pursued when prompting existing models proves insufficient. Learn more about this decision process in the [Hugging Face LLM Course](https://huggingface.co/learn/llm-course/en/chapter11/3){:target="_blank"}.

[When to Use Supervised Fine-Tuning](https://huggingface.co/learn/smol-course/unit1/3#when-to-use-supervised-fine-tuning) provides some guidance on when SFT is necessary, versus just relying on a model without additional tuning.
They offer the following checklist to determine if SFT is appropriate, which we quote verbatim:

> * Have you tried prompt engineering with existing instruction-tuned models?
> * Do you need consistent output formats that prompting cannot achieve?
> * Is your domain specialized enough that general models struggle?
> * Do you have high-quality training data (at least 1,000 examples)?
> * Do you have the computational resources for training and evaluation?

If you answered “yes” to most of these, SFT is likely worth pursuing.

In [The SFT Process](https://huggingface.co/learn/smol-course/unit1/3#the-sft-process){:target="_blank"}, they point out that you need a relatively small, but very high-quality dataset:

> * Minimum: 1,000 high-quality examples for basic fine-tuning.
> * Recommended: 10,000+ examples for robust performance.
> * Quality over quantity: 1,000 well-curated examples often outperform 10,000 mediocre ones.

This is _supervised_ data, so each example requires:

> * Input prompt: The user’s instruction or question
> * Expected response: The ideal assistant response
> * Context (optional): Any additional information needed

The section goes on to provide detailed suggestions for tuning parameters, like the learning rate, how to run their tuning tools, and how to interpret the results.

## &ldquo;How to approach post-training for AI applications&rdquo; - Nathan Lambert

This section summarizes of [Nathan Lambert]({{site.referencesurl}}/#nathan-lambert)'s NeurIPS 2024 talk, [How to approach post-training for AI applications](https://docs.google.com/presentation/d/1LWHbtz74GwKSGYZKyBVUtcyvp8lgYOi5EVpMnVDXBPs/edit#slide=id.p){:target="nl-neurips2024"} (December 10, 2024), along with the following supporting blog posts and other links that are referenced in the presentation and listed here in reverse chronological order. Some terms in this list will be defined later:

* [OpenAI's Reinforcement Finetuning and RL for the masses](https://www.interconnects.ai/p/openais-reinforcement-finetuning){:target="openai-rf"} (December 11, 2024) - A description of OpenAI's recently announced research program combining RL and fine tuning (our spelling here). There is a link in the post to an OpenAI web page for this, but it appears to be gone now.
* [SimPO: A New Way to Teach AI Models to Follow Human Preferences](https://pli.princeton.edu/blog/2024/simpo-new-way-teach-ai-models-follow-human-preferences){:target="_blank"} (December 2, 2024) - Another replacement for RLHF that provides very efficient and effective fine tuning of instruction models.
* [OpenAI’s Strawberry, LM self-talk, inference scaling laws, and spending more on inference](https://www.interconnects.ai/p/openai-strawberry-and-inference-scaling-laws){:target="_blank"} (September 6, 2024) - Details on _inference scaling laws_ and uses of it to improve inference.
* [A recipe for frontier model post-training](https://www.interconnects.ai/p/frontier-model-post-training){:target="_blank"} (August 07, 2024), which discusses the general topic of state-of-the-art [Post-Training]({{site.glossaryurl}}/#post-training){:target="_glossary"} a [Pre-trained]({{site.glossaryurl}}/#pre-training){:target="_glossary"} model.
* [Do we need RL for RLHF?](){:target="_blank"} (December 6, 2023) - &ldquo;Direct (DPO) vs. RL methods for preferences, more RLHF models, and hard truths in open RLHF work. We have more questions than answers.&rdquo;
* [RLHF progress: Scaling DPO to 70B, DPO vs PPO update, Tülu 2, Zephyr-β, meaningful evaluation, data contamination](https://www.interconnects.ai/p/rlhf-progress-scaling-dpo-to-70b){:target="_blank"} (November 22nd, 2023)

I put in the dates, because everything is moving rapidly and it helps to know the sequence of these writings, as some of the ideas discussed emerged after a particular post was written.

Incidentally, Nathan also co-presented a [tutorial on language modeling](https://docs.google.com/presentation/d/179dpzWSQ9G7EAUlvaJdeE0av9PLuk9Rl33nfhHSJ4xI/edit?slide=id.g31b08bdaca5_0_238#slide=id.g31b08bdaca5_0_238){:target="_blank"} at the same NeurIPS conference.

Nathan also has a [new book](https://rlhfbook.com){:target="_blank"} on [Reinforcement Learning with Human Feedback]({{site.glossaryurl}}/#reinforcement-learning-with-human-feedback){:target="_glossary"} (RLHF).

### Introduction

As the presentation points out: _The raw pre-trained LMs are neither safe nor robust for public use and interactions, thus require “alignment” between AI and humans._

Where the terms are as follows

* [Pre-Training]({{site.glossaryurl}}/#pre-training){:target="_glossary"} creates the raw LLM.
* [Adaptation]({{site.glossaryurl}}/#adaptation){:target="_glossary"} is the process for [Alignment]({{site.glossaryurl}}/#alignment){:target="_glossary"}, so that the resulting model is better in the following ways:
  * It follows natural language instructions better.
  * It is aware of harmful behaviors.
  * It responds according to human preferences.
  * It has improved core skills.

In the blog post, [A recipe for frontier model post-training](https://www.interconnects.ai/p/frontier-model-post-training){:target="_blank"}, he mentions that some seminal projects on adaptation, [InstructGPT](https://arxiv.org/abs/2203.02155){:target="_blank"}, [WebGPT](https://arxiv.org/abs/2112.09332){:target="_blank"}, [Sparrow](https://deepmind.google/discover/blog/building-safer-dialogue-agents/){:target="_blank"}, [Summarizing from Human Feedback](https://arxiv.org/abs/2009.01325){:target="_blank"}, and [Helpful and Harmless Assistant](https://arxiv.org/abs/2204.05862){:target="_blank"} are becoming out of date with how tuning, especially with [Reinforcement Learning with Human Feedback]({{site.glossaryurl}}/#reinforcement-learning-with-human-feedback){:target="_glossary"} (RLHF), is done today. While the goals, high-level tools, and some of the evaluations are still relevant the details of data curation and other aspects are now dated.

He cites the [Llama 3.1 paper](https://ai.meta.com/research/publications/the-llama-3-herd-of-models/){:target="llama31"}, an [Apple paper](https://machinelearning.apple.com/papers/apple_intelligence_foundation_language_models.pdf){:target="apple"} ([arXiv](https://arxiv.org/abs/2407.21075v1){:target="archive"}), and others as more up-to-date descriptions.

The new recipe these projects use requires a few assumptions to hold:

* Synthetic data can be of higher quality than humans, especially for demonstrations on challenging tasks.
* Reinforcement learning from human feedback (RLHF) can scale far further than instruction tuning.
* It takes multiple rounds of training and generation to reach your best model.
* Data filtering is the most important part of training.

### The New Standard Pipeline

This section summarizes part of the blog post, [A recipe for frontier model post-training](https://www.interconnects.ai/p/frontier-model-post-training){:target="_blank"}.

#### 1. Human Preference Data

Nathan says the focus of the original RLHF pipeline was on human data, which came in two primary forms: 1) human data for instruction-tuning on specialized tasks and 2) human preference data on model completions. The data sets were costly to create with few OSS data sets available. Also, while he was at Hugging Face, his team found that success tuning one model didn't always translate to success tuning other models.

These days, the only human-generated data widely used appears to be preference data, used for [Instruction Fine Tuning]({{site.glossaryurl}}/#instruction-fine-tuning){:target="_glossary"} (IFT) (the most common form of [Supervised Fine Tuning]({{site.glossaryurl}}/#supervised-fine-tuning){:target="_glossary"} - SFT). Human-generated data is expensive to acquire. Based on what information is available about Llama 2's training, Nathan speculates that Meta spent at least $10-20 million on preference data. In contrast, Nemotron was developed with a large amount of synthetic data to replace the human data, but the model is not considered comparably strong.

Because of the expense of human data, there is a need and therefore an opportunity for the open community to pioneer reducing human input with [LLM-as-a-judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge/) or reward modeling techniques (the latter for reinforcement learning).

#### 2. Scaling RLHF

[Reinforcement Learning with Human Feedback]({{site.glossaryurl}}/#reinforcement-learning-with-human-feedback){:target="_glossary"} (RLHF) is considered by many researchers to be more scalable and more productive than instruction fine tuning, so much so that many model builders may stop using IFT. At the very least, the current consensus is to use IFT initially, especially for domain-specific tuning, then switch to RLHF.

RLHF is an iterative process of refinement, with each model generation improving over its predecessor. An open question is how many rounds are optimal. The Llama 2 paper and the Nemotron paper detail about five training rounds. Llama 3.1 used six rounds and Nemotron used four. Multiple instruction tuning rounds were done before these RLHF rounds. 

There are two practical reasons for using iterations like this:

* The third-party annotation companies supplied the human data in batches, rather than all at once, so they did tuning iterations with the data that was available. 
* In general, iterations are a universally-wise strategy. They de-risk any project, since you can check progress as you go to be sure you are moving in the right direction, rather than waiting for all data to be available and doing one large and expensive training run with an uncertain outcome.

The Llama 2 paper has diagrams (reproduced in the presentation) that show how the model's _harmlessness_ improved during several iterations of RLHF tuning.

The algorithms used for RL (or replacing it...) have evolved rapidly, with several popular variants in use. For example:

* [Proximal Policy Optimization](https://arxiv.org/abs/1707.06347){:target="_blank"} (PPO) - An algorithm for training a _reward model_ used in RL that eliminates stability problems and some overhead of earlier algorithms. Used widely by OpenAI since 2018, at least until recently.
* [Direct Preference Optimization](https://arxiv.org/abs/2305.18290){:target="_blank"} (DPO) - The most popular algorithm currently, which is simpler to use and more stable than PPO. It eliminates the need for a reward model and hence the use of "classical" RL. Instead a preference data set is used to tune the target model directly, whereas in PPO, the data is used to train the reward model, which is then used in an RL process to tune the target model.
* [MDLOO](https://arxiv.org/abs/2407.21075v1){:target="_blank"} used by Apple and based on [research from Cohere](https://arxiv.org/abs/2402.14740){:target="_blank"}.

See [this blog post](https://medium.com/@joaolages/direct-preference-optimization-dpo-622fc1f18707){:target="_blank"} for an accessible overview of DPO. The following image is taken from and explained in that post:

![DPO algorithm](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*AqKOT0pxzi5kOgiobb-Fvg.png) 

I won't repeat the explanation here...

See also:
* An Interconnects post [Do we need RL for RLHF?](https://www.interconnects.ai/p/the-dpo-debate){:target="_blank"}
* An Ai2 [video](https://www.youtube.com/watch?v=YJMCSVLRUNs){:target="_blank"} on DPO.
* [Unsloth documentation](https://docs.unsloth.ai/get-started/reinforcement-learning-rl-guide/reinforcement-learning-dpo-orpo-and-kto){:target="_blank"} on different RL algorithms.
* Sebastian Raschka's [detailed description of RLHF](https://magazine.sebastianraschka.com/p/llm-training-rlhf-and-its-alternatives){:target="_blank"} published two years ago, shortly before DPO came out.

#### 3. Synthetic Data

Because of the expense of human generated or curated data, synthesizing data is now an established part of tuning. One very common practice is to use bigger models to generate data used to tune smaller models.

From the **Discussions** section of the slides, _How much data do you need?_

* For instruction fine tuning:
  * You can start to see behaviors change with just ~1000 samples.
  * For good performance, you need data on each task you are trying to improve.
  * Performance continues to improve as you scale the data per task, even when approaching millions of examples.
* For RL fine tuning:
  * OpenAI says performance improves with just ~10 samples. _This is just for entirely out-of-distribution tasks._
* In work on Ai2's in Tülu 3, performance continued to scale with 100s to 1000s of examples.

In contrast, if you are doing full post-training, by which I think he means _full_ in the sense of a raw foundation model being tuned for widely varying applications, you should expect to use:
* 1 million+ SFT prompts.
* 1 million+ preference pairs.
* Substantial data filtering.

Obviously the narrower the application or domain being targeted, the less expensive it will be to acquire enough data for good results.

#### 4. Data Quality Is King

&ldquo;The majority of the Llama 3.1 report is about data curation details.&rdquo; High-quality, domain-specific data is essential to successfully tune a domain-specific model.

### Putting It Together

Here is a diagram of the Llama 3 tuning process taken from the [Llama 3 research paper](https://arxiv.org/abs/2407.21783){:target="_blank"}:

![Llama 3 tuning process](https://substackcdn.com/image/fetch/$s_!HvLI!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F08658b68-fcca-4fe4-9a66-abb821412d65_1730x877.png)

A similar process was used for Nemotron.

#### Side Note: What Is Rejection Sampling?
 
_Rejection sampling_ is a technique for randomly sampling data points weighted by a probability distribution. For example, consider the blue _normal distribution_ curve in this [diagram from Wikipedia](https://en.wikipedia.org/wiki/Normal_distribution#/media/File:Normal_Distribution_PDF.svg){:target="wikipedia"}.

![Normal Distribution](https://upload.wikimedia.org/wikipedia/commons/7/74/Normal_Distribution_PDF.svg)

Now suppose you want to randomly sample _x_ values between _-5_ and _+5_, where the resulting set should have more values near the _mean_ of a _normal distribution_, which is _x=0_, and fewer values away from the mean, that is where the density of _x_ values corresponds to the distribution.

To do this randomly pick _(x, y)_ points on the diagram, then **_reject_** those where the _y_ value is above the curve. Keep the &ldquo;surviving&rdquo; _x_ values. In the resulting set, the _x_ values will be denser near the mean, etc., following the distribution. 

### Apple Confirms the New Normal

In the blog post, [A recipe for frontier model post-training](https://www.interconnects.ai/p/frontier-model-post-training){:target="_blank"}, he discusses how Apple also followed the same general recipe for its models, with some interesting points of difference:

* For initial instruction tuning, they treated it as an optimization process, where they explored the optimal mix of instruction data sets to use.
* They found that the best instruction base model doesn't always lead to the best model after RL.
* Their rejection sampling technique, called _iTeC_ uses a large &ldquo;committee&rdquo; of models to generate completions, where the best completion per prompt is chosen.
* The used an RL algorithm called [MDLOO](https://arxiv.org/abs/2407.21075v1){:target="_blank"} based on [research from Cohere](https://arxiv.org/abs/2402.14740){:target="_blank"}.

It's not mentioned in the blog post, but the Apple paper's section 5.1, _Adapter Architecture_, discusses dynamic use of LoRA to fine tune their models for user's everyday activities. This could be interesting for the ideas discussed in [From Testing to Tuning]({{site.baseurl}}/advanced-techniques/from-testing-to-tuning/), where we need the ability to incrementally tune models as features are added to applications.

### The Presentation's "Discussion" Section

Back to the presentation's **Discussion** section. Most of this material will be relevant for advanced tuning situations, like improving raw base models. Below are notes on the incremental, pragmatic approach we will start in our work. This section starts with slides on data requirements, which I worked into sections above.

#### What Techniques Should You Use?

On the slide titled _What post-training methods should you use?_, he suggests this:

* Use instruction tuning / SFT for improved behavior control and performance gains.
* Use preference tuning / PreFT for stronger style control, but it's not as useful for improving performance.
* Use RL tuning for the potentially very high performance gains, but _this remains unstudied_.

#### Comparing DPO and PPO

Next, Nathan points out that &ldquo;DPO and PPO are very different optimizers:&rdquo;
* DPO is learning directly from preferences vs. using RL update rules.
* DPO is also not really online vs offline RL, but that is more muddled.

It's not yet clear if one is truly superior to the other. Early experience suggests each approach may be optimal in particular cases. See this post from Nathan, [The DPO Debate](https://www.interconnects.ai/p/the-dpo-debate){:target="_blank"} and his [video explainer](https://www.youtube.com/watch?v=YJMCSVLRUNs){:target="_blank"}.

#### Other Algorithms

**GRPO**

_Group Relative Policy Optimization_ (GRPO), introduced in the [DeepSeekMath paper](https://arxiv.org/abs/2402.03300){:target="_blank"} is explained concisely in this [DataCamp blog post](https://www.datacamp.com/blog/what-is-grpo-group-relative-policy-optimization){:target="_blank"}, which also compares it to PPO and DPO. It has the advantage that it doesn't require labeled data, just a means to “verify” correctness and order responses accordingly. For example, to train model to generate source code, a reward function can be used that verifies the generated source code compiles, passes tests, etc.

In the typical GRPO workflow, the model generates several outputs, the reward function rates each one, and the model weights are updated to favor future generation of the better results.

This method is data and cost efficient, less likely to over fit, and promotes learning novel strategies and chains of thought.

Some example domains where GRPO has been used:

* Mathematical skills
* Code generation
* Multi-step reasoning

**KTO**

Yet another algorithm has emerged, Kahneman-Tversky Optimization (KTO), which only needs directional labels on one completion rather than pairwise data. So, if you collect data that is only 👍 or 👎, KTO is very promising and is often more aligned to a particular problem's specification. Anecdotally, Nathan has heard of several cases where people have switched from DPO to KTO and see improvements. However, there is little research to base this on.

**SimPO**

Another alternative to DPO is [SimPO: A New Way to Teach AI Models to Follow Human Preferences](https://pli.princeton.edu/blog/2024/simpo-new-way-teach-ai-models-follow-human-preferences){:target="_blank"} (December 2, 2024) - Another replacement for RLHF that provides very efficient and effective fine tuning of instruction models.

#### Which Base Model?

Should you start with a base model or an instruct model as your foundation?

* For small changes → start from an instruct model.
* for developing many capabilities or for bigger changes → start from a base model.

Deciding on the foundation model to use:

* **Performance variations (and ceilings):** Some models will show better behaviors for different different tasks! Consider trying multiple options, e.g. Mistral Large is great for CLIs. 
* **Implementation variations:** If you are building open-source models, some also have wildly different behavior in open source tools (e.g. Qwen 7B faster than Phi 3B in vLLM due to implementation issues).

#### What About Effective Use of Prompting?

Every frontier lab extensively uses prompting to help target specific behaviors for specific evaluations. You will have to figure out how this applies to your domain.

#### How to Use Inference Scaling Laws

The intuition of inference scaling laws is based on the observation that if your model CAN generate the correct answer sometimes, then scaling inference up can make that more reliable.
It is also expected that future inference-scaled training will learn new behaviors. I believe this reflects the fact that more expensive models, where you pay more per token generated, tend to produce better results. It appears this also applies for pre- and post-training, even if inference costs were fixed. Spending more money per token gives better results.

Nathan goes into this in more detail in his post [OpenAI’s Strawberry, LM self-talk, inference scaling laws, and spending more on inference](https://www.interconnects.ai/p/openai-strawberry-and-inference-scaling-laws){:target="_blank"}. 

### Reinforcement Fine Tuning

Back to [Nathan's NeurIPS 2024 presentation](https://docs.google.com/presentation/d/1LWHbtz74GwKSGYZKyBVUtcyvp8lgYOi5EVpMnVDXBPs/edit#slide=id.p){:target="nl-neurips2024"}, which was published four months after the blog post, he discusses OpenAI's recently announced RL approach called [Reinforcement Fine Tuning]({{site.glossaryurl}}/#reinforcement-fine-tuning){:target="_glossary"}[^2] (RFT), which is described in [this OpenAI page](https://openai.com/form/rft-research-program/){:target="openai-rf"} (no longer online!). He also discusses RFT in [this Interconnects post](https://www.interconnects.ai/p/openais-reinforcement-finetuning){:target="openai-rf"}. 

[^2]: Nathan spells it _finetuning_, but we spell it as two words. Often, people hyphenate it: _fine-tuning_.

Here is a description of RFT adapted from the presentation:

{: .attention }
> **What Is Reinforcement Fine Tuning?**
>
> Reinforcement fine tuning uses repeated passes over the data with reinforcement learning (RL) to encourage the model to figure out more robust behaviors in domains.
> 
> It requires:
> 
> 1. Training data with explicitly correct answers.
> 1. A grader (or extraction program) for verifying outputs.
> 1. A model that can sometimes generate a correct solution. _Otherwise, there will be no signal for RL to learn from._
>
> Key innovation: 
> 
> **It improves targeted skills reliably without degradation on other tasks.**

RFT has since been [launched as a product feature](https://platform.openai.com/docs/guides/reinforcement-fine-tuning){:target="_blank"} by OpenAI and it appears they have published very little about it themselves, since the initial web page disappeared. See [this independent post](https://medium.com/@joycebirkins/deep-dive-into-openais-reinforcement-fine-tuning-rft-step-by-step-guide-comparison-to-b0692743d079){:target="_blank"} on how to use the product feature. If OpenAI is successful with their product offering, it will greatly increase the available domain-specific tuned models.

RFT is entirely focused on conventional model tuning, but it may fit our goals of finding general ways to assure desired behavior in an incremental fashion. In fact, this paper, [Reinforcement Fine-Tuning Naturally Mitigates Forgetting in Continual Post-Training](https://arxiv.org/abs/2507.05386){:target="_blank"}, compares SFT and RFT, finding the latter superior for avoiding _catastrophic forgetting_, especially in the context of continual fine tuning. Here is the abstract for that paper:

{: .attention}
> Continual post-training (CPT) is a popular and effective technique for adapting foundation models like multimodal large language models to specific and ever-evolving downstream tasks. While existing research has primarily concentrated on methods like data replay, model expansion, or parameter regularization, the fundamental role of the learning paradigm within CPT remains largely unexplored. This paper presents a comparative analysis of two core post-training paradigms: supervised fine-tuning (SFT) and reinforcement fine-tuning (RFT), investigating their respective impacts on knowledge retention during CPT. Our experiments are conducted on a benchmark comprising seven diverse multimodal tasks, utilizing Qwen2.5-VL-7B-Instruct as the base model for continual post-training. The investigation yields two significant findings: (1) When continuously learning on downstream tasks, SFT leads to catastrophic forgetting of previously learned tasks. In contrast, RFT inherently preserves prior knowledge and achieve performance comparable to multi-task training. (2) RFT successfully protects and even enhances the model's general knowledge on standard benchmarks (e.g., MMMU and MMLU-Pro). Conversely, SFT degrades general model capabilities severely. Further analysis reveals that this stability is not primarily due to explicit mechanisms like KL penalty or chain-of-thought reasoning. Instead, we identify an implicit regularization mechanism inherent to RFT as a key contributing factor. Our theoretical analysis suggests that RFT's gradient updates are naturally scaled by the reward variance, acting as a data-dependent regularizer that inherently protects previously acquired knowledge. Finally, we propose a rollout-based instance filtering algorithm to enhance the stability and efficiency of RFT. Our comprehensive study demonstrates the superiority of RFT as a robust paradigm for continual post-training.


Nathan also discusses RFT in [this Interconnects post](https://www.interconnects.ai/p/openais-reinforcement-fine-tuning){:target="openai-rf"}. 

In RFT, a _grader_ is used to verify outputs, analogous to [LLM as a Judge]({{site.baseurl}}/testing-strategies/llm-as-a-judge). Hence, it is worth exploring what suite of graders would be useful for many AI-centric [Use Cases]({{site.glossaryurl}}/#use-case){:target="_glossary"}. John Allard from OpenAI describes them in [this X post](https://x.com/john__allard/status/1865520756559614090?s=46&mx=2){:target="x"}. Graders may be useful for testing, as well as tuning.

Nathan says that the data used includes a prompt and an answer, so basically Q&A pairs, but it's not clear if OpenAI allows _open-ended_ questions and answers or if more structure is expected. 

He points out that Ai2's [Open Instruct](https://github.com/allenai/open-instruct){:target="_blank"} uses a similar approach to RFT for post training. See this paper, [TÜLU 3: Pushing Frontiers in Open Language Model Post-Training](https://arxiv.org/abs/2411.15124){:target="_blank"}. His slides include a screen shot of [this Ai2 dataset on HuggingFace](https://huggingface.co/datasets/allenai/RLVR-IFeval/viewer/default/train?row=0&views%5B%5D=train){:target="_blank"}, which is part of the Tülu 3 release, a dataset containing instruction-following data formatted for use with Ai2's [Open Instruct](https://github.com/allenai/open-instruct){:target="open-instruct"} system, specifically supporting [Reinforcement Learning with Verifiable Rewards]({{site.glossaryurl}}/#reinforcement-learning-with-verifiable-rewards){:target="_glossary"} (RLVR). 

OpenAI uses a special LM to extract the answer for reward computation. Nathan cites the example challenge of recognizing that, for example, "`.05`, `1/20`, `\frac{1}{20}` (LaTex), `5E-02`, and `5 x 10^-2`, …" all refer to the same value and the answer extractor needs to account for such differences.

### Concluding Advice

The talk concludes with the following summary (lightly edited):

1. Data is always the most important part of these processes.
2. You need your own evaluations.
3. Still a lot of under-explored research in fine tuning from instruct models. 
4. RL fine tuning will open up a lot more domains where specific correctness matters.
5. For behavior control, SFT/IFT (supervised/instruction fine tuning) is still your best bet.
6. Preference tuning is largely not worth spending time on for now. It requires high effort, it's a new research topic, and it mostly just delivers style and small performance gains.


---
