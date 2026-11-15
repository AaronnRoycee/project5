#!/bin/sh
# Download the three books from Project Gutenberg into books/ (run inside the container):
#   docker exec cse6332-course sh /data/word-count-app/fetch_books.sh
# The file name (without .txt) is the title the pages show.
# If www.gutenberg.org refuses the download, the same file is fetched from gutenberg.pglaf.org,
# the mirror run by the Project Gutenberg Literary Archive Foundation.
cd "$(dirname "$0")" && mkdir -p books
get() {
  for host in www.gutenberg.org gutenberg.pglaf.org; do
    curl -fsSL -o "books/$2.txt" "https://$host/cache/epub/$1/pg$1.txt" && echo "books/$2.txt (from $host)" && return 0
  done
  echo "could not download $2" >&2; return 1
}
get 1342 Pride_and_Prejudice
get 2600 War_and_Peace
get 78   Tarzan_of_the_Apes
