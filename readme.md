<h1 align="center">HTTP SERVER</h1>
<p align="center">
    <img src="https://img.shields.io/badge/%20python-3.11.3-blue?style=for-the-badge&logo=Python" alt="python">
    <img src="https://img.shields.io/badge/%20asyncio-latest-brightgreen?style=for-the-badge" alt="asyncio">
    <img src="https://img.shields.io/badge/%20socket-latest-brightgreen?style=for-the-badge" alt="socket">
    <img src="https://img.shields.io/badge/%20mytime-week-red?style=for-the-badge" alt="mytime">

</p>

<h2>About</h2>

*__HTTP Server for your web applications or other needs. All features implementing on native python with AsyncIO and Socket modules. Mainly, this project aims to show how to work with HTTP protocol combine with TLS security, and ofcourse asynchronous tasks.__*

_Features_:
- [ ] _Secure connection between client and server with TLS_
- [x] _Accept connections from client and handle request_
- [x] _Send client request through proxy to web application_
- [x] _Balancing requests between multiple web applications_
- [ ] _Logging underhood stuff and connections_
- [ ] _Providing some useful commands with server CLI_
- [ ] _Serving static files_

> All features above is asynchronous, don't worry

<h2>Installation</h2>

> Well, actually, you have two routes from here: `DockerHub` or `GitHub`

__Installation from GitHub__:

- _Save project archive or clone repo on your local machine_
- _Install python from <a ref="https://www.python.org/downloads/">official site</a>_
- _Install project from it's directory:_ `python -m pip install -e .`
- _Configurate server with file (examples inside):_ `https-server/src/configurations/config.ini`
- _Now, you have to choices how to start server:_ `combine this two ways all you want`
    - _with settings from config file:_ `serv`
    - _with settings from shell arguments:_ `serv -H host -P port -M max_connections`

__Installation from DockerHub__:

> Currently, not implemented
