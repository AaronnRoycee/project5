# Project 5 demo (Wed 11/18, Teams)

## Before the call
    docker ps --format '{{.Names}} {{.Status}}'                       # cse6332-course Up
    docker exec cse6332-course pkill -f "node server.js"              # nothing left on port 9002
Open https://cse6332-project5.onrender.com/word-chart-app/ a minute early (free tier wakes slowly).

## 1. Start the app (Terminal 1)
    docker exec -it -w /data/word-count-app cse6332-course node server.js
    # Server running at http://127.0.0.1:9002/word-chart-app/
    # Indexed book: Pride_and_Prejudice / Tarzan_of_the_Apes / War_and_Peace

## 2. The four pages (http://127.0.0.1:9002/word-chart-app/)
1. Landing page: three cards, nav bar.
2. Word Counts: pick a book, filter, move the Top N / Top M sliders (pie + bar).
3. Unique Word Comparison: Pride_and_Prejudice vs Tarzan_of_the_Apes, Compare Books.
4. Word Charts: War_and_Peace, 20, Literary, Generate Chart (natasha and pierre appear).

## 3. Redis (Terminal 2)
    docker exec -it cse6332-course redis-cli
    KEYS book:*
    HGET book:Pride_and_Prejudice:word_counts elizabeth     # "645"
    HGET book:War_and_Peace:word_counts natasha              # "1213"
    HLEN book:War_and_Peace:word_counts                      # 17581

## 4. The five TODOs, one sentence each
1. indexBooks: `del` removes the book's old hash so no stale words survive a restart, then `hSet` writes every word and its count into the hash in one command.
2. /api/books: `keys('book:*:word_counts')` finds every book stored in Redis; the route turns each key into a title.
3. /api/book/:title/top/:n: `hGetAll` reads all words and counts of one book, which the route filters, sorts and cuts to the top N.
4. /api/compare-words: `hKeys` reads only the words of both books at the same time (Promise.all), because comparing needs the words, not the counts.
5. /api/chart-data/:title/:n: `hGetAll` reads all words and counts of one book for the chart, the same as TODO 3.

## 5. Issues, if asked
- gutenberg.org returned 403 for every book; fetch_books.sh now falls back to the gutenberg.pglaf.org mirror.
- Accented letters split names ("Natásha" became "nat" + "sha"); accents are now stripped before counting.
- Redis saves to disk, so TODO 1's delete matters: it removed the old "sha" fragments after the fix.
