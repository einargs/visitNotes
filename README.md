# Frontend
The source for the frontend website is in `frontend-site`.

You'll need Node.js 18+ installed. If your package manager doesn't have it,
you can download it from (here)[https://nodejs.org/en/download/current].
We're using pnpm. To install it, go
(here)[https://pnpm.io/installation#using-npm].

To run the frontend in development mode, `cd` into `notes-site` and run
`pnpm run dev`.

Because pnpm doesn't want to provide an easy way to turn their lockfile into a
normal package-lock.json file, we need to run `npm i --package-lock-only` to
update the lockfile so that nix can read it to build everything. We'll probably
need to transition over to using only npm, but for now that would be a pain
because of the way shadcn-ui is configured.

# Backend
We're going to use Quart (basically Flask but for asyncio), python-socketio,
which has better support for sessions and also works with asyncio. To run it,
we're using hypercorn. As such, just run:
```
hypercorn src/app:asgi -b [::1]:8000
```

See hypercorn docs for more.

## Transcript
Eventually the transcript should contain objects that indicate whether the
doctor or patient is speaking. Every time a recognized event is fired we'll
add that to the transcript list, and use speaker recognition to tell whether
it's the doctor or patient. (We may not be able to tell whether it's the doctor
or patient who is speaking, in which case I suppose it'll be an object with a
speaker id note.)

Then, when turning it into documents for langchain, we can try and condense
multiple sentences in sequence from the same speaker into one document. There
are also other kinds of metadata it might allow us to annotate with.

It's important to remember that there can easily be more than two people
speaking to a doctor in a meeting.

TODO: this has gotten out of date. Talk to Kiriti.

# Virtual Machine
## Building Local
To build a virtual machine on nixos for local testing, first go into
`vm/config.nix` and uncomment the import of `./local.nix`. Then do:
```
nixos-rebuild build-vm --flake .#azure-vm
```

Then run the command it prompts you to run. Then you can ssh into it with:
```
ssh -p 8022 mtsu@localhost
```

You'll need to add the selfsigned.crt file to your browser's certificate
management. Going to localhost:8000 will get you the http port, which will try
to redirect you to ssl but fail because this is a different port than in
production. So go straight to https with `https://localhost:8443`.

If you don't know the password you can edit the `hashedPassword` option in
`vm/config.nix` to use the output of running `mkpasswd`.

You'll also need to copy the `.env` file into `/var/lib/site-backend` on the
virtual machine once it's running.

You can use scp to copy files.
```
scp ./.env scp://mtsu@localhost:8022/env-file
```

## Building For Azure
To build the azure image, you should only need to do:
```
nix build .#nixosConfigurations.azure-vm.config.formats.azure
```

## Deploying Azure
TODO: automate this as a script with the cli.

When using the CLI, make sure to wait for various operations to complete and
deploy before continuing.

First go to the azure portal. Alternatively, log in to the azure cli with:
```sh
az login
```

The subscription id is 3ecd1513-0871-4f6f-a0e7-7411e074b783. You can set the
default subscription with:
```sh
az account set -s 3ecd1513-0871-4f6f-a0e7-7411e074b783
```

You can configure the default resource group with:
```sh
az configure --defaults group=tnhimss
```

Then go to the storage accounts (via search bar). Select mtsutnhimss, then the
containers section on the left side. Select audiobackendimage1. Upload the new
image to this as audioBackend.vhd, making sure to select the option to replace
existing images.

Or, you can use the CLI.
[CLI Docs.](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-cli#authorize-access-to-blob-storage)
```sh
az storage blob upload --overwrite \
    --account-name mtsutnhimss \
    --container-name audiobackendimage1 \
    --name audioBackend.vhd \
    --file audioBackend.vhd \
    --auth-mode login
```

With the CLI you will need to give yourself the storage blob data contributor
role.
```sh
az ad signed-in-user show --query id -o tsv | az role assignment create \
    --role "Storage Blob Data Contributor" \
    --assignee @- \
    --scope "/subscriptions/3ecd1513-0871-4f6f-a0e7-7411e074b783/resourceGroups/tnhimss/providers/Microsoft.Storage/storageAccounts/mtsutnhimss"
```

Then go to the azure compute galleries.
Remember to increment the version.
```sh
az sig image-version create --resource-group tnhimss \
    --gallery-name nixos_images --gallery-image-definition tnhimss \
    --gallery-image-version $VERSION \
    --os-vhd-storage-account /subscriptions/3ecd1513-0871-4f6f-a0e7-7411e074b783/resourceGroups/imageGroups/providers/Microsoft.Storage/storageAccounts/mtsutnhimss \
    --os-vhd-uri https://mtsutnhimss.blob.core.windows.net/audiobackendimage1/audioBackend.vhd
```

Now remember to deallocate and delete the previous the machine with:
```sh
az vm deallocate --name audioVM --no-wait \
    --resource-group tnhimss \
    --subscription 3ecd1513-0871-4f6f-a0e7-7411e074b783
```

TODO: You may be able to just run delete without a preceding deallocate,
I'm not sure.
```sh
az vm delete --name audioVM --no-wait --yes \
    --resource-group tnhimss \
    --subscription 3ecd1513-0871-4f6f-a0e7-7411e074b783
```

Create a VM using the latest version of the image definition.
- We install a public key for sshing into the machine. Contact einargs on
  discord to get access to the private key.
- TODO: I don't know yet if we need to allocate data disks or not. I don't think
  so.
- We use a 5 GB os disk to just give us a bit of extra space.
- We can use `--public-ip-address-allocation static` to make a newly allocated ip
  address static.
- We can use `--public-ip-address` to attach to an existing public ip address
  with a given name and keep it stable. This will be important for when the DNS
  to resolve a url is configured.
- We use a `Standard_B1s` which is very cheap but only has 1 GB of RAM.
- The `Standard_B1ls` is half the price for 0.5 GB of RAM.
- Delete options when creating a VM:
  [docs](https://learn.microsoft.com/en-us/azure/virtual-machines/delete?tabs=cli2%2Ccli3%2Cportal4%2Cportal5#set-delete-options-when-creating-a-vm).
```sh
az vm create -g tnhimss -n audioVM \
    --image /subscriptions/3ecd1513-0871-4f6f-a0e7-7411e074b783/resourceGroups/tnhimss/providers/Microsoft.Compute/galleries/nixos_images/images/tnhimss \
    --os-disk-delete-option Delete \
    --public-ip-address audioBackend-ip \
    --ssh-key-name audioBackend002_key \
    --size Standard_B1s \
    --os-disk-size-gb 5
```

Right now you'll then need to go into the portal and change the network
interface to allow HTTP and HTTPS. TODO: find command for this.

## Connecting to Azure
To ssh into it you can do:
```
ssh -i ~/.ssh/audioBackend002_key.pem mtsu@audio.einargs.dev
```
Currently you do not need the key and just the password is enough, but I am
working on fixing this. I think I need to change the settings in the openssh.

To copy the env file over into `/home/mtsu/env-file`, you can do:
```
scp -i ~/.ssh/audioBackend002_key.pem ./.env scp://mtsu@audio.einargs.dev/env-file
```
Then to install it you just ssh in and do:
```
sudo mv ~/env-file /var/lib/site-backend/
```

# Docker
To build the docker images, you're going to need [nix
installed](https://nixos.org/download.html).

Then, go to the root project directory and run `nix build .#docker`. This will
install all of the tools, build everything, and then place it in `./result`. You
can then load it into docker with `docker load < ./result`.

Then to run it locally, do:
```
docker run --env-file=./.env -p 8000:80 -t visit-notes:latest
```
This launches the docker with environment variables taken from the .env file --
which `load_dotenv` also uses -- which is where we keep all of the api keys for
chatgpt and azure speech recognition. It then binds the local port 8000 to the
port 80 on the docker container, allowing you to load the website with
`localhost:8000`. Then it attaches it to the terminal so that we can see output
and any errors.

To open a shell inside the container you'll want to run:
```
docker run -p 8000:80 --env-file=./.env -it --entrypoint=/bin/sh visit-notes:latest -i
```

You can mount an external file or folder via the mount argument. This mounts a
folder test in the working directory as `/test` in the root of the container.
```
--mount type=bind,source="$(pwd)"/test,target=/test
```

This is very important, because azure speech services only outputs internal
errors to a logfile. You can control the path of this by setting the
`SPEECH_LOG_FILE` environmental variable.

A good default run command is:
```
docker run -d --env-file=./.env -p 8000:80 --env SPEECH_LOG_FILE=/speech-log.txt \
  --mount type=bind,source="$(pwd)"/speech-log.txt,target=/speech-log.txt \
  -t visit-notes:latest
```

This uses `-d` to run it in the background. To stop it, use `docker ps` to list
all running containers and get the id, and then do `docker stop <container-id>`.
You will need to do this even if you run it without `-d`.

# Pydoc
You may need to call `python -m pydoc -b` to launch pydoc as aware of packages
installed in the virtual environment.

## Doctor vs. Patient
One nice feature might be writing a module to determine whether the doctor or
patient is speaking.

# Queries/Pie in the Sky
- We can enable the user to request the AI to make changes to the summary. "Hey,
  the patient said it started two days ago, not one day ago." etc.
- We can highlight important information in the transcript.
  - Clicking on it could bring up a context menu to include it in the summary or
    find related medical codes?
