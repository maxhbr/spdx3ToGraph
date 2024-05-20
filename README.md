# spdx3ToGraph

Create a visualization of SPDX 3.0 documents.

spdx3ToGraph converts an SPDX 3 JSON-LD file to a graph, using
[PlantUML](https://plantuml.com/) textual description.

The resulting output can be use as an input to a visualization tool like one on
[www.plantuml.com](http://www.plantuml.com) to get a PNG image, a SVG vector
graphic, or an ASCII Art.

To get started, run the following:

```shell
nix develop
poetry run python -m spdx3_to_graph -- -v test_data/package_sbom.json 
```

The output will be the lines between `@startuml` and `@enduml`.

[Nix](https://nixos.org/) is required to create a running environment for
spdx3ToGraph.

In some machine configurations, you may need to replace the `nix develop` line
with
`nix develop --extra-experimental-features nix-command --extra-experimental-features flakes`.

```shell
nix develop --extra-experimental-features nix-command --extra-experimental-features flakes
poetry run python -m spdx3_to_graph -- -v sbom.json > sbom.puml
```

Your SBOM visualization will be in `sbom.puml` file.
