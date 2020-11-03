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

**Note: this is partly outdated - Docker is no longer required and conda may be used in place of it**

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

Updating versions
=================

Steps to update ads-deploy:

1. Update ads-ioc-docker (follow its README)
2. Tag and release pytmc (use v0.0.0 style as usual)
3. Update the `FROM` pcdshub/ads-ioc version
4. Update environment variables: `PYTMC_VERSION`, `ADS_IOC_VERSION`
5. Rebuild. Match the `ADS_DEPLOY_VERSION` with the pytmc version, as it
   tends to change the most:
    ```
    $ export ADS_DEPLOY_VERSION={pytmc version}
    $ docker build -t pcdshub/ads-deploy:${ADS_DEPLOY_VERSION} .
    $ docker build -t pcdshub/ads-deploy:latest .
    ```
6. Push to DockerHub
    ```
    $ docker push pcdshub/ads-deploy:${ADS_DEPLOY_VERSION}
    $ docker push pcdshub/ads-deploy:latest
    ```
7. Commit, tag, and push to GitHub
    ```
    $ git tag ${ADS_DEPLOY_VERSION}
    $ git push
    $ git push --tags
    ```

Links
=====

* [Docker Hub](https://hub.docker.com/r/pcdshub/ads-deploy/tags)
