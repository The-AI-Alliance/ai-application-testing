---
layout: default
title: LLM as a Judge
nav_order: 320
parent: Testing Strategies and Techniques
has_children: false
---

# LLM as a Judge

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

In _LLM as a Judge_, a separate model, one that is very smart and also usually expensive to use or otherwise not suitable for production use in your application, serves as a _judge_ to generate Q&A pairs for the benchmarks. 

The judge model can also be used to decide whether or not the application model's response to a particular question is sufficiently close to the expected answer.

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> TODO

## Variations

### Voting

## Tools

Popular frameworks for implementing [_evaluations_](https://the-ai-alliance.github.io/trust-safety-evals/){:target="tsei"} include [`unitxt`](https://www.unitxt.ai){:target="unitxt"} and [`lm-evaluation-harness`](https://github.com/EleutherAI/lm-evaluation-harness){:target="lm-eval"}.

IBM Research recently open-sourced [EvalAssist](https://ibm.github.io/eval-assist/){:target="eval-assist"}, which makes writing `unitxt`-based evaluations easier. Specifically, EvalAssist is an application that simplifies using implementing evaluations using LLM as a Judge. It also helps users refine evaluation criteria iteratively using a web-based user experience. 

## An Example

An example of using an LLM as a judge can be found in the [IBM Granite Community](https://github.com/ibm-granite-community){:target="igc"}, in the [Granite &ldquo;Snack&ldquo; Cookbook](https://github.com/ibm-granite-community/granite-snack-cookbook){:target="igc-snack"} repo, under the [`recipes/Evaluation`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation){:target="igc-snack-eval"} folder. The _recipes_ in this folder use `unitxt`. They only require running [Jupyter](https://jupyter.org/){:target="jupyter"} locally, because all inference is done remotely by the community's back-end services:

* [`Unitxt_Granite_as_Judge.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Granite_as_Judge.ipynb){:target="igc-snack-eval3"}

In addition, these notebooks demonstrate other aspects of using `unitxt`:

* [`Unitxt_Quick_Start.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Quick_Start.ipynb){:target="igc-snack-eval1"} - A quick introduction to `unitxt`.
* [`Unitxt_Demo_Strategies.ipynb`](https://github.com/ibm-granite-community/granite-snack-cookbook/tree/main/recipes/Evaluation/Unitxt_Demo_Strategies.ipynb){:target="igc-snack-eval2"} - Various ways to use `unitxt`.

# Issues You Have to Consider

1. How do you validate that the judge model is producing good Q&A pairs or accurately evaluating the student model's results, depending on the usage pattern? Most likely, some human inspection of the Q&A pairs and possibly some test results will be necessary, until sufficient confidence is established. [Statistical techniques]({{site.baseurl}}/testing-strategies/statistical-tests) will be useful in establishing confidence. 
2. If the judge model is expensive or slow, how do you use it economically? On the other hand, it won't be used during normal inference, just for the testing process, so the higher inference costs may not really matter.
3. ...

TODO

---

Review the [highlights](#highlights) summarized above, then proceed to [Statistical Tests]({{site.baseurl}}/testing-strategies/statistical-tests/).
