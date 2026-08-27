## Pagination strategies

| Site | Pattern | Why |
|---|---|---|
| books.toscrape.com | Follow `<li class="next">` link | No assumption about total page count; works even if the site's page count changes |
| webscraper.io | Increment `?page=N`, stop on empty result | Predictable URL scheme allows this; demonstrates the query-param pattern common on e-commerce/admin sites |