<div align="center">
  <h1><code>Mapping the Internet</code></h1>
  <p>
    <strong>Code du cours de GRAAL à l'École Centrale de Nantes.</strong>
  </p>
  <p>
    <img alt="logo ECN" src="https://upload.wikimedia.org/wikipedia/fr/thumb/c/c0/Logo_ECN.svg/1200px-Logo_ECN.svg.png" height="300" width="475">
  </p>
</div>

# Wikipedia mapper

First go to the correct directory

```bash
cd wikipedia_mapper
```

## Install dependencies

```bash
pip install scrapy
```

## Scrap wikipedia links

```bash
scrapy crawl wikipedia -o output.json
```

## Convert json file to graph format

```bash
python3 graph_converter/convert.py
```

This should produce a `graph.dot` file.

## Display the graph

Use your favorite software to display the graph (the DOT format should be supported). In our case we used [gephi](https://gephi.org/).
