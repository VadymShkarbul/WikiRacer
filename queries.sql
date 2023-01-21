-- Get top 5 most popular articles
-- (those with the most links to themselves)
SELECT name as page_name, COUNT(name) as link_count
FROM link
GROUP BY name
ORDER BY link_count DESC
LIMIT 5;

-- Top 5 articles with the fewest links to other articles
-- not the biggest, because in my case for most links it is 200
SELECT page.name as page_name, COUNT(link.id) as link_count
FROM page
JOIN link ON page.id = link.page_id
GROUP BY page.id
ORDER BY link_count --DESC
LIMIT 5

-- My implementation of the find_path() method
-- do not allow me to perform the other two queries
-- because I do not identify the search levels in my code.
-- I had a solution for this, but this is not the code
-- that should be shared with a future employer ;)

