# CSE 6332 Project 5: Redis Word Counts

Aaron Pantoja

Word-count statistics for three Project Gutenberg books (Pride and Prejudice, War and Peace,
Tarzan of the Apes). Each book is one Redis hash, `book:{title}:word_counts`, with one field per
word and the count as its value.

| Path | |
|---|---|
| `word-count-app/` | The course starter with TODOs 1-5 completed; this is the folder that is submitted |
| `Dockerfile`, `start.sh`, `render.yaml` | Deployment: Node.js and Redis in one container on Render |
| `scripts/screenshots.mjs` | Captures the four pages for the report |
| `sync-from-course.sh` | Copies the app from the course container's `data/word-count-app` |

## The five TODOs (`word-count-app/server.js`)

| TODO | Code | What it does |
|---|---|---|
| 1 | `client.del(redisKey)` then `client.hSet(redisKey, wordCounts)` | Deletes the book's old hash, then writes every word and its count in one command |
| 2 | `client.keys('book:*:word_counts')` | Lists the key of every book stored in Redis |
| 3 | `client.hGetAll(redisKey)` | Reads every word and count of one book for the top-N lists |
| 4 | `client.hKeys(redisKey1)`, `client.hKeys(redisKey2)` in `Promise.all` | Reads only the words of both books, at the same time, to compare them |
| 5 | `client.hGetAll(redisKey)` | Reads every word and count of one book for the chart |

## Run

In the course container:

    docker exec cse6332-course sh /data/word-count-app/fetch_books.sh
    docker exec -it -w /data/word-count-app cse6332-course node server.js

then open <http://127.0.0.1:9002/word-chart-app/>.

Standalone, with its own Redis:

    docker compose up -d --build

then open <http://127.0.0.1:8085/word-chart-app/>.

Check Redis:

    docker exec -it cse6332-course redis-cli
    KEYS book:*
    HGET book:Pride_and_Prejudice:word_counts elizabeth      # 645
