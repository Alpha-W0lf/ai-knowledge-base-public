# Choosing an MCP transport: stdio versus HTTP

The Model Context Protocol defines how a client and a server exchange messages, and it supports more than one transport. The choice of transport decides who can reach the server and therefore what authentication it needs.

## Local stdio

With the stdio transport, the client launches the server as a child process and talks to it over standard input and output. Nothing listens on a network port. Only the local user who started the client can reach the server, and the server runs with that user's permissions. For a local knowledge base or a developer tool, stdio is the simplest and safest option: there is no network attack surface and no authentication to build.

The trade-off is that each client runs its own copy of the server, and the server must be installed on the same machine.

## Streamable HTTP

The HTTP transport, called Streamable HTTP in recent versions of the specification, runs the server as a web service that clients reach over the network. It replaced an earlier design based on server-sent events. HTTP makes sense for shared or hosted servers used by many clients, but it brings every web-service concern with it: TLS, authentication, authorisation, rate limiting and protection against cross-site requests.

## Authorisation for remote servers

The specification describes an authorisation flow based on OAuth 2.1 for HTTP servers. The client obtains an access token and presents it with each request, and the server validates the token and its scopes before running a tool. Servers should check that tokens were issued for them specifically, rather than passing tokens through to other services.

A server bound to localhost is not automatically safe: web pages in a local browser can sometimes send requests to localhost ports, so validate the Origin header and require authentication even for local HTTP servers.

## A simple rule

Use stdio for anything that runs on the user's own machine. Move to HTTP only when the server genuinely must be shared, and then treat it as a production web service with authentication on every request, least-privilege scopes per tool, and logging of who called what.
