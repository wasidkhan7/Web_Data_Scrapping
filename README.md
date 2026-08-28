## Pagination strategies

| Site | Pattern | Why |
|---|---|---|
| books.toscrape.com | Follow `<li class="next">` link | No assumption about total page count; works even if the site's page count changes |
| webscraper.io | Increment `?page=N`, stop on empty result | Predictable URL scheme allows this; demonstrates the query-param pattern common on e-commerce/admin sites |
| quotes.toscrape.com/js | Click a "Next" button, stop when it's no longer clickable | Content is JS-rendered, so there's no href to follow directly — pagination happens through browser interaction, not a static link |


# Books scrapped data  using beautifulSoap
<img width="1791" height="726" alt="image" src="https://github.com/user-attachments/assets/32ee7f5d-0446-4898-be75-6d3c8bb445da" />

# Laptop scrapped data using beautifulSoap
<img width="1803" height="760" alt="image" src="https://github.com/user-attachments/assets/7f548905-2b29-484a-8af4-5d2b4319f96e" />

# Quotes scrapped data using selenium
<img width="1826" height="757" alt="image" src="https://github.com/user-attachments/assets/737b1549-7f71-4f40-bbff-09cd9f0eb13c" />

