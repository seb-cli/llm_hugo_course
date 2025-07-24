# ---
# deploy: true
# cmd: ["modal", "serve", "10_integrations/streamlit/serve_streamlit.py"]
# ---

# # Run and share Streamlit apps

# This example shows you how to run a Streamlit app with `modal serve`, and then deploy it as a serverless web app.

# ![example streamlit app](./streamlit.png)

# This example is structured as two files:

# 1. This module, which defines the Modal objects (name the script `serve_streamlit.py` locally).

# 2. `app.py`, which is any Streamlit script to be mounted into the Modal
# function ([download script](https://github.com/modal-labs/modal-examples/blob/main/10_integrations/streamlit/app.py)).

import os
import shlex
import subprocess
from pathlib import Path

import modal

# ## Define container dependencies

# The `app.py` script imports three third-party packages, so we include these in the example's
# image definition and then add the `app.py` file itself to the image.

# reflex_script_local_path = Path(__file__).parent / "word_map/word_map.py"
# reflex_script_remote_path = "/root/word_map/word_map.py"
reflex_script_local_dir = Path(__file__).parent  
reflex_script_remote_dir = "/root/"


image = (
    modal.Image.debian_slim(python_version="3.13")
    .apt_install(["unzip", "curl"])
    .pip_install("modal==1.1.0","reflex","python-dotenv==1.1.1","PyMuPDF==1.26.3","httpx==0.28.1","openai==1.97.1")
    # .add_local_file(
        # reflex_script_local_path,
        # reflex_script_remote_path,
    # )
    .add_local_dir(
        reflex_script_local_dir,
        reflex_script_remote_dir,
    )
)

app = modal.App(name="word_map", image=image)

if not reflex_script_local_dir.exists():
    raise RuntimeError(
        "word_map DIR not found!"
        # "word_map.py not found! Place the script with your reflex app in the same directory."
    )

# ## Spawning the Streamlit server

# Inside the container, we will run the Streamlit server in a background subprocess using
# `subprocess.Popen`. We also expose port 8000 using the `@web_server` decorator.

@app.function(secrets=[modal.Secret.from_name("openrouter-secret")])
def f():
    print(os.environ["OPENROUTER_API_KEY"])

@app.function()
@modal.concurrent(max_inputs=100)
@modal.web_server(8000)
def run():
    # target = shlex.quote(reflex_script_remote_path)
    cmd = f"REFLEX_API_URL=http://0.0.0.0:8000 reflex run --env prod" # {target} --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false"
    subprocess.Popen(cmd, shell=True)


# ## Iterate and Deploy

# While you're iterating on your screamlit app, you can run it "ephemerally" with `modal serve`. This will
# run a local process that watches your files and updates the app if anything changes.

# ```shell
# modal serve serve_streamlit.py
# ```

# Once you're happy with your changes, you can deploy your application with

# ```shell
# modal deploy serve_streamlit.py
# ```

# If successful, this will print a URL for your app that you can navigate to from
# your browser �� .
