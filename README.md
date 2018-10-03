# TDD Hack

I'm noodling around with some software testing ideas that occurred
to me recently. The context is that I work on a large-ish project
with way too little automated testing, and I'd like to retrofit as
much testing as I can without disrupting our roadmap work.

One thing about this system is that running a job often takes several
hours, so I'd love to do something clever with mocks that makes a
"job" run in seconds or minutes. Also I'd like, as much as possible,
to be able to test pieces in isolation. I can do this with some
pieces, but a lot of pieces are too dependent upon what came before.

I know how to do TDD on a small scale, but I'm interested in trying
TDD at a larger scale, encompassing larger subsets of the system.

I'm also interested in adopting more of an "architect for testability"
mindset, and what would be involved in retrofitting that to the
existing system.

## Modules

A module has an API, and a Mock version and a Real version.
The Mock version is shared across the team and changes slowly
or not at all. The Real version can change quicker, and
implements the actual functionality. So the Mock is a
shallow placeholder for functionality.

Plan for the Real version to inherit from the Mock version,
that ensures API compliance.

Mocks can do a lot of logging, and part of that logging connects
to instrumentation that confirms that integration requirements
are met. These might be specified in a domain-specific language
and might include pre- and post-conditions for how things
interact. Ideally the logging could be enabled with the Real
versions as well.

## Where to go next with this

An obvious thing would be to start adapting this to some non-trivial
example project. Maybe set up some little web server and throw requests
at it and make sure it does the right things at the right times.

Also, it might be nice to have some way to select which Python classes
should run as mocks and which should run as real. Maybe something like

    python hack.py --mocks-except MyFavoriteClass

That doesn't explain how you'll implement it, but it's a starting point.
