# Security policy

Please report vulnerabilities privately to dev@atalay.biz, not in a public issue.
Include the affected RenderCV version and the steps or files that reproduce the problem.

RenderCV is meant to render CVs and themes that you trust. A CV can read local files,
download photos, and contain Typst code, and a custom theme runs Python code. These are
features, so a CV that uses them isn't a vulnerability. A service that renders other
people's CVs must isolate each render from its secrets, other users' files, and the
network.
