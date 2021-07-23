# speckle-webhooks-example

This is a simple example of what you can do using Speckle Stream Webhooks. 

Requests from the Speckle Server are consumed and formatted to then be sent to Discord:

![example-messages](https://user-images.githubusercontent.com/7717434/126758892-3bb465af-56ba-4574-ae58-72a4772b1996.png)
![stream-update-example](https://user-images.githubusercontent.com/7717434/126792981-0e20b52e-4eda-45fc-bf62-50332ebbbf1b.png)
![commit-update-example](https://user-images.githubusercontent.com/7717434/126761699-acba440f-7c13-4660-afa9-90f25af65747.png)

## Setup

You'll need access to a Speckle Server (or use our public one, [speckle.xyz](https://speckle.xyz/)). Create some webhooks on the server to get started. 

![create-webhook](https://user-images.githubusercontent.com/7717434/126762211-97caab23-fdf2-49e8-9dee-7724689a699f.png)


Fill in your `.env` file based on the `.env-example`:
 - `SECRET`: the secret you used to set up the webhooks. note that it is assumed that all your webhooks have the same secret
 - `SPECKLE_TOKEN`: (optional) you can generate this from your profile online. this is only used for the `commit_created` event
 - `DISCORD_URL`: generate this by going to a discord channel's settings > integrations > webhooks > new webhook

![generate discord webhooks url](https://user-images.githubusercontent.com/7717434/126759731-d624b7be-e5af-428a-b11b-a1f18828207b.png)

## Developing

### Dependencies

This project uses [poetry](https://python-poetry.org/docs/) for package management. Follow the [docs](https://python-poetry.org/docs/#installation) to install.

If this is your first time using poetry and you're used to creating your virtual environments within the project directory, run `$ poetry config virtualenvs.in-project true` to configure poetry to do the same.

To bootstrap the project environment run `$ poetry install`. This will create a new virtual-env for the project and install both the package and dev dependencies.

If you don't want to use poetry, you can roll your own virtual env and install the specified dependencies in the `pyproject.toml`.

### Start

To start up, simply run the `run.py` file in the root directory.