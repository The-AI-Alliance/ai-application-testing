---
layout: default
title: Can We Eliminate Source Code?
nav_order: 420
parent: Advanced Techniques
has_children: false
---

# Can We Eliminate Source Code?

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

<a id="highlights"></a>

{: .tip}
> **Highlights:**
>
> 1. Plain text source code dominates software development, because of its relative flexibility, human readability, and ease of use by tools.
> 1. Plain text source code requires learning and correctly using a programming language.
> 1. Attempts to replace plain text source code have only succeeded in a few, special cases.
> 1. Generative AI has the potential of replacing source code with a _richer_ representation that reduces or eliminates the disadvantages of source code.
> 1. A new representation will have have the following requirements (at least):
>     1. Support enough human understanding for purposes of ensuring requirements are met and to allow detection of and fixing bugs and other issues.
>     1. Include a component library with very clear, unambiguous interfaces and behaviors, so LLMs can effectively compose applications from them.
>     1. Retrain application-generation LLMs on examples using the new representation so generation works effectively.
> 1. Given the roadblocks, maybe we shouldn't try to abandon source code, but instead use the refactoring capabilities of LLMs to more aggressively improve all aspects of our languages, libraries, and tools, replacing suboptimal and deprecated aspects of them once and for all.

## Why Do We Use Source Code in the First Place?

Almost all software in existence was written using a structured form of plain text: a programming language. Plain text dominates because it can be very flexible, it is human readable, and it requires the least effort to build tools that can translate plain-text source code into applications and other tasks. However, it also has several disadvantages:

* To write an application, you need to learn the programming language and tools for building, testing, and deploying the application.
* It is very easy to make mistakes, from small typos to logic errors, which may or may not be caught by our tools.
* A compiler or interpreter is necessary to translate the text into a machine-executable form.
* Besides the core logic of the application, there are static and runtime dependencies that are poorly captured in source code, and extracting this information for various tasks requires specialized tools that aren't always available.
* Other tools are needed for application analysis and maintenance purposes.
* and so forth...

Other approaches, such as &ldquo;drag-and-drop&rdquo; graphical environments have been tried, but they usually have frustrating limitations and succeed in limited circumstances. (A notable example is [LabVIEW](https://www.ni.com/en/shop/labview.html){:target="_blank"}, which provides a graphical environment for connecting laboratory instrumentation, etc.)

### Writing Applications with Generative AI

The generative AI community has rapidly improved the ability of models to automate many of the manual activities involving source code, especially code generation from prompts. This holds the promise that people with no programming abilities will be able to write applications just by asking for them with sufficiently detailed, plain English (or other native language), so called [Vibe Coding]({{site.glossaryurl}}/#vibe-coding){:target="_glossary"}.

However, current implementations still generate source code, sometimes imperfectly. For &ldquo;important&rdquo; applications, the resulting code still requires all the same engineering processes to validate it works correctly. The technology has already demonstrated significant productivity boosts, but it is still immature enough that being able to read, understand, and modify the generated source code is usually necessary to ensure the desired results.

## What Would Be Required to Replace Source Code?

If generative AI can (or will be able to) create complete applications from user prompts, it begs the question; can we finally replace source code with something better, a representation that avoids the limitations of source code?

At a minimum, the alternative would have to support a comprehensive library of [Components]({{site.glossaryurl}}/#component){:target="_glossary"} with clear, unambiguous abstraction boundaries and behaviors, so the application generation can join them together to implement the desired functionality. Also, the user will need some way to ensure correct behavior, or be assured by the system that the behavior is correct. Once deployed, these applications will still require monitoring tools, in part to support the required ability to detect, diagnose, and fix problems. 

Hence, if the alternative representation isn't human readable itself, it would need to expose enough information, let's call it _metadata_, for humans to intervene as necessary, at least until AI can perform these tasks autonomously instead. Determining the right amount metadata won't be easy, and it may turn out to be very close to just having source code itself!

One possibility is to leverage the libraries that already exist in one or more programming ecosystems. The human readable metadata could be bundled with the components and exposed in some way. Because of diverse requirements for performance, overhead, etc., e.g., running on big clusters to edge devices, it is unlikely that one representation, library, and runtime will be sufficient for all needs, but we can let the LLM worry about which environment to use, based on the prompts we provide.

Whatever the new representation is, a new generation of LLMs will have to be trained on enough examples using it so application generation is effective, like it is today for the widely-used, source-code languages, such as Java and Python.

## What if Instead We Make Source Code Better?

We listed some requirements that will be difficult to meet, especially since application generation using source code already works reasonably well and it is improving rapidly. Creating a whole new programming ecosystem is hard enough that it rarely happens, even when an established ecosystem has plenty of flaws that people love to complain about.

Instead, could we improve any perceived flaws in our existing source code approaches? Could we use them more effectively? What if we used LLMs' abilities to refactor code to aggressively and permanently fix any flaws? Historically, language communities have kept poorly-designed library components to maintain backwards compatibility, because asking a large community of developers to upgrade to &ldquo;fixed&rdquo; libraries is too much to ask, or at least it can only be done rarely and carefully.

But LLMs can quickly fix code. What if the next version of Java contained only optimally-designed components, along with LLM-based refactoring tools to quickly transform all uses of obsolete components with their better replacements? Over time, as newer versions of code-generation LLMs are trained, they will be able to generate much better, more reliable code, using only the improved components.

A related improvement language communities should do is to aggressive convert common boilerplate into robust library components, so that when LLMs generate applications, they generate _as little code as possible_, only the &ldquo;glue&rdquo; required to integrate components to implement requirements. Can we reach a place where _all_ generated applications are very concise and modular?

## What's Next?

After reviewing the [highlights](#highlights) summarized above, proceed to [From Testing to Tuning]({{site.baseurl}}/advanced-techniques/from-testing-to-tuning/).

---
