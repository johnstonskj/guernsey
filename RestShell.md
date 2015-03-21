# Introduction #

An example of the Guernsey API in use, this is a simple interactive shell that allows you to access and inspect REST services from the command line.

# Usage #

The shell must be started with a single parameter, the root URL for the service to inspect.

```
$ resh http://www.thomas-bayer.com/sqlrest/
> pwd
http://www.thomas-bayer.com/sqlrest/
> set Accepts=*/xml
> set
Accepts=*/xml
> cd CUSTOMERS/
> pwd
http://www.thomas-bayer.com/sqlrest/CUSTOMERS/
> head
200 OK
{'connection': 'close',
 'content-length': '99',
 'content-type': 'application/xml',
 'date': 'Thu, 03 Nov 2011 15:31:46 GMT',
 'server': 'Apache-Coyote/1.1'}
```

The shell supports command completion, just hit the tab key twice at the prompt to suggest commands. Also the `help` command provides a brief description of each shell command.

# Commands #

  * `! [command]` - Execute a command in a sub-shell.
  * `cd path` - Resolve path against the current working resource and change URL.
  * `debug [On|Off]` - Either display the current debug status, or set it.
  * `delete` - Delete the current resource.
  * `exit` - Exit the shell.
  * `filter [name=On|Off]` - Either display the current status of system filters, or set the state of a specific filter.
  * `get [ouputfile]` - Retrieve the current URL entity ; if specified the returned entity will be written to `outputfile`.
  * `head` - Retrieve the current resource headers only.
  * `help` - Display help on built-in shell commands.
  * `options` - Retrieve the options for current resource.
  * `post [@filename] [content-type]` - Post content to the resource, if you specify the file name it's content will be read, otherwise all content entered manually until two blank lines will be sent. Note that the second parameter will set the Content-Type header and will override any value you specified with the `set` command.
  * `put [@filename] [content-type]` - Put content to the resource, if you specify the file name it's content will be read, otherwise all content entered manually until two blank lines will be sent. Note that the second parameter will set the Content-Type header and will override any value you specified with the `set` command.
  * `pwd` - Print current target URL.
  * `query [query_params]` - Either display the current query parameters, or set new query parameters.
  * `set [key=value]` - Either display the current request settings, or define a new request setting by providing an HTTP request header key and value.

Any command can be run asynchronously by appending the '&' character to the command and its arguments, all stdout and stderr will be written to the console as normal.

# Files #

The `resh` shell uses two files during startup.

  * `~/.resh_history` - the readline history file, this i read during startup and written during exit of the shell.
  * `~/.reshrc` - an initialization file, this is read after the URL passed to the shell is processed and so any commands in this file apply to the resource created for that URL. Note that it is common to provide often used headers in the `.restrc` file.