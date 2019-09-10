ads-deploy docker image + tools
===============================

ads-deploy bridges the gap between your PLC project in TwinCAT XAE + Visual Studio and the
Python/EPICS tools we use for development and deployment ([PyTMC](https://github.com/slaclab/pytmc), 
[ads-ioc](https://github.com/pcdshub/ads-ioc)) by providing a full EPICS and Python environment
in a containerized Docker image.

Features
========

* pytmc pragma linting / verification
* Build and run ads-based EPICS IOCs directly from Windows
* Generate batch files to run the IOC outside of Visual Studio
* Auto-generate and run simple Typhon screens directly from Windows
* No need to transfer your project and files to a Linux machine just to generate the IOC

Installation
============

Step-by-step notes are available here:
https://confluence.slac.stanford.edu/display/PCDS/Installing+ads-deploy+on+Windows

Using just the Docker container is simple on all platforms. Run the following to check it out:

Windows
```sh
C:\> docker run -it pcdshub/ads-deploy:latest /bin/bash
```

OSX / Linux
```sh
$ eval $(docker-machine env)
$ docker run -it pcdshub/ads-deploy:latest /bin/bash
```

Links
=====

* [Docker Hub](https://hub.docker.com/r/pcdshub/ads-deploy/tags)
