# README for the `open-webui` Directory

This directory is used to run and configure [Open WebUI](https://docs.openwebui.com) as a nicer interface for the ChatBot application. See the [user guide's](https://the-ai-alliance.github.io/ai-application-testing/) section [Using the ChatBot with Open WebUI](https://the-ai-alliance.github.io/ai-application-testing/working-example/#using-the-chatbot-with-open-webui) for details.

Contents:

* `README.md`: This file
* JSON configuration file, `open-webui.config.json`: It is loaded into Open WebUI to configure it to use our ChatBot's API server.
* `pyproject.toml`: Rather than include the `open-webui` dependencies in the project's `pyproject.toml`, we use a separate setup in this directory and run Open WebUI here.
