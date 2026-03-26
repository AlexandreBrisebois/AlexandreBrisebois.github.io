
The previous version of this blog lived on WordPress. That sentence alone should explain the impulse to start over.

It's not that WordPress is broken. It does what it promises. But every update felt like a negotiation — plugins drift, themes conflict, and somewhere beneath it all, your actual content is locked in a database you technically own but practically can't touch without a GUI.

I wanted something different. A blog that lives in a Git repository. That builds to static HTML. That deploys to a CDN in minutes and costs nothing to run at scale.

Hugo gives me that. A pull request is a draft. A merge is a publish. The entire editorial workflow is a `git log`.

There's something honest about this approach. The writing is the source. Not a row in a database, not a JSON blob from an API — a plain text file with a date and some frontmatter. Readable without a browser. Editable without a login.

I'm not anti-CMS for ideological reasons. I'm anti-CMS because I've watched too many content systems become the main character of their own story. The tool starts serving itself instead of the writer.

A CMS that requires maintenance, updates, plugins, and credentials is infrastructure. Infrastructure that produces content. That inversion is the problem.

This is the opposite of that. The writing is the infrastructure. Everything else is just a build step.

