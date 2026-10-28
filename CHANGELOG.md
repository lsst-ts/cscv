# Change log

cscv is versioned with [semver](https://semver.org/).
Dependencies are updated to the latest available version during each release, and aren't noted here.

Find changes for the upcoming release in the project's [changelog.d directory](https://github.com/lsst-dm/cscv/tree/main/changelog.d/).

<!-- scriv-insert-here -->

<a id='changelog-v0.3.1'></a>
## v0.3.1 (2026-10-28)

### Backwards-incompatible changes

- EFD credentials are now read from the file in `EFDAUTH` environment variable.
- lsst-efd-client updated to version 1.1.2.
- Requires Python 3.13 or later.

### Bug fixes

- CSCs whose topic is missing from the EFD schema are now shown with "no data" instead of being left off the page.

### Other changes

- Update to Starlette 1.x.
- Run CI on Python 3.14 to match the Docker image.
- Update ruff and the shared ruff configuration.
