<div align="center">
  <h1><code>Mapping the Internet</code></h1>
  <p>
    <strong>Code du cours de GRAAL à l'École Centrale de Nantes.</strong>
  </p>
  <p>
    <img alt="logo ECN" src="https://upload.wikimedia.org/wikipedia/fr/thumb/c/c0/Logo_ECN.svg/1200px-Logo_ECN.svg.png" height="300" width="475">
  </p>
</div>

## Install dependencies

```bash
pip install scrapy
```

## Scrap wikipedia links

```bash
cd wikipedia_mapper
scrapy crawl wikipedia -o output.json
```
